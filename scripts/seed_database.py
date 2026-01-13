"""
Database Seeder Script
======================

Loads seed data into the database for testing.
"""

import asyncio
import json
import os
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text


async def seed_jobs():
    """Seed the database with job listings."""
    # Load seed data
    seed_file = Path(__file__).parent.parent / "data" / "raw" / "seed_jobs.json"
    
    if not seed_file.exists():
        print(f"Seed file not found: {seed_file}")
        return
    
    with open(seed_file, "r") as f:
        jobs = json.load(f)
    
    print(f"Loaded {len(jobs)} jobs from seed file")
    
    # Create database connection
    db_path = Path(__file__).parent.parent / "backend" / "talentlens.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    
    async with engine.begin() as conn:
        # Drop and recreate jobs table to ensure clean schema
        await conn.execute(text("DROP TABLE IF EXISTS jobs"))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                company VARCHAR(200) NOT NULL,
                location VARCHAR(200),
                job_type VARCHAR(50),
                remote_option VARCHAR(50),
                description TEXT,
                requirements TEXT,
                skills_required JSON,
                experience_required INTEGER,
                education_required VARCHAR(100),
                salary_min INTEGER,
                salary_max INTEGER,
                apply_url VARCHAR(500),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Insert jobs
        for job in jobs:
            skills_json = json.dumps(job.get("skills_required", []))
            await conn.execute(text("""
                INSERT OR REPLACE INTO jobs 
                (id, title, company, location, job_type, remote_option, 
                 description, requirements, skills_required, experience_required,
                 education_required, salary_min, salary_max, apply_url, is_active, created_at)
                VALUES 
                (:id, :title, :company, :location, :job_type, :remote_option,
                 :description, :requirements, :skills, :experience,
                 :education, :salary_min, :salary_max, :apply_url, 1, :created_at)
            """), {
                "id": job["id"],
                "title": job["title"],
                "company": job["company"],
                "location": job.get("location"),
                "job_type": job.get("job_type"),
                "remote_option": job.get("remote_option"),
                "description": job.get("description"),
                "requirements": job.get("requirements"),
                "skills": skills_json,
                "experience": job.get("experience_required"),
                "education": job.get("education_required"),
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "apply_url": job.get("apply_url"),
                "created_at": job.get("created_at") or "2026-01-13 15:00:00"
            })
        
        print(f"Inserted {len(jobs)} jobs into database")
    
    await engine.dispose()
    print("Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_jobs())
