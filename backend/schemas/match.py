"""
Match Schemas
=============

Pydantic schemas for match score API operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SkillMatch(BaseModel):
    """Schema for skill matching details."""
    skill: str
    matched: bool
    importance: Optional[float] = None


class MatchScoreBreakdown(BaseModel):
    """Schema for detailed match score breakdown."""
    overall_score: float = Field(..., ge=0, le=100, description="Overall match percentage")
    skill_score: float = Field(..., ge=0, le=100, description="Skill match percentage")
    experience_score: float = Field(..., ge=0, le=100, description="Experience match percentage")
    education_score: float = Field(..., ge=0, le=100, description="Education match percentage")
    semantic_score: float = Field(..., ge=0, le=100, description="Semantic similarity percentage")


class MatchCreate(BaseModel):
    """Schema for creating a match calculation request."""
    resume_id: int
    job_id: int


class MatchResponse(BaseModel):
    """Schema for match response."""
    id: int
    resume_id: int
    job_id: int
    overall_score: float
    skill_score: Optional[float] = None
    experience_score: Optional[float] = None
    education_score: Optional[float] = None
    semantic_score: Optional[float] = None
    skill_overlap: Optional[List[str]] = None
    skill_gaps: Optional[List[str]] = None
    explanation: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchDetailResponse(MatchResponse):
    """Schema for detailed match response with job info."""
    job_title: Optional[str] = None
    job_company: Optional[str] = None
    feature_importance: Optional[Dict[str, float]] = None
    
    class Config:
        from_attributes = True


class MatchListResponse(BaseModel):
    """Schema for list of matches for a resume."""
    resume_id: int
    matches: List[MatchDetailResponse]
    total: int


class MatchExplanation(BaseModel):
    """Schema for match explainability."""
    overall_summary: str
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    feature_contributions: Dict[str, float]
