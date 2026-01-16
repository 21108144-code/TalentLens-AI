import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from database.connection import async_session_maker
from models import Resume, Job
from services.recommendation_service import RecommendationService
from sqlalchemy import select

async def test():
    async with async_session_maker() as db:
        # Get resume
        resume_result = await db.execute(select(Resume).where(Resume.id == 1))
        resume = resume_result.scalar_one_or_none()
        if not resume:
            print("Resume ID 1 not found!")
            return
            
        print(f"Testing with Resume ID: {resume.id} ({resume.filename})")
        print(f"Skills: {resume.skills}")

        # Get jobs
        jobs_result = await db.execute(select(Job).where(Job.is_active == 1))
        jobs = jobs_result.scalars().all()
        print(f"Testing with {len(jobs)} jobs")
        
        # Generate recs
        service = RecommendationService()
        # Use empty filters like the frontend
        recs = await service.generate(resume, jobs, filters={})
        
        print(f"\nGot {len(recs)} recommendations")
        for r in recs:
            print(f"- {r.title} at {r.company} (Score: {r.score}%)")
            print(f"  Location: {r.location}, Recent: True")

if __name__ == "__main__":
    asyncio.run(test())
