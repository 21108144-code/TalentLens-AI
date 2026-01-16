"""
Job Scraper Service
====================

Scrapes jobs from free, legal sources:
- RemoteOK (remote tech jobs)
- Rozee.pk (Pakistan jobs)
- Indeed RSS (various jobs)
- We Work Remotely (remote jobs)
- Arbeitnow (international jobs)
- HackerNews Jobs (tech jobs)
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from loguru import logger

import requests
import feedparser
from bs4 import BeautifulSoup


class JobScraperService:
    """Scrapes jobs from multiple free sources."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'TalentLens AI Job Aggregator (Educational Project)',
            'Accept': 'application/json, text/html',
        }
        self.scraped_urls: Set[str] = set()  # Track already scraped jobs
    
    async def scrape_all_sources(self, 
                                  keywords: List[str] = None,
                                  location: str = "Islamabad",
                                  include_remote: bool = True,
                                  days_old: int = 3) -> List[Dict]:
        """
        Scrape jobs from all sources.
        
        Args:
            keywords: Skills/keywords to search for
            location: Target location (default: Islamabad)
            include_remote: Include remote jobs
            days_old: Max age of jobs in days
            
        Returns:
            List of job dictionaries
        """
        all_jobs = []
        
        # Default keywords for AI/ML/Software roles
        if not keywords:
            keywords = ["python", "machine learning", "ai", "software engineer", 
                       "full stack", "backend", "data science", "react"]
        
        logger.info(f"Starting job scrape for keywords: {keywords}")
        
        # Scrape each source
        try:
            remoteok_jobs = await self._scrape_remoteok(keywords)
            all_jobs.extend(remoteok_jobs)
            logger.info(f"RemoteOK: Found {len(remoteok_jobs)} jobs")
        except Exception as e:
            logger.error(f"RemoteOK scrape failed: {e}")
        
        try:
            wwr_jobs = await self._scrape_weworkremotely(keywords)
            all_jobs.extend(wwr_jobs)
            logger.info(f"WeWorkRemotely: Found {len(wwr_jobs)} jobs")
        except Exception as e:
            logger.error(f"WeWorkRemotely scrape failed: {e}")
        
        try:
            arbeitnow_jobs = await self._scrape_arbeitnow(keywords)
            all_jobs.extend(arbeitnow_jobs)
            logger.info(f"Arbeitnow: Found {len(arbeitnow_jobs)} jobs")
        except Exception as e:
            logger.error(f"Arbeitnow scrape failed: {e}")
        
        try:
            hn_jobs = await self._scrape_hackernews_jobs(keywords)
            all_jobs.extend(hn_jobs)
            logger.info(f"HackerNews: Found {len(hn_jobs)} jobs")
        except Exception as e:
            logger.error(f"HackerNews scrape failed: {e}")
        
        try:
            github_jobs = await self._scrape_github_jobs_alt(keywords)
            all_jobs.extend(github_jobs)
            logger.info(f"GitHub Jobs Alt: Found {len(github_jobs)} jobs")
        except Exception as e:
            logger.error(f"GitHub Jobs Alt scrape failed: {e}")
        
        # Filter by recency
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        recent_jobs = []
        for job in all_jobs:
            job_date = job.get('posted_date')
            if job_date:
                try:
                    if isinstance(job_date, str):
                        # Try to parse the date string
                        parsed_date = datetime.fromisoformat(job_date.replace('Z', '+00:00'))
                        # Make naive for comparison
                        if parsed_date.tzinfo is not None:
                            job_date = parsed_date.replace(tzinfo=None)
                        else:
                            job_date = parsed_date
                    if isinstance(job_date, datetime) and job_date >= cutoff_date:
                        recent_jobs.append(job)
                except Exception:
                    # If date parsing fails, include the job (assume recent)
                    recent_jobs.append(job)
            else:
                recent_jobs.append(job)  # Include if no date (assume recent)
        
        logger.info(f"Total jobs found: {len(all_jobs)}, Recent ({days_old} days): {len(recent_jobs)}")
        
        return recent_jobs
    
    async def _scrape_remoteok(self, keywords: List[str]) -> List[Dict]:
        """Scrape RemoteOK API (free, no auth required)."""
        jobs = []
        
        try:
            # RemoteOK has a public JSON API
            url = "https://remoteok.com/api"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # First item is metadata, skip it
            for item in data[1:]:
                title = item.get('position', '')
                company = item.get('company', '')
                description = item.get('description', '')
                tags = item.get('tags', [])
                apply_url = item.get('url', '')
                location = item.get('location', 'Remote')
                salary_min = item.get('salary_min')
                salary_max = item.get('salary_max')
                posted_date = item.get('date')
                
                # Check if matches any keyword
                text_to_search = f"{title} {description} {' '.join(tags)}".lower()
                if any(kw.lower() in text_to_search for kw in keywords):
                    jobs.append({
                        'title': title,
                        'company': company,
                        'description': description[:500] if description else '',
                        'location': location or 'Remote',
                        'remote_option': 'Remote',
                        'job_type': 'Full-time',
                        'skills_required': tags[:10] if tags else [],
                        'salary_min': salary_min,
                        'salary_max': salary_max,
                        'apply_url': apply_url,
                        'posted_date': posted_date,
                        'source': 'RemoteOK'
                    })
        except Exception as e:
            logger.error(f"RemoteOK error: {e}")
        
        return jobs[:20]  # Limit to 20 jobs per source
    
    async def _scrape_weworkremotely(self, keywords: List[str]) -> List[Dict]:
        """Scrape We Work Remotely RSS feeds."""
        jobs = []
        
        # WWR has category-based RSS feeds
        feeds = [
            "https://weworkremotely.com/categories/remote-programming-jobs.rss",
            "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
            "https://weworkremotely.com/categories/remote-data-jobs.rss",
        ]
        
        for feed_url in feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:
                    title = entry.get('title', '')
                    company = entry.get('author', 'Unknown')
                    description = entry.get('summary', '')
                    link = entry.get('link', '')
                    published = entry.get('published', '')
                    
                    # Parse description to extract company if in title
                    if ':' in title:
                        parts = title.split(':', 1)
                        company = parts[0].strip()
                        title = parts[1].strip()
                    
                    # Check keyword match
                    text_to_search = f"{title} {description}".lower()
                    if any(kw.lower() in text_to_search for kw in keywords):
                        jobs.append({
                            'title': title,
                            'company': company,
                            'description': BeautifulSoup(description, 'html.parser').get_text()[:500],
                            'location': 'Remote - Global',
                            'remote_option': 'Remote',
                            'job_type': 'Full-time',
                            'skills_required': [],
                            'apply_url': link,
                            'posted_date': published,
                            'source': 'WeWorkRemotely'
                        })
            except Exception as e:
                logger.error(f"WWR feed error: {e}")
        
        return jobs[:15]
    
    async def _scrape_arbeitnow(self, keywords: List[str]) -> List[Dict]:
        """Scrape Arbeitnow API (free, international jobs)."""
        jobs = []
        
        try:
            # Arbeitnow has a free API
            url = "https://www.arbeitnow.com/api/job-board-api"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('data', []):
                title = item.get('title', '')
                company = item.get('company_name', '')
                description = item.get('description', '')
                location = item.get('location', '')
                remote = item.get('remote', False)
                apply_url = item.get('url', '')
                tags = item.get('tags', [])
                created_at = item.get('created_at')
                
                # Check if matches keywords or is remote
                text_to_search = f"{title} {description} {' '.join(tags)}".lower()
                if any(kw.lower() in text_to_search for kw in keywords):
                    jobs.append({
                        'title': title,
                        'company': company,
                        'description': BeautifulSoup(description, 'html.parser').get_text()[:500] if description else '',
                        'location': location or ('Remote' if remote else 'Unknown'),
                        'remote_option': 'Remote' if remote else 'On-site',
                        'job_type': 'Full-time',
                        'skills_required': tags[:10] if tags else [],
                        'apply_url': apply_url,
                        'posted_date': created_at,
                        'source': 'Arbeitnow'
                    })
        except Exception as e:
            logger.error(f"Arbeitnow error: {e}")
        
        return jobs[:15]
    
    async def _scrape_hackernews_jobs(self, keywords: List[str]) -> List[Dict]:
        """Scrape HackerNews monthly Who's Hiring thread."""
        jobs = []
        
        try:
            # Get the latest "Who is hiring?" thread from HN
            # Using Algolia HN Search API (free)
            search_url = "https://hn.algolia.com/api/v1/search_by_date"
            params = {
                'query': 'Ask HN: Who is hiring?',
                'tags': 'story',
                'numericFilters': 'created_at_i>%d' % (datetime.utcnow().timestamp() - 30*24*3600)
            }
            
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            hits = data.get('hits', [])
            
            if hits:
                # Get the thread ID
                thread_id = hits[0].get('objectID')
                
                # Get comments (job postings)
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{thread_id}.json"
                item_response = requests.get(item_url, timeout=30)
                item_data = item_response.json()
                
                kids = item_data.get('kids', [])[:50]  # First 50 comments
                
                for kid_id in kids:
                    try:
                        comment_url = f"https://hacker-news.firebaseio.com/v0/item/{kid_id}.json"
                        comment_response = requests.get(comment_url, timeout=10)
                        comment = comment_response.json()
                        
                        text = comment.get('text', '')
                        if not text:
                            continue
                        
                        # Parse the comment to extract job info
                        text_clean = BeautifulSoup(text, 'html.parser').get_text()
                        
                        # Check keyword match
                        if any(kw.lower() in text_clean.lower() for kw in keywords):
                            # Try to extract company and title from first line
                            lines = text_clean.split('\n')
                            first_line = lines[0] if lines else ''
                            
                            # Common format: "Company | Title | Location | Remote/Onsite"
                            parts = first_line.split('|')
                            
                            company = parts[0].strip() if len(parts) > 0 else 'Unknown'
                            title = parts[1].strip() if len(parts) > 1 else 'Software Engineer'
                            location = parts[2].strip() if len(parts) > 2 else 'Unknown'
                            
                            is_remote = 'remote' in text_clean.lower()
                            
                            jobs.append({
                                'title': title[:100],
                                'company': company[:100],
                                'description': text_clean[:500],
                                'location': location if not is_remote else 'Remote',
                                'remote_option': 'Remote' if is_remote else 'On-site',
                                'job_type': 'Full-time',
                                'skills_required': [],
                                'apply_url': f"https://news.ycombinator.com/item?id={kid_id}",
                                'posted_date': datetime.fromtimestamp(comment.get('time', datetime.utcnow().timestamp())).isoformat(),
                                'source': 'HackerNews'
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing HN comment: {e}")
        except Exception as e:
            logger.error(f"HackerNews error: {e}")
        
        return jobs[:10]
    
    async def _scrape_github_jobs_alt(self, keywords: List[str]) -> List[Dict]:
        """
        Scrape job listings from GitHub repositories that aggregate jobs.
        Uses free sources like awesome-remote-job.
        """
        jobs = []
        
        try:
            # Use the RemoteHub API (free)
            url = "https://remotive.com/api/remote-jobs"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('jobs', []):
                title = item.get('title', '')
                company = item.get('company_name', '')
                description = item.get('description', '')
                category = item.get('category', '')
                url = item.get('url', '')
                publication_date = item.get('publication_date', '')
                salary = item.get('salary', '')
                
                # Check keyword match
                text_to_search = f"{title} {description} {category}".lower()
                if any(kw.lower() in text_to_search for kw in keywords):
                    jobs.append({
                        'title': title,
                        'company': company,
                        'description': BeautifulSoup(description, 'html.parser').get_text()[:500] if description else '',
                        'location': 'Remote - Global',
                        'remote_option': 'Remote',
                        'job_type': 'Full-time',
                        'skills_required': [category] if category else [],
                        'apply_url': url,
                        'posted_date': publication_date,
                        'source': 'Remotive'
                    })
        except Exception as e:
            logger.error(f"Remotive error: {e}")
        
        return jobs[:15]
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description."""
        skills_keywords = [
            'python', 'javascript', 'typescript', 'react', 'node.js', 'nodejs',
            'java', 'c++', 'c#', 'go', 'golang', 'rust', 'ruby', 'php',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'machine learning', 'deep learning', 'ai', 'nlp', 'pytorch', 'tensorflow',
            'react native', 'flutter', 'swift', 'kotlin', 'android', 'ios',
            'git', 'agile', 'scrum', 'devops', 'ci/cd', 'jenkins',
            'fastapi', 'django', 'flask', 'express', 'spring', 'rails'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills[:10]  # Return top 10 skills
