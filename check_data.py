import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from database.connection import async_session_maker
from models import Resume, Job
from sqlalchemy import select

async def check():
    async with async_session_maker() as db:
        # Check Resume
        res = await db.execute(select(Resume).where(Resume.id == 1))
        resume = res.scalar_one_or_none()
        if resume:
            print(f"Resume ID: {resume.id}")
            print(f"Skills: {resume.skills}")
            print(f"Exp Years: {resume.experience_years}")
        else:
            print("Resume ID 1 not found")

        # Check Jobs
        res = await db.execute(select(Job).where(Job.is_active == 1))
        jobs = res.scalars().all()
        print(f"\nActive Jobs: {len(jobs)}")
        for j in jobs[:2]:
            print(f"Job ID: {j.id}, Title: {j.title}")
            print(f"Skills Req: {j.skills_required}")
            print(f"Location: {j.location}")
            print(f"Created At: {j.created_at}")

if __name__ == "__main__":
    asyncio.run(check())
