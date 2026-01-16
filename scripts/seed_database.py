"""
Database Seeder Script
======================

Loads seed data into the database using SQLAlchemy models.
This ensures the schema ALWAYS matches the application models.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from database.connection import engine, Base, async_session_maker
from models import Job
from sqlalchemy import delete


async def seed_jobs():
    """Seed the database with job listings using SQLAlchemy models."""
    
    # Load seed data
    seed_file = Path(__file__).parent.parent / "data" / "raw" / "seed_jobs.json"
    
    if not seed_file.exists():
        print(f"Seed file not found: {seed_file}")
        return
    
    with open(seed_file, "r") as f:
        jobs_data = json.load(f)
    
    print(f"Loaded {len(jobs_data)} jobs from seed file")
    
    # Create all tables using SQLAlchemy models (this ensures correct schema)
    async with engine.begin() as conn:
        # This creates tables if they don't exist, with the CORRECT schema
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables verified/created with correct schema")
    
    # Clear existing jobs and insert new ones
    async with async_session_maker() as session:
        # Delete all existing jobs
        await session.execute(delete(Job))
        await session.commit()
        print("Cleared existing jobs")
        
        # Insert new jobs using the SQLAlchemy model
        for job_data in jobs_data:
            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                description=job_data.get("description", ""),
                requirements=job_data.get("requirements"),
                skills_required=job_data.get("skills_required", []),
                experience_required=job_data.get("experience_required"),
                education_required=job_data.get("education_required"),
                location=job_data.get("location"),
                job_type=job_data.get("job_type"),
                remote_option=job_data.get("remote_option"),
                salary_min=job_data.get("salary_min"),
                salary_max=job_data.get("salary_max"),
                salary_currency="USD",
                apply_url=job_data.get("apply_url"),
                is_active=1
            )
            session.add(job)
        
        await session.commit()
        print(f"Inserted {len(jobs_data)} jobs into database")
    
    await engine.dispose()
    print("✅ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_jobs())
