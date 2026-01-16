"""
Fix database schema to match SQLAlchemy models EXACTLY.
This drops and recreates all tables using SQLAlchemy.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from database.connection import engine, Base
from models import User, Resume, Job, Match, Recommendation
from sqlalchemy import text


async def fix_schema():
    """Drop and recreate the jobs table with correct schema."""
    
    print("Fixing database schema...")
    
    async with engine.begin() as conn:
        # Drop the jobs table completely
        await conn.execute(text("DROP TABLE IF EXISTS jobs"))
        print("Dropped jobs table")
        
        # Recreate using SQLAlchemy model (this ensures correct schema)
        await conn.run_sync(Base.metadata.create_all)
        print("Recreated all tables with correct schema")
    
    # Now load seed data
    seed_file = Path(__file__).parent / "data" / "raw" / "seed_jobs.json"
    
    if not seed_file.exists():
        print(f"Seed file not found: {seed_file}")
        return
    
    with open(seed_file, "r") as f:
        jobs_data = json.load(f)
    
    print(f"Loaded {len(jobs_data)} jobs from seed file")
    
    # Insert using raw SQL to avoid any ORM issues
    async with engine.begin() as conn:
        for job_data in jobs_data:
            skills_json = json.dumps(job_data.get("skills_required", []))
            await conn.execute(text("""
                INSERT INTO jobs 
                (title, company, description, requirements, skills_required, 
                 experience_required, education_required, location, job_type, 
                 remote_option, salary_min, salary_max, salary_currency, 
                 is_active, apply_url)
                VALUES 
                (:title, :company, :description, :requirements, :skills,
                 :experience, :education, :location, :job_type,
                 :remote_option, :salary_min, :salary_max, 'USD',
                 1, :apply_url)
            """), {
                "title": job_data["title"],
                "company": job_data["company"],
                "description": job_data.get("description", "No description"),
                "requirements": job_data.get("requirements"),
                "skills": skills_json,
                "experience": job_data.get("experience_required"),
                "education": job_data.get("education_required"),
                "location": job_data.get("location"),
                "job_type": job_data.get("job_type"),
                "remote_option": job_data.get("remote_option"),
                "salary_min": job_data.get("salary_min"),
                "salary_max": job_data.get("salary_max"),
                "apply_url": job_data.get("apply_url")
            })
    
    print(f"Inserted {len(jobs_data)} jobs")
    
    # Verify
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM jobs"))
        count = result.scalar()
        print(f"Verified: {count} jobs in database")
        
        result = await conn.execute(text("PRAGMA table_info(jobs)"))
        cols = [row[1] for row in result.fetchall()]
        print(f"Columns: {cols}")
    
    await engine.dispose()
    print("✅ Database schema fixed!")


if __name__ == "__main__":
    asyncio.run(fix_schema())
