"""
Jobs API Routes
===============

Endpoints for job listings, search, and management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from loguru import logger

from database import get_db
from models import Job
from schemas import JobCreate, JobUpdate, JobResponse, JobListResponse
from core.security import get_current_user


router = APIRouter()


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    query: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    remote_option: Optional[str] = None,
    min_salary: Optional[float] = None,
    skills: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of job listings with optional filters.
    
    Args:
        page: Page number
        per_page: Items per page
        query: Search query (title, company, description)
        location: Filter by location
        job_type: Filter by job type
        remote_option: Filter by remote option
        min_salary: Filter by minimum salary
        skills: Comma-separated skills filter
        
    Returns:
        Paginated job list
    """
    # Build query
    stmt = select(Job).where(Job.is_active == 1)
    
    # Apply filters
    if query:
        search_term = f"%{query}%"
        stmt = stmt.where(
            or_(
                Job.title.ilike(search_term),
                Job.company.ilike(search_term),
                Job.description.ilike(search_term)
            )
        )
    
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        stmt = stmt.where(Job.job_type == job_type)
    
    if remote_option:
        stmt = stmt.where(Job.remote_option == remote_option)
    
    if min_salary:
        stmt = stmt.where(Job.salary_min >= min_salary)
    
    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    stmt = stmt.offset(offset).limit(per_page).order_by(Job.created_at.desc())
    
    # Execute query
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    total_pages = (total + per_page - 1) // per_page
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific job by ID.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job details
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job listing.
    
    Args:
        job_data: Job creation data
        
    Returns:
        Created job
    """
    job = Job(**job_data.model_dump())
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    logger.info(f"Job created: {job.id} - {job.title}")
    
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a job listing.
    
    Args:
        job_id: Job ID to update
        job_data: Update data
        
    Returns:
        Updated job
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update fields
    for field, value in job_data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)
    
    logger.info(f"Job updated: {job_id}")
    
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (deactivate) a job listing.
    
    Args:
        job_id: Job ID to delete
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Soft delete
    job.is_active = 0
    await db.commit()
    
    logger.info(f"Job deactivated: {job_id}")


@router.get("/search/skills", response_model=List[JobResponse])
async def search_by_skills(
    skills: str = Query(..., description="Comma-separated list of skills"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Search jobs by matching skills.
    
    Args:
        skills: Comma-separated skills
        limit: Maximum results
        
    Returns:
        Matching jobs
    """
    skill_list = [s.strip().lower() for s in skills.split(",")]
    
    # Get jobs with any matching skills
    result = await db.execute(
        select(Job)
        .where(Job.is_active == 1)
        .limit(limit * 3)  # Get more to filter
    )
    jobs = result.scalars().all()
    
    # Score jobs by skill match
    scored_jobs = []
    for job in jobs:
        if job.skills_required:
            job_skills = [s.lower() for s in job.skills_required]
            match_count = sum(1 for s in skill_list if s in job_skills)
            if match_count > 0:
                scored_jobs.append((job, match_count))
    
    # Sort by match count and return top results
    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    
    return [job for job, _ in scored_jobs[:limit]]
