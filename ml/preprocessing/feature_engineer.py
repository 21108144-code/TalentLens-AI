"""
Feature Engineer Module
=======================

Feature engineering utilities for ML pipeline.
"""

import re
from typing import Dict, List, Any, Optional
import numpy as np

from ml.preprocessing.text_cleaner import TextCleaner


class FeatureEngineer:
    """
    Feature engineering for resume-job matching ML models.
    """
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
    
    def extract_features(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Extract features for resume-job pair.
        
        Args:
            resume_data: Resume information
            job_data: Job information
            
        Returns:
            Dictionary of feature values
        """
        features = {}
        
        # Skill features
        skill_features = self._extract_skill_features(
            resume_data.get("skills", []),
            job_data.get("skills_required", [])
        )
        features.update(skill_features)
        
        # Experience features
        exp_features = self._extract_experience_features(
            resume_data.get("experience_years", 0),
            job_data.get("experience_required", 0)
        )
        features.update(exp_features)
        
        # Text features
        text_features = self._extract_text_features(
            resume_data.get("raw_text", ""),
            job_data.get("description", "")
        )
        features.update(text_features)
        
        # Education features
        edu_features = self._extract_education_features(
            resume_data.get("education", []),
            job_data.get("education_required", "")
        )
        features.update(edu_features)
        
        return features
    
    def _extract_skill_features(
        self,
        resume_skills: List[str],
        job_skills: List[str]
    ) -> Dict[str, float]:
        """Extract skill-based features."""
        resume_skills_lower = set(s.lower() for s in resume_skills)
        job_skills_lower = set(s.lower() for s in job_skills)
        
        if not job_skills_lower:
            return {
                "skill_overlap_ratio": 1.0,
                "skill_overlap_count": len(resume_skills_lower),
                "skill_gap_count": 0,
                "extra_skills_count": len(resume_skills_lower)
            }
        
        overlap = resume_skills_lower.intersection(job_skills_lower)
        gaps = job_skills_lower - resume_skills_lower
        extras = resume_skills_lower - job_skills_lower
        
        return {
            "skill_overlap_ratio": len(overlap) / len(job_skills_lower),
            "skill_overlap_count": len(overlap),
            "skill_gap_count": len(gaps),
            "extra_skills_count": len(extras)
        }
    
    def _extract_experience_features(
        self,
        resume_exp: int,
        job_exp: int
    ) -> Dict[str, float]:
        """Extract experience-based features."""
        if job_exp == 0:
            exp_ratio = 1.0
            exp_diff = resume_exp
        else:
            exp_ratio = min(1.0, resume_exp / job_exp)
            exp_diff = resume_exp - job_exp
        
        return {
            "experience_ratio": exp_ratio,
            "experience_diff": exp_diff,
            "experience_meets_req": 1.0 if resume_exp >= job_exp else 0.0,
            "experience_exceeds": 1.0 if resume_exp > job_exp else 0.0
        }
    
    def _extract_text_features(
        self,
        resume_text: str,
        job_text: str
    ) -> Dict[str, float]:
        """Extract text-based features."""
        # Clean texts
        resume_clean = self.text_cleaner.clean_text(resume_text)
        job_clean = self.text_cleaner.clean_text(job_text)
        
        # Token overlap
        resume_tokens = set(resume_clean.split())
        job_tokens = set(job_clean.split())
        
        if not job_tokens:
            jaccard = 0.5
        else:
            intersection = resume_tokens.intersection(job_tokens)
            union = resume_tokens.union(job_tokens)
            jaccard = len(intersection) / len(union) if union else 0
        
        return {
            "text_jaccard_similarity": jaccard,
            "resume_length": len(resume_text.split()),
            "job_length": len(job_text.split()),
            "common_tokens_count": len(resume_tokens.intersection(job_tokens))
        }
    
    def _extract_education_features(
        self,
        resume_education: List[Dict],
        job_education: str
    ) -> Dict[str, float]:
        """Extract education-based features."""
        # Education level mapping
        edu_levels = {
            "high school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5,
            "doctorate": 5
        }
        
        # Get required level
        required_level = 0
        job_edu_lower = job_education.lower()
        for key, level in edu_levels.items():
            if key in job_edu_lower:
                required_level = level
                break
        
        # Get candidate's highest level
        candidate_level = 0
        for edu in resume_education:
            degree = str(edu.get("degree", "")).lower()
            for key, level in edu_levels.items():
                if key in degree:
                    candidate_level = max(candidate_level, level)
        
        if required_level == 0:
            edu_ratio = 1.0
            meets_req = 1.0
        else:
            edu_ratio = min(1.0, candidate_level / required_level) if required_level > 0 else 1.0
            meets_req = 1.0 if candidate_level >= required_level else 0.0
        
        return {
            "education_level_ratio": edu_ratio,
            "education_meets_req": meets_req,
            "candidate_education_level": candidate_level,
            "required_education_level": required_level
        }
    
    def features_to_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dictionary to numpy array."""
        # Define consistent feature order
        feature_order = [
            "skill_overlap_ratio",
            "skill_overlap_count",
            "skill_gap_count",
            "extra_skills_count",
            "experience_ratio",
            "experience_diff",
            "experience_meets_req",
            "experience_exceeds",
            "text_jaccard_similarity",
            "resume_length",
            "job_length",
            "common_tokens_count",
            "education_level_ratio",
            "education_meets_req",
            "candidate_education_level",
            "required_education_level"
        ]
        
        return np.array([features.get(f, 0.0) for f in feature_order])
    
    @property
    def feature_names(self) -> List[str]:
        """Get ordered list of feature names."""
        return [
            "skill_overlap_ratio",
            "skill_overlap_count",
            "skill_gap_count",
            "extra_skills_count",
            "experience_ratio",
            "experience_diff",
            "experience_meets_req",
            "experience_exceeds",
            "text_jaccard_similarity",
            "resume_length",
            "job_length",
            "common_tokens_count",
            "education_level_ratio",
            "education_meets_req",
            "candidate_education_level",
            "required_education_level"
        ]
