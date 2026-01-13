"""
Resume API Routes
=================

Endpoints for resume upload, parsing, and management.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from database import get_db
from models import Resume, User
from schemas import ResumeResponse, ResumeDetailResponse, ResumeUploadResponse
from core.config import settings
from core.security import get_current_user
from services.resume_parser import ResumeParserService
from services.skill_extractor import SkillExtractorService


router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse a resume file (PDF or DOCX).
    
    Args:
        file: Resume file upload
        current_user_id: Current user's ID
        db: Database session
        
    Returns:
        Parsed resume with extracted information
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )
    
    try:
        # Parse resume
        parser = ResumeParserService()
        parsed_data = await parser.parse(contents, file_ext)
        
        # Extract skills
        skill_extractor = SkillExtractorService()
        skills = await skill_extractor.extract(parsed_data.get("raw_text", ""))
        
        # Create resume record
        resume = Resume(
            user_id=int(current_user_id),
            filename=file.filename,
            content_type=file.content_type,
            raw_text=parsed_data.get("raw_text"),
            parsed_data=parsed_data.get("sections"),
            skills=skills,
            experience_years=parsed_data.get("experience_years"),
            education=parsed_data.get("education"),
            work_history=parsed_data.get("work_history")
        )
        
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        
        logger.info(f"Resume uploaded: {resume.id} by user {current_user_id}")
        
        return ResumeUploadResponse(
            id=resume.id,
            filename=resume.filename,
            message="Resume uploaded and parsed successfully",
            skills_extracted=len(skills) if skills else 0
        )
        
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all resumes for the current user.
    
    Returns:
        List of user's resumes
    """
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == int(current_user_id))
        .order_by(Resume.created_at.desc())
    )
    resumes = result.scalars().all()
    
    return resumes


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific resume by ID.
    
    Args:
        resume_id: Resume ID
        
    Returns:
        Resume details
    """
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
    
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a resume.
    
    Args:
        resume_id: Resume ID to delete
    """
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
    
    await db.delete(resume)
    await db.commit()
    
    logger.info(f"Resume deleted: {resume_id} by user {current_user_id}")


@router.get("/{resume_id}/skills", response_model=List[str])
async def get_resume_skills(
    resume_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get extracted skills from a resume.
    
    Returns:
        List of skills
    """
    result = await db.execute(
        select(Resume.skills)
        .where(Resume.id == resume_id, Resume.user_id == int(current_user_id))
    )
    skills = result.scalar_one_or_none()
    
    if skills is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return skills or []
