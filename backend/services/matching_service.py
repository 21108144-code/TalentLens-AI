"""
Matching Service
================

Service for calculating resume-job match scores with explainability.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from loguru import logger

from services.embedding_service import EmbeddingService
from services.skill_extractor import SkillExtractorService


class MatchingService:
    """
    Service for calculating match scores between resumes and jobs.
    Provides explainable matching with feature importance.
    """
    
    # Weight configuration for scoring
    WEIGHTS = {
        "skill_score": 0.40,      # 40% weight for skill match
        "semantic_score": 0.30,   # 30% weight for semantic similarity
        "experience_score": 0.20, # 20% weight for experience match
        "education_score": 0.10   # 10% weight for education match
    }
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.skill_extractor = SkillExtractorService()
    
    async def calculate_match(
        self, 
        resume, 
        job
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive match score between resume and job.
        
        Args:
            resume: Resume model instance
            job: Job model instance
            
        Returns:
            Dictionary with scores and analysis
        """
        # Calculate individual scores
        skill_result = await self._calculate_skill_score(resume, job)
        semantic_score = await self._calculate_semantic_score(resume, job)
        experience_score = self._calculate_experience_score(resume, job)
        education_score = self._calculate_education_score(resume, job)
        
        # Calculate weighted overall score
        overall_score = (
            skill_result["score"] * self.WEIGHTS["skill_score"] +
            semantic_score * self.WEIGHTS["semantic_score"] +
            experience_score * self.WEIGHTS["experience_score"] +
            education_score * self.WEIGHTS["education_score"]
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            overall_score=overall_score,
            skill_overlap=skill_result["overlap"],
            skill_gaps=skill_result["gaps"],
            experience_match=experience_score > 70,
            education_match=education_score > 70
        )
        
        # Calculate feature importance
        feature_importance = {
            "skills": self.WEIGHTS["skill_score"] * (skill_result["score"] / 100),
            "semantic": self.WEIGHTS["semantic_score"] * (semantic_score / 100),
            "experience": self.WEIGHTS["experience_score"] * (experience_score / 100),
            "education": self.WEIGHTS["education_score"] * (education_score / 100)
        }
        
        return {
            "overall_score": round(overall_score, 2),
            "skill_score": round(skill_result["score"], 2),
            "experience_score": round(experience_score, 2),
            "education_score": round(education_score, 2),
            "semantic_score": round(semantic_score, 2),
            "skill_overlap": skill_result["overlap"],
            "skill_gaps": skill_result["gaps"],
            "explanation": explanation,
            "feature_importance": feature_importance
        }
    
    async def _calculate_skill_score(
        self, 
        resume, 
        job
    ) -> Dict[str, Any]:
        """Calculate skill match score."""
        resume_skills = set(s.lower() for s in (resume.skills or []))
        job_skills = set(s.lower() for s in (job.skills_required or []))
        
        if not job_skills:
            return {"score": 100.0, "overlap": list(resume_skills), "gaps": []}
        
        # Calculate overlap
        overlap = resume_skills.intersection(job_skills)
        gaps = job_skills - resume_skills
        
        # Score based on percentage of required skills matched
        score = (len(overlap) / len(job_skills)) * 100 if job_skills else 100
        
        return {
            "score": score,
            "overlap": list(overlap),
            "gaps": list(gaps)
        }
    
    async def _calculate_semantic_score(self, resume, job) -> float:
        """Calculate semantic similarity between resume and job description."""
        try:
            # Get embeddings
            resume_text = resume.raw_text or ""
            job_text = f"{job.title} {job.description} {job.requirements or ''}"
            
            if not resume_text or not job_text:
                return 50.0  # Neutral score if text unavailable
            
            resume_embedding = await self.embedding_service.embed_text(resume_text)
            job_embedding = await self.embedding_service.embed_text(job_text)
            
            # Calculate similarity
            similarity = self.embedding_service.compute_similarity(
                resume_embedding, 
                job_embedding
            )
            
            return similarity * 100
            
        except Exception as e:
            logger.error(f"Semantic score calculation failed: {e}")
            return 50.0
    
    def _calculate_experience_score(self, resume, job) -> float:
        """Calculate experience match score."""
        resume_exp = resume.experience_years or 0
        required_exp = job.experience_required or 0
        
        if required_exp == 0:
            return 100.0  # No requirement, full score
        
        if resume_exp >= required_exp:
            return 100.0  # Meets or exceeds requirement
        
        # Partial score based on how close they are
        ratio = resume_exp / required_exp
        return min(100.0, ratio * 100)
    
    def _calculate_education_score(self, resume, job) -> float:
        """Calculate education match score."""
        required_edu = (job.education_required or "").lower()
        
        if not required_edu:
            return 100.0  # No requirement
        
        resume_edu = resume.education or []
        
        # Education level mapping
        edu_levels = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5,
            "doctorate": 5
        }
        
        # Find required level
        required_level = 0
        for key, level in edu_levels.items():
            if key in required_edu:
                required_level = level
                break
        
        if required_level == 0:
            return 100.0
        
        # Find candidate's highest level
        candidate_level = 0
        for edu_entry in resume_edu:
            degree = str(edu_entry.get("degree", "")).lower()
            for key, level in edu_levels.items():
                if key in degree:
                    candidate_level = max(candidate_level, level)
        
        if candidate_level >= required_level:
            return 100.0
        
        # Partial score
        return (candidate_level / required_level) * 100 if required_level > 0 else 100.0
    
    def _generate_explanation(
        self,
        overall_score: float,
        skill_overlap: List[str],
        skill_gaps: List[str],
        experience_match: bool,
        education_match: bool
    ) -> str:
        """Generate human-readable explanation for the match."""
        parts = []
        
        # Overall assessment
        if overall_score >= 80:
            parts.append("Excellent match!")
        elif overall_score >= 60:
            parts.append("Good match with room for improvement.")
        elif overall_score >= 40:
            parts.append("Moderate match. Consider upskilling.")
        else:
            parts.append("Limited match. Significant gaps identified.")
        
        # Skills
        if skill_overlap:
            parts.append(f"Matching skills: {', '.join(skill_overlap[:5])}")
            if len(skill_overlap) > 5:
                parts.append(f"...and {len(skill_overlap) - 5} more.")
        
        if skill_gaps:
            parts.append(f"Skills to develop: {', '.join(skill_gaps[:5])}")
        
        # Experience
        if experience_match:
            parts.append("Experience level meets requirements.")
        else:
            parts.append("Additional experience may be beneficial.")
        
        # Education
        if education_match:
            parts.append("Education requirements satisfied.")
        
        return " ".join(parts)
    
    async def generate_explanation(self, match) -> Dict[str, Any]:
        """Generate detailed explanation for an existing match."""
        skill_overlap = match.skill_overlap or []
        skill_gaps = match.skill_gaps or []
        
        strengths = []
        gaps = []
        recommendations = []
        
        # Analyze strengths
        if match.skill_score >= 70:
            strengths.append(f"Strong skill alignment ({match.skill_score:.0f}%)")
        if match.experience_score >= 80:
            strengths.append("Experience level exceeds requirements")
        if match.semantic_score >= 70:
            strengths.append("Resume content strongly aligns with job description")
        if skill_overlap:
            strengths.append(f"Key matching skills: {', '.join(skill_overlap[:3])}")
        
        # Analyze gaps
        if match.skill_score < 70:
            gaps.append("Skill match could be improved")
        if skill_gaps:
            gaps.append(f"Missing required skills: {', '.join(skill_gaps[:3])}")
        if match.experience_score < 70:
            gaps.append("Experience level below requirements")
        
        # Generate recommendations
        if skill_gaps:
            recommendations.append(f"Consider learning: {', '.join(skill_gaps[:3])}")
        if match.semantic_score < 60:
            recommendations.append("Tailor resume language to match job description")
        if match.experience_score < 80:
            recommendations.append("Highlight relevant project experience")
        
        return {
            "overall_summary": match.explanation or "Match analysis complete.",
            "strengths": strengths if strengths else ["No major strengths identified"],
            "gaps": gaps if gaps else ["No significant gaps found"],
            "recommendations": recommendations if recommendations else ["Continue building relevant experience"],
            "feature_contributions": match.feature_importance or {}
        }
