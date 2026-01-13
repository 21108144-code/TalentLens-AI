"""
Job Model
=========

SQLAlchemy model for job listings.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, LargeBinary, Float

from database.connection import Base


class Job(Base):
    """
    Job listing model.
    
    Attributes:
        id: Primary key
        title: Job title
        company: Company name
        description: Full job description
        requirements: Job requirements (JSON)
        skills_required: Required skills list (JSON)
        location: Job location
        job_type: Full-time, Part-time, Contract, etc.
        salary_min: Minimum salary
        salary_max: Maximum salary
        experience_required: Required years of experience
        education_required: Required education level
        embedding: Vector embedding (binary)
        is_active: Whether job is still open
        created_at: Posting timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Requirements
    requirements = Column(Text, nullable=True)  # Full requirements text
    skills_required = Column(JSON, nullable=True)  # List of required skills
    experience_required = Column(Integer, nullable=True)  # Years
    education_required = Column(String(100), nullable=True)
    
    # Job details
    location = Column(String(255), nullable=True)
    job_type = Column(String(50), nullable=True)  # Full-time, Part-time, etc.
    remote_option = Column(String(50), nullable=True)  # Remote, Hybrid, On-site
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), default="USD")
    
    # ML features
    embedding = Column(LargeBinary, nullable=True)  # Vector embedding
    
    # Status
    is_active = Column(Integer, default=1)  # 1 = active, 0 = closed
    
    # Metadata
    source = Column(String(100), nullable=True)  # Where the job was sourced from
    external_id = Column(String(100), nullable=True)  # ID from source
    apply_url = Column(String(500), nullable=True)  # Direct link to apply
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, company={self.company})>"
