"""
Complete database reset script.
Deletes the database and recreates ALL tables from scratch using SQLAlchemy.
"""

import asyncio
import json
from pathlib import Path
import sys
import os

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Delete the database file first
db_path = Path(__file__).parent / "backend" / "talentlens.db"
if db_path.exists():
    os.remove(db_path)
    print(f"Deleted old database: {db_path}")

from database.connection import engine, Base
from models import User, Resume, Job, Match, Recommendation


async def reset_database():
    """Completely reset the database."""
    
    print("Creating fresh database with correct schema...")
    
    # Create ALL tables from scratch using SQLAlchemy models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("All tables created with correct schema")
    
    # Load and insert seed jobs
    seed_file = Path(__file__).parent / "data" / "raw" / "seed_jobs.json"
    
    if seed_file.exists():
        with open(seed_file, "r") as f:
            jobs_data = json.load(f)
        
        print(f"Loaded {len(jobs_data)} jobs from seed file")
        
        from database.connection import async_session_maker
        
        async with async_session_maker() as session:
            for job_data in jobs_data:
                job = Job(
                    title=job_data["title"],
                    company=job_data["company"],
                    description=job_data.get("description", "No description"),
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
            print(f"Inserted {len(jobs_data)} jobs")
    
    await engine.dispose()
    print("✅ Database reset complete!")
    print("\n⚠️ NOTE: You need to register a new user and upload your resume again!")


if __name__ == "__main__":
    asyncio.run(reset_database())
