"""
Matches API Routes
==================

Endpoints for resume-job matching and score calculation.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from database import get_db
from models import Match, Resume, Job
from schemas import MatchCreate, MatchResponse, MatchDetailResponse, MatchListResponse, MatchExplanation
from core.security import get_current_user
from services.matching_service import MatchingService


router = APIRouter()


@router.post("/calculate", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def calculate_match(
    match_data: MatchCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate match score between a resume and a job.
    
    Args:
        match_data: Resume and job IDs
        
    Returns:
        Match scores and analysis
    """
    # Verify resume belongs to user
    result = await db.execute(
        select(Resume)
        .where(Resume.id == match_data.resume_id, Resume.user_id == int(current_user_id))
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get job
    result = await db.execute(select(Job).where(Job.id == match_data.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check for existing match
    result = await db.execute(
        select(Match)
        .where(Match.resume_id == match_data.resume_id, Match.job_id == match_data.job_id)
    )
    existing_match = result.scalar_one_or_none()
    
    if existing_match:
        return existing_match
    
    # Calculate match
    matching_service = MatchingService()
    match_result = await matching_service.calculate_match(resume, job)
    
    # Create match record
    match = Match(
        resume_id=resume.id,
        job_id=job.id,
        overall_score=match_result["overall_score"],
        skill_score=match_result["skill_score"],
        experience_score=match_result["experience_score"],
        education_score=match_result["education_score"],
        semantic_score=match_result["semantic_score"],
        skill_overlap=match_result["skill_overlap"],
        skill_gaps=match_result["skill_gaps"],
        explanation=match_result["explanation"],
        feature_importance=match_result["feature_importance"]
    )
    
    db.add(match)
    await db.commit()
    await db.refresh(match)
    
    logger.info(f"Match calculated: resume {resume.id} -> job {job.id} = {match.overall_score}%")
    
    return match


@router.get("/resume/{resume_id}", response_model=MatchListResponse)
async def get_resume_matches(
    resume_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all match scores for a resume.
    
    Args:
        resume_id: Resume ID
        
    Returns:
        List of matches with job details
    """
    # Verify resume belongs to user
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id, Resume.user_id == int(current_user_id))
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get matches with job info
    result = await db.execute(
        select(Match)
        .where(Match.resume_id == resume_id)
        .order_by(Match.overall_score.desc())
    )
    matches = result.scalars().all()
    
    # Enrich with job info
    enriched_matches = []
    for match in matches:
        job_result = await db.execute(select(Job).where(Job.id == match.job_id))
        job = job_result.scalar_one_or_none()
        
        enriched_matches.append(MatchDetailResponse(
            id=match.id,
            resume_id=match.resume_id,
            job_id=match.job_id,
            overall_score=match.overall_score,
            skill_score=match.skill_score,
            experience_score=match.experience_score,
            education_score=match.education_score,
            semantic_score=match.semantic_score,
            skill_overlap=match.skill_overlap,
            skill_gaps=match.skill_gaps,
            explanation=match.explanation,
            created_at=match.created_at,
            job_title=job.title if job else None,
            job_company=job.company if job else None,
            feature_importance=match.feature_importance
        ))
    
    return MatchListResponse(
        resume_id=resume_id,
        matches=enriched_matches,
        total=len(enriched_matches)
    )


@router.get("/{match_id}", response_model=MatchDetailResponse)
async def get_match(
    match_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific match by ID.
    
    Args:
        match_id: Match ID
        
    Returns:
        Match details
    """
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Get job info
    job_result = await db.execute(select(Job).where(Job.id == match.job_id))
    job = job_result.scalar_one_or_none()
    
    return MatchDetailResponse(
        id=match.id,
        resume_id=match.resume_id,
        job_id=match.job_id,
        overall_score=match.overall_score,
        skill_score=match.skill_score,
        experience_score=match.experience_score,
        education_score=match.education_score,
        semantic_score=match.semantic_score,
        skill_overlap=match.skill_overlap,
        skill_gaps=match.skill_gaps,
        explanation=match.explanation,
        created_at=match.created_at,
        job_title=job.title if job else None,
        job_company=job.company if job else None,
        feature_importance=match.feature_importance
    )


@router.get("/{match_id}/explain", response_model=MatchExplanation)
async def explain_match(
    match_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed explanation for a match.
    
    Args:
        match_id: Match ID
        
    Returns:
        Detailed explanation
    """
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Generate explanation
    matching_service = MatchingService()
    explanation = await matching_service.generate_explanation(match)
    
    return explanation
