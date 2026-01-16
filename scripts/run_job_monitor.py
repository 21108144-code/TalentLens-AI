"""
Job Monitor CLI Runner
=======================

Run this script to start the job monitor.
It will scrape jobs from free sources and notify you of matching opportunities.

Usage:
    python run_job_monitor.py              # Run once
    python run_job_monitor.py --schedule   # Run on schedule (every 30 minutes)
    python run_job_monitor.py --test       # Test notifications only
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend to path BEFORE other imports
backend_path = str(Path(__file__).parent.parent / "backend")
sys.path.insert(0, backend_path)
os.chdir(backend_path)  # Change to backend directory

from loguru import logger

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO"
)
logger.add(
    "logs/job_monitor.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG"
)


async def run_once():
    """Run the job monitor once."""
    from tasks.job_monitor import JobMonitor
    
    print("\n" + "=" * 60)
    print("🔍 TalentLens AI - Job Monitor")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    monitor = JobMonitor()
    result = await monitor.run_monitor(
        min_match_score=40,
        notify_desktop=True,
        notify_email=True
    )
    
    print("\n" + "-" * 60)
    print("📊 Results Summary:")
    print(f"  • Total jobs scraped: {result.get('total_scraped', 0)}")
    print(f"  • New jobs found: {result.get('new_jobs', 0)}")
    print(f"  • Matching jobs: {result.get('matching_jobs', 0)}")
    print(f"  • Stored in database: {result.get('stored_in_db', 0)}")
    
    notifications = result.get('notifications', {})
    print(f"  • Desktop notification: {'✅ Sent' if notifications.get('desktop_sent') else '❌ Not sent'}")
    print(f"  • Email notification: {'✅ Sent' if notifications.get('email_sent') else '❌ Not configured'}")
    
    top_matches = result.get('top_matches', [])
    if top_matches:
        print("\n🎯 Top Matching Jobs:")
        for i, job in enumerate(top_matches, 1):
            print(f"  {i}. {job.get('title')} at {job.get('company')} ({job.get('score')}% match)")
    
    print("\n" + "=" * 60)
    return result


async def run_scheduled():
    """Run the job monitor on a schedule."""
    import schedule
    import time
    
    print("\n" + "=" * 60)
    print("🔄 TalentLens AI - Job Monitor (Scheduled Mode)")
    print("=" * 60)
    print("Running every 30 minutes. Press Ctrl+C to stop.")
    print("-" * 60 + "\n")
    
    # Run immediately first
    await run_once()
    
    # Schedule future runs
    def sync_run():
        asyncio.run(run_once())
    
    schedule.every(30).minutes.do(sync_run)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n👋 Job monitor stopped by user.")


async def test_notifications():
    """Test the notification system."""
    from services.notification_service import NotificationService
    
    print("\n" + "=" * 60)
    print("🧪 Testing Notifications")
    print("=" * 60)
    
    notifier = NotificationService()
    results = notifier.test_notifications()
    
    print(f"\n📱 Desktop notification: {'✅ Working' if results.get('desktop') else '❌ Failed'}")
    print(f"📧 Email notification: {'✅ Working' if results.get('email') else '❌ Not configured'}")
    
    if not results.get('email'):
        print("\n💡 To enable email notifications, set these in your .env file:")
        print("   EMAIL_USER=your.email@gmail.com")
        print("   EMAIL_PASSWORD=your-app-password")
        print("   NOTIFICATION_EMAIL=where.to.send@email.com")
        print("\n   For Gmail, use an App Password: https://myaccount.google.com/apppasswords")
    
    print("\n" + "=" * 60)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="TalentLens AI Job Monitor - Find matching jobs from free sources"
    )
    parser.add_argument(
        '--schedule', 
        action='store_true',
        help='Run on schedule (every 30 minutes)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test notifications only'
    )
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_notifications())
    elif args.schedule:
        asyncio.run(run_scheduled())
    else:
        asyncio.run(run_once())


if __name__ == "__main__":
    main()
