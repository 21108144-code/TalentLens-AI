"""
Resume Model
============

SQLAlchemy model for resume documents.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, LargeBinary
from sqlalchemy.orm import relationship

from database.connection import Base


class Resume(Base):
    """
    Resume document model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        filename: Original filename
        file_path: Storage path
        raw_text: Extracted text content
        parsed_data: Structured parsed data (JSON)
        skills: Extracted skills list (JSON)
        experience_years: Calculated experience
        education: Education details (JSON)
        embedding: Vector embedding (binary)
        created_at: Upload timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    content_type = Column(String(100), nullable=True)
    
    # Extracted content
    raw_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Structured sections
    
    # Extracted features
    skills = Column(JSON, nullable=True)  # List of skills
    experience_years = Column(Integer, nullable=True)
    education = Column(JSON, nullable=True)  # Education history
    work_history = Column(JSON, nullable=True)  # Work experience
    
    # ML features
    embedding = Column(LargeBinary, nullable=True)  # Vector embedding
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    matches = relationship("Match", back_populates="resume", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Resume(id={self.id}, filename={self.filename})>"
