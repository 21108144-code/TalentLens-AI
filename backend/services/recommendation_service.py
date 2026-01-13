"""
Recommendation Service
======================

Service for generating personalized job recommendations using hybrid approach.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger

from services.embedding_service import EmbeddingService
from services.matching_service import MatchingService
from schemas import RecommendedJob


class RecommendationService:
    """
    Hybrid recommendation engine combining:
    - Content-based filtering (skill matching)
    - Semantic similarity (embedding-based)
    - Skill gap analysis
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.matching_service = MatchingService()
    
    async def generate(
        self,
        resume,
        jobs: List,
        filters: Optional[Dict] = None,
        limit: int = 5
    ) -> List[RecommendedJob]:
        """
        Generate personalized job recommendations.
        
        Args:
            resume: Resume model instance
            jobs: List of job instances
            filters: Optional filters (location, job_type, etc.)
            limit: Maximum recommendations to return
            
        Returns:
            List of recommended jobs with explanations
        """
        if not jobs:
            return []
        
        # Apply filters
        filtered_jobs = self._apply_filters(jobs, filters)
        
        if not filtered_jobs:
            return []
        
        # Score all jobs
        scored_jobs = []
        
        for job in filtered_jobs:
            try:
                match_result = await self.matching_service.calculate_match(resume, job)
                
                scored_jobs.append({
                    "job": job,
                    "score": match_result["overall_score"],
                    "skill_overlap": match_result["skill_overlap"],
                    "skill_gaps": match_result["skill_gaps"],
                    "explanation": match_result["explanation"]
                })
            except Exception as e:
                logger.warning(f"Error scoring job {job.id}: {e}")
                continue
        
        # Sort by score
        scored_jobs.sort(key=lambda x: x["score"], reverse=True)
        
        # Take top N
        top_jobs = scored_jobs[:limit]
        
        # Convert to response schema
        recommendations = []
        for rank, item in enumerate(top_jobs, 1):
            job = item["job"]
            
            # Generate match highlights
            highlights = self._generate_highlights(item)
            
            # Format salary range
            salary_range = None
            if job.salary_min and job.salary_max:
                salary_range = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}"
            
            recommendations.append(RecommendedJob(
                job_id=job.id,
                rank=rank,
                score=round(item["score"], 2),
                title=job.title,
                company=job.company,
                location=job.location,
                salary_range=salary_range,
                explanation=self._generate_recommendation_explanation(item, rank),
                skill_overlap=item["skill_overlap"][:5],  # Top 5
                skill_gaps=item["skill_gaps"][:5],  # Top 5
                match_highlights=highlights
            ))
        
        return recommendations
    
    def _apply_filters(self, jobs: List, filters: Optional[Dict]) -> List:
        """Apply user filters to job list."""
        if not filters:
            return jobs
        
        filtered = jobs
        
        # Location filter
        if filters.get("location"):
            loc = filters["location"].lower()
            filtered = [j for j in filtered if loc in (j.location or "").lower()]
        
        # Job type filter
        if filters.get("job_type"):
            jt = filters["job_type"].lower()
            filtered = [j for j in filtered if (j.job_type or "").lower() == jt]
        
        # Remote option filter
        if filters.get("remote_option"):
            ro = filters["remote_option"].lower()
            filtered = [j for j in filtered if (j.remote_option or "").lower() == ro]
        
        # Salary filter
        if filters.get("min_salary"):
            min_sal = filters["min_salary"]
            filtered = [j for j in filtered if (j.salary_min or 0) >= min_sal]
        
        if filters.get("max_salary"):
            max_sal = filters["max_salary"]
            filtered = [j for j in filtered if (j.salary_max or float('inf')) <= max_sal]
        
        return filtered
    
    def _generate_highlights(self, item: Dict) -> List[str]:
        """Generate match highlights for a job."""
        highlights = []
        
        score = item["score"]
        skill_overlap = item["skill_overlap"]
        skill_gaps = item["skill_gaps"]
        
        # Score-based highlights
        if score >= 80:
            highlights.append("🎯 Excellent match for your profile")
        elif score >= 70:
            highlights.append("✨ Strong alignment with your skills")
        elif score >= 60:
            highlights.append("📈 Good growth opportunity")
        
        # Skill-based highlights
        if len(skill_overlap) >= 5:
            highlights.append(f"💪 {len(skill_overlap)} skills match required skills")
        elif len(skill_overlap) >= 3:
            highlights.append(f"✓ Core skills aligned")
        
        if len(skill_gaps) <= 2:
            highlights.append("📋 Minimal skill gaps")
        elif len(skill_gaps) <= 5:
            highlights.append("📚 Achievable skill development path")
        
        return highlights[:3]  # Max 3 highlights
    
    def _generate_recommendation_explanation(self, item: Dict, rank: int) -> str:
        """Generate explanation for why job is recommended."""
        score = item["score"]
        skill_overlap = item["skill_overlap"]
        skill_gaps = item["skill_gaps"]
        job = item["job"]
        
        parts = []
        
        # Rank-specific intro
        if rank == 1:
            parts.append(f"Top recommendation with {score:.0f}% match.")
        elif rank <= 3:
            parts.append(f"Highly recommended ({score:.0f}% match).")
        else:
            parts.append(f"Good fit ({score:.0f}% match).")
        
        # Skills explanation
        if skill_overlap:
            if len(skill_overlap) > 3:
                parts.append(f"Your {', '.join(skill_overlap[:3])} and {len(skill_overlap)-3} other skills align well.")
            else:
                parts.append(f"Your {', '.join(skill_overlap)} skills are relevant.")
        
        # Growth potential
        if skill_gaps:
            parts.append(f"Opportunity to develop: {', '.join(skill_gaps[:2])}.")
        
        return " ".join(parts)
    
    async def generate_skill_gap_analysis(
        self,
        resume,
        jobs: List
    ) -> Dict[str, Any]:
        """
        Analyze skill gaps across multiple jobs.
        
        Args:
            resume: Resume instance
            jobs: List of target jobs
            
        Returns:
            Skill gap analysis with recommendations
        """
        resume_skills = set(s.lower() for s in (resume.skills or []))
        
        # Aggregate required skills from all jobs
        all_required_skills = {}
        
        for job in jobs:
            job_skills = job.skills_required or []
            for skill in job_skills:
                skill_lower = skill.lower()
                if skill_lower not in all_required_skills:
                    all_required_skills[skill_lower] = 0
                all_required_skills[skill_lower] += 1
        
        # Find missing skills sorted by frequency
        missing_skills = {
            skill: count 
            for skill, count in all_required_skills.items() 
            if skill not in resume_skills
        }
        
        sorted_gaps = sorted(
            missing_skills.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Categorize gaps
        critical_gaps = [s for s, c in sorted_gaps if c >= len(jobs) * 0.7]
        important_gaps = [s for s, c in sorted_gaps if len(jobs) * 0.3 <= c < len(jobs) * 0.7]
        nice_to_have = [s for s, c in sorted_gaps if c < len(jobs) * 0.3]
        
        return {
            "total_jobs_analyzed": len(jobs),
            "current_skills": list(resume_skills),
            "critical_gaps": critical_gaps[:5],
            "important_gaps": important_gaps[:5],
            "nice_to_have": nice_to_have[:5],
            "overall_coverage": len(resume_skills.intersection(all_required_skills)) / len(all_required_skills) * 100 if all_required_skills else 100,
            "recommendation": self._generate_gap_recommendation(critical_gaps, important_gaps)
        }
    
    def _generate_gap_recommendation(
        self, 
        critical: List[str], 
        important: List[str]
    ) -> str:
        """Generate recommendation based on skill gaps."""
        if not critical and not important:
            return "Your skills align well with the job market. Keep building on your strengths!"
        
        if critical:
            return f"Focus on learning {', '.join(critical[:3])} to significantly improve your marketability."
        
        return f"Consider developing {', '.join(important[:3])} to enhance your profile."
