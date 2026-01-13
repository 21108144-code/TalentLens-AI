"""
Skill Model
===========

SQLAlchemy model for skills taxonomy.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, LargeBinary

from database.connection import Base


class Skill(Base):
    """
    Skill taxonomy model.
    
    Attributes:
        id: Primary key
        name: Skill name (normalized)
        category: Skill category (technical, soft, domain)
        subcategory: More specific categorization
        aliases: Alternative names for the skill (JSON)
        related_skills: Related skill IDs (JSON)
        embedding: Vector embedding (binary)
        created_at: Creation timestamp
    """
    
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Skill information
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)  # technical, soft, domain
    subcategory = Column(String(100), nullable=True)  # More specific category
    
    # Aliases and relationships
    aliases = Column(JSON, nullable=True)  # Alternative names
    related_skills = Column(JSON, nullable=True)  # Related skill IDs
    
    # ML features
    embedding = Column(LargeBinary, nullable=True)  # Vector embedding
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Skill(id={self.id}, name={self.name})>"
