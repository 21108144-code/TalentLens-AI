"""
Recommendations API Routes
==========================

Endpoints for personalized job recommendations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from database import get_db
from models import Recommendation, Resume, Job
from schemas import (
    RecommendationRequest, 
    RecommendationResponse, 
    RecommendedJob,
    RecommendationFilters
)
from core.security import get_current_user
from services.recommendation_service import RecommendationService


router = APIRouter()


@router.post("/generate", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def generate_recommendations(
    request: RecommendationRequest,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate personalized job recommendations for a resume.
    
    Args:
        request: Recommendation request with resume ID and filters
        
    Returns:
        Top job recommendations with explanations
    """
    # Verify resume belongs to user
    result = await db.execute(
        select(Resume)
        .where(Resume.id == request.resume_id, Resume.user_id == int(current_user_id))
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get active jobs
    result = await db.execute(
        select(Job).where(Job.is_active == 1)
    )
    jobs = result.scalars().all()
    
    if not jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No jobs available"
        )
    
    # Generate recommendations
    recommendation_service = RecommendationService()
    recommendations = await recommendation_service.generate(
        resume=resume,
        jobs=jobs,
        filters=request.filters,
        limit=request.limit
    )
    
    # Store recommendations
    rec = Recommendation(
        user_id=int(current_user_id),
        resume_id=resume.id,
        job_recommendations=[
            {"job_id": r.job_id, "score": r.score, "rank": r.rank}
            for r in recommendations
        ],
        explanations={
            str(r.job_id): r.explanation for r in recommendations
        },
        filters_applied=request.filters,
        algorithm_used="hybrid_content_semantic"
    )
    
    db.add(rec)
    await db.commit()
    await db.refresh(rec)
    
    logger.info(f"Recommendations generated: {rec.id} for resume {resume.id}")
    
    return RecommendationResponse(
        id=rec.id,
        user_id=int(current_user_id),
        resume_id=resume.id,
        recommendations=recommendations,
        total_jobs_analyzed=len(jobs),
        algorithm_used="hybrid_content_semantic",
        created_at=rec.created_at
    )


@router.get("/resume/{resume_id}", response_model=RecommendationResponse)
async def get_recommendations(
    resume_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest recommendations for a resume.
    
    Args:
        resume_id: Resume ID
        
    Returns:
        Latest recommendations
    """
    # Get latest recommendation
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.resume_id == resume_id, Recommendation.user_id == int(current_user_id))
        .order_by(Recommendation.created_at.desc())
        .limit(1)
    )
    rec = result.scalar_one_or_none()
    
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No recommendations found. Generate recommendations first."
        )
    
    # Reconstruct recommendations with job details
    recommendations = []
    for job_rec in rec.job_recommendations:
        job_result = await db.execute(
            select(Job).where(Job.id == job_rec["job_id"])
        )
        job = job_result.scalar_one_or_none()
        
        if job:
            recommendations.append(RecommendedJob(
                job_id=job.id,
                rank=job_rec["rank"],
                score=job_rec["score"],
                title=job.title,
                company=job.company,
                location=job.location,
                salary_range=f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}" if job.salary_min else None,
                explanation=rec.explanations.get(str(job.id), ""),
                skill_overlap=[],
                skill_gaps=[],
                match_highlights=[]
            ))
    
    return RecommendationResponse(
        id=rec.id,
        user_id=rec.user_id,
        resume_id=rec.resume_id,
        recommendations=recommendations,
        total_jobs_analyzed=len(rec.job_recommendations),
        algorithm_used=rec.algorithm_used or "hybrid_content_semantic",
        created_at=rec.created_at
    )


@router.get("/history", response_model=List[RecommendationResponse])
async def get_recommendation_history(
    limit: int = Query(10, ge=1, le=50),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommendation history for the current user.
    
    Args:
        limit: Maximum number of records
        
    Returns:
        List of past recommendations
    """
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.user_id == int(current_user_id))
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    recs = result.scalars().all()
    
    history = []
    for rec in recs:
        # Simplified response for history
        history.append(RecommendationResponse(
            id=rec.id,
            user_id=rec.user_id,
            resume_id=rec.resume_id,
            recommendations=[],  # Empty for history overview
            total_jobs_analyzed=len(rec.job_recommendations),
            algorithm_used=rec.algorithm_used or "hybrid_content_semantic",
            created_at=rec.created_at
        ))
    
    return history


@router.delete("/{rec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    rec_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a recommendation record.
    
    Args:
        rec_id: Recommendation ID
    """
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.id == rec_id, Recommendation.user_id == int(current_user_id))
    )
    rec = result.scalar_one_or_none()
    
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    await db.delete(rec)
    await db.commit()
    
    logger.info(f"Recommendation deleted: {rec_id}")
