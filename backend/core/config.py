"""
Application Configuration
=========================

Centralized configuration management using Pydantic Settings.
All configuration values are loaded from environment variables.
"""

from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application
    APP_NAME: str = "TalentLens AI"
    DEBUG: bool = False
    
    # Backend Server
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./talentlens.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # ML Models
    MODEL_PATH: str = "./ml/models"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".doc"]
    UPLOAD_DIR: str = "./uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()


# Global settings instance
settings = get_settings()
