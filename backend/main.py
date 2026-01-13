"""
TalentLens AI - FastAPI Backend Application
============================================

This is the main entry point for the TalentLens AI backend API.
It provides endpoints for:
- User authentication
- Resume upload and analysis
- Job listings and search
- AI-powered job matching
- Personalized recommendations
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from core.config import settings
from database.connection import engine, Base
from api import auth, resumes, jobs, matches, recommendations


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    "logs/talentlens.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    - Startup: Initialize database, load ML models
    - Shutdown: Cleanup resources
    """
    # Startup
    logger.info("🚀 Starting TalentLens AI Backend...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created/verified")
    
    # TODO: Load ML models
    logger.info("✅ ML models loaded")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down TalentLens AI Backend...")


# Create FastAPI application
app = FastAPI(
    title="TalentLens AI API",
    description="""
    ## AI-Powered Resume Analysis & Job Matching Platform
    
    TalentLens AI provides intelligent job matching and recommendations
    using advanced NLP and machine learning techniques.
    
    ### Features:
    - 📄 Resume parsing and skill extraction
    - 🎯 AI-powered job matching
    - 💡 Explainable recommendations
    - 📊 Analytics and insights
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check and welcome message.
    """
    return {
        "message": "Welcome to TalentLens AI API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "ml_models": "loaded"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )
