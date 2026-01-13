"""
Job Schemas
===========

Pydantic schemas for job-related API operations.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """Base job schema with common fields."""
    title: str
    company: str
    description: str


class JobCreate(JobBase):
    """Schema for creating a new job listing."""
    requirements: Optional[str] = None
    skills_required: Optional[List[str]] = None
    experience_required: Optional[int] = None
    education_required: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = Field(None, description="Full-time, Part-time, Contract, etc.")
    remote_option: Optional[str] = Field(None, description="Remote, Hybrid, On-site")
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"


class JobUpdate(BaseModel):
    """Schema for updating a job listing."""
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    skills_required: Optional[List[str]] = None
    location: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    is_active: Optional[int] = None


class JobResponse(JobBase):
    """Schema for job response."""
    id: int
    requirements: Optional[str] = None
    skills_required: Optional[List[str]] = None
    experience_required: Optional[int] = None
    education_required: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    remote_option: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for paginated job list."""
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class JobSearchParams(BaseModel):
    """Schema for job search parameters."""
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    remote_option: Optional[str] = None
    min_salary: Optional[float] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[int] = None
    page: int = 1
    per_page: int = 20
