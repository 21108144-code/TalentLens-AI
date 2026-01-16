import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from database.connection import async_session_maker
from models import User
from sqlalchemy import select

async def test():
    print("Testing User retrieval...")
    async with async_session_maker() as db:
        try:
            current_user_id = "1"
            result = await db.execute(select(User).where(User.id == int(current_user_id)))
            user = result.scalar_one_or_none()
            if user:
                print(f"✅ Success: Found user {user.email}")
            else:
                print("❌ Error: User not found")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
