"""
Job Monitor Task
=================

Scheduled task that:
1. Scrapes jobs from free sources
2. Matches them against user's resume
3. Sends notifications for high-match jobs
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from services.job_scraper import JobScraperService
from services.notification_service import NotificationService
from database.connection import async_session_maker
from models import Job, Resume, User
from sqlalchemy import select, and_


class JobMonitor:
    """
    Monitors job boards and notifies user of matching opportunities.
    """
    
    def __init__(self):
        self.scraper = JobScraperService()
        self.notifier = NotificationService()
        self.seen_jobs: set = set()  # Track seen job URLs to avoid duplicates
        self._load_seen_jobs()
    
    def _load_seen_jobs(self):
        """Load previously seen jobs from cache file."""
        cache_file = Path(__file__).parent.parent / "data" / "seen_jobs.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.seen_jobs = set(json.load(f))
                logger.info(f"Loaded {len(self.seen_jobs)} previously seen jobs")
            except Exception as e:
                logger.error(f"Error loading seen jobs: {e}")
    
    def _save_seen_jobs(self):
        """Save seen jobs to cache file."""
        cache_file = Path(__file__).parent.parent / "data" / "seen_jobs.json"
        cache_file.parent.mkdir(exist_ok=True)
        try:
            with open(cache_file, 'w') as f:
                json.dump(list(self.seen_jobs), f)
        except Exception as e:
            logger.error(f"Error saving seen jobs: {e}")
    
    async def get_user_skills(self, user_id: int = None) -> List[str]:
        """
        Get skills from user's resume.
        Returns combined skills from all user resumes or default skills.
        """
        skills = []
        
        try:
            async with async_session_maker() as session:
                if user_id:
                    query = select(Resume).where(Resume.user_id == user_id)
                else:
                    # Get all resumes if no user specified
                    query = select(Resume)
                
                result = await session.execute(query)
                resumes = result.scalars().all()
                
                for resume in resumes:
                    if resume.skills:
                        resume_skills = resume.skills
                        if isinstance(resume_skills, str):
                            resume_skills = json.loads(resume_skills)
                        skills.extend(resume_skills)
        except Exception as e:
            logger.error(f"Error getting user skills: {e}")
        
        # Default skills if none found
        if not skills:
            skills = [
                "python", "machine learning", "ai", "nlp", "deep learning",
                "fastapi", "react", "javascript", "sql", "docker",
                "pytorch", "tensorflow", "data science"
            ]
            logger.info("Using default skills for job matching")
        
        # Remove duplicates and return
        unique_skills = list(set(s.lower() for s in skills))
        logger.info(f"Matching against skills: {unique_skills[:10]}...")
        return unique_skills
    
    def calculate_match_score(self, job: Dict, user_skills: List[str]) -> int:
        """
        Calculate how well a job matches user's skills.
        
        Returns:
            Match score 0-100
        """
        job_skills = job.get('skills_required', [])
        job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
        
        if not job_skills:
            # Extract skills from description
            job_skills = self.scraper.extract_skills_from_text(job_text)
        
        # Start with base score for remote jobs (these are all remote-focused sources)
        location = job.get('location', '').lower()
        remote_option = job.get('remote_option', '').lower()
        
        base_score = 30  # Base score
        
        # Remote bonus
        if 'remote' in location or 'remote' in remote_option:
            base_score += 20
        
        # Islamabad/Pakistan bonus
        if 'islamabad' in location or 'pakistan' in location:
            base_score += 25
        
        # Count matching skills
        matches = 0
        for skill in user_skills:
            skill_lower = skill.lower()
            if skill_lower in job_text or skill_lower in [s.lower() for s in job_skills]:
                matches += 1
        
        # Each skill match adds points
        skill_score = min(50, matches * 10)  # Up to 50 points from skills
        
        total_score = min(100, base_score + skill_score)
        
        return total_score
    
    async def run_monitor(self, 
                           min_match_score: int = 40,
                           notify_desktop: bool = True,
                           notify_email: bool = True) -> Dict:
        """
        Run the job monitor.
        
        Args:
            min_match_score: Minimum match score to notify (0-100)
            notify_desktop: Send desktop notifications
            notify_email: Send email notifications
            
        Returns:
            Summary of the run
        """
        logger.info("=" * 50)
        logger.info("Starting Job Monitor Run")
        logger.info("=" * 50)
        
        start_time = datetime.utcnow()
        
        # Get user skills from resume
        user_skills = await self.get_user_skills()
        
        # Scrape jobs from all sources
        all_jobs = await self.scraper.scrape_all_sources(
            keywords=user_skills[:10],  # Use top 10 skills as keywords
            include_remote=True,
            days_old=3
        )
        
        logger.info(f"Scraped {len(all_jobs)} total jobs")
        
        # Filter to new jobs only
        new_jobs = []
        for job in all_jobs:
            job_url = job.get('apply_url', '')
            job_key = f"{job.get('title', '')}|{job.get('company', '')}|{job_url}"
            
            if job_key not in self.seen_jobs:
                new_jobs.append(job)
                self.seen_jobs.add(job_key)
        
        logger.info(f"Found {len(new_jobs)} new jobs")
        
        # Score jobs against user skills
        matching_jobs = []
        for job in new_jobs:
            score = self.calculate_match_score(job, user_skills)
            job['match_score'] = score
            
            if score >= min_match_score:
                matching_jobs.append(job)
        
        # Sort by match score
        matching_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        logger.info(f"Found {len(matching_jobs)} jobs matching criteria (score >= {min_match_score})")
        
        # Store new jobs in database
        stored_count = await self._store_jobs_in_db(matching_jobs)
        
        # Send notifications
        notification_result = {'desktop_sent': False, 'email_sent': False}
        if matching_jobs:
            notification_result = self.notifier.send_job_alert(
                matching_jobs[:10],  # Top 10 matches
                via_desktop=notify_desktop,
                via_email=notify_email
            )
        
        # Save seen jobs cache
        self._save_seen_jobs()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            'timestamp': start_time.isoformat(),
            'duration_seconds': duration,
            'total_scraped': len(all_jobs),
            'new_jobs': len(new_jobs),
            'matching_jobs': len(matching_jobs),
            'stored_in_db': stored_count,
            'notifications': notification_result,
            'top_matches': [
                {
                    'title': j.get('title'),
                    'company': j.get('company'),
                    'score': j.get('match_score'),
                    'source': j.get('source')
                }
                for j in matching_jobs[:5]
            ]
        }
        
        logger.info(f"Monitor run complete in {duration:.1f}s")
        logger.info(f"Summary: {json.dumps(summary, indent=2)}")
        
        return summary
    
    async def _store_jobs_in_db(self, jobs: List[Dict]) -> int:
        """Store scraped jobs in the database."""
        stored = 0
        
        try:
            async with async_session_maker() as session:
                for job_data in jobs:
                    # Check if job already exists
                    existing = await session.execute(
                        select(Job).where(
                            and_(
                                Job.title == job_data.get('title'),
                                Job.company == job_data.get('company'),
                                Job.apply_url == job_data.get('apply_url')
                            )
                        )
                    )
                    
                    if existing.scalar_one_or_none() is None:
                        job = Job(
                            title=job_data.get('title', 'Unknown')[:255],
                            company=job_data.get('company', 'Unknown')[:255],
                            description=job_data.get('description', '')[:5000],
                            location=job_data.get('location', '')[:255],
                            remote_option=job_data.get('remote_option', '')[:50],
                            job_type=job_data.get('job_type', 'Full-time')[:50],
                            skills_required=job_data.get('skills_required', []),
                            salary_min=job_data.get('salary_min'),
                            salary_max=job_data.get('salary_max'),
                            apply_url=job_data.get('apply_url', '')[:500],
                            source=job_data.get('source', '')[:100],
                            is_active=1
                        )
                        session.add(job)
                        stored += 1
                
                await session.commit()
        except Exception as e:
            logger.error(f"Error storing jobs: {e}")
        
        logger.info(f"Stored {stored} new jobs in database")
        return stored


async def main():
    """Run the job monitor once."""
    monitor = JobMonitor()
    result = await monitor.run_monitor(
        min_match_score=40,
        notify_desktop=True,
        notify_email=True
    )
    return result


if __name__ == "__main__":
    asyncio.run(main())
