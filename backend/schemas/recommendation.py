"""
Recommendation Schemas
======================

Pydantic schemas for recommendation API operations.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class RecommendedJob(BaseModel):
    """Schema for a single recommended job."""
    job_id: int
    rank: int
    score: float
    title: str
    company: str
    location: Optional[str] = None
    salary_range: Optional[str] = None
    explanation: str
    skill_overlap: List[str]
    skill_gaps: List[str]
    match_highlights: List[str]


class RecommendationRequest(BaseModel):
    """Schema for recommendation request."""
    resume_id: int
    filters: Optional[Dict] = None
    limit: int = 5


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""
    id: int
    user_id: int
    resume_id: int
    recommendations: List[RecommendedJob]
    total_jobs_analyzed: int
    algorithm_used: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecommendationFilters(BaseModel):
    """Schema for recommendation filtering options."""
    location: Optional[str] = None
    job_type: Optional[str] = None
    remote_option: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    skills_focus: Optional[List[str]] = None


class RecommendationExplanation(BaseModel):
    """Schema for detailed recommendation explanation."""
    job_id: int
    why_recommended: str
    key_matching_skills: List[str]
    growth_opportunities: List[str]
    salary_assessment: Optional[str] = None
    experience_fit: str
    overall_fit_summary: str
