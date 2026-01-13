"""
Recommendation Model
====================

SQLAlchemy model for personalized job recommendations.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship

from database.connection import Base


class Recommendation(Base):
    """
    Personalized job recommendations model.
    
    Stores a set of recommended jobs for a user based on their resume.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        resume_id: Foreign key to resume used
        job_recommendations: List of recommended job IDs with scores (JSON)
        explanations: Explanations for each recommendation (JSON)
        filters_applied: Any filters used (JSON)
        created_at: Generation timestamp
    """
    
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, index=True)
    
    # Recommendations
    job_recommendations = Column(JSON, nullable=False)  # [{job_id, score, rank}, ...]
    
    # Explanations
    explanations = Column(JSON, nullable=True)  # {job_id: explanation_text, ...}
    
    # Filtering and context
    filters_applied = Column(JSON, nullable=True)  # Location, job type, etc.
    algorithm_used = Column(Text, nullable=True)  # Which algorithm generated these
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    
    def __repr__(self):
        return f"<Recommendation(id={self.id}, user_id={self.user_id})>"
