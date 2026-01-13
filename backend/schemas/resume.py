"""
Resume Schemas
==============

Pydantic schemas for resume-related API operations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SkillInfo(BaseModel):
    """Schema for extracted skill information."""
    name: str
    category: Optional[str] = None
    confidence: Optional[float] = None


class WorkExperience(BaseModel):
    """Schema for work experience entry."""
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    duration_months: Optional[int] = None


class Education(BaseModel):
    """Schema for education entry."""
    degree: str
    institution: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class ResumeBase(BaseModel):
    """Base resume schema."""
    filename: str


class ResumeCreate(BaseModel):
    """Schema for resume creation (file upload)."""
    # File is handled separately via Form data
    pass


class ResumeUpdate(BaseModel):
    """Schema for updating resume metadata."""
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None


class ResumeAnalysis(BaseModel):
    """Schema for resume analysis results."""
    skills: List[SkillInfo] = []
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    experience_years: Optional[int] = None
    summary: Optional[str] = None


class ResumeResponse(ResumeBase):
    """Schema for resume response."""
    id: int
    user_id: int
    content_type: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResumeDetailResponse(ResumeResponse):
    """Schema for detailed resume response with parsed data."""
    raw_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    work_history: Optional[List[Dict]] = None
    education: Optional[List[Dict]] = None
    
    class Config:
        from_attributes = True


class ResumeUploadResponse(BaseModel):
    """Schema for resume upload response."""
    id: int
    filename: str
    message: str
    skills_extracted: int
    analysis: Optional[ResumeAnalysis] = None
