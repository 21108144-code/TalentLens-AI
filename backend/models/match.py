"""
Match Model
===========

SQLAlchemy model for resume-job match scores.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database.connection import Base


class Match(Base):
    """
    Resume-Job match score model.
    
    Attributes:
        id: Primary key
        resume_id: Foreign key to resume
        job_id: Foreign key to job
        overall_score: Overall match percentage (0-100)
        skill_score: Skill match score
        experience_score: Experience match score
        education_score: Education match score
        semantic_score: Semantic similarity score
        skill_overlap: Matching skills (JSON)
        skill_gaps: Missing skills (JSON)
        explanation: Human-readable explanation
        feature_importance: Feature importance values (JSON)
        created_at: Calculation timestamp
    """
    
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    
    # Scores (0-100)
    overall_score = Column(Float, nullable=False)
    skill_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    semantic_score = Column(Float, nullable=True)
    
    # Skill analysis
    skill_overlap = Column(JSON, nullable=True)  # Skills that match
    skill_gaps = Column(JSON, nullable=True)  # Missing required skills
    
    # Explainability
    explanation = Column(Text, nullable=True)  # Human-readable explanation
    feature_importance = Column(JSON, nullable=True)  # Which features contributed most
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    resume = relationship("Resume", back_populates="matches")
    
    def __repr__(self):
        return f"<Match(resume_id={self.resume_id}, job_id={self.job_id}, score={self.overall_score})>"
