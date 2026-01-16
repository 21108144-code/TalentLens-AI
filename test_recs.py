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
    print("Starting recommendation test...")
    async with async_session_maker() as db:
        # Get resume
        resume_result = await db.execute(select(Resume).limit(1))
        resume = resume_result.scalar_one_or_none()
        if not resume:
            print("ERROR: No resume found in database!")
            return
            
        print(f"Resume ID: {resume.id} ({resume.filename})")
        print(f"Skills: {resume.skills}")

        # Get jobs
        jobs_result = await db.execute(select(Job).where(Job.is_active == 1))
        jobs = jobs_result.scalars().all()
        print(f"Found {len(jobs)} active jobs")
        
        if not jobs:
            print("ERROR: No jobs found!")
            return
        
        # Generate recs
        print("\nGenerating recommendations...")
        service = RecommendationService()
        try:
            recs = await service.generate(resume, jobs, filters={})
            print(f"\n✅ SUCCESS! Got {len(recs)} recommendations:")
            for r in recs:
                print(f"  - {r.title} at {r.company} (Score: {r.score}%)")
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
