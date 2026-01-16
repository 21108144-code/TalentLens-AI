"""
Notification Service
=====================

Sends notifications via:
- Desktop notifications (Windows/Linux/Mac)
- Email (Gmail SMTP - free)
- Optional: Telegram bot (future)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from loguru import logger

try:
    from plyer import notification as desktop_notification
    DESKTOP_AVAILABLE = True
except ImportError:
    DESKTOP_AVAILABLE = False
    logger.warning("Desktop notifications not available (plyer not installed)")


class NotificationService:
    """
    Sends notifications through multiple channels.
    """
    
    def __init__(self):
        # Email configuration (set in environment variables)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')  # App password for Gmail
        self.notification_email = os.getenv('NOTIFICATION_EMAIL', '')  # Where to send alerts
    
    def send_desktop_notification(self, title: str, message: str, timeout: int = 10) -> bool:
        """
        Send a desktop notification.
        
        Args:
            title: Notification title
            message: Notification message
            timeout: How long to show (seconds)
            
        Returns:
            True if sent successfully
        """
        if not DESKTOP_AVAILABLE:
            logger.warning("Desktop notifications not available")
            return False
        
        try:
            desktop_notification.notify(
                title=title,
                message=message[:256],  # Windows limit
                app_name="TalentLens AI",
                timeout=timeout
            )
            logger.info(f"Desktop notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Desktop notification failed: {e}")
            return False
    
    def send_email_notification(self, 
                                 subject: str, 
                                 body: str,
                                 to_email: Optional[str] = None) -> bool:
        """
        Send an email notification.
        
        Args:
            subject: Email subject
            body: Email body (HTML supported)
            to_email: Recipient email (defaults to NOTIFICATION_EMAIL)
            
        Returns:
            True if sent successfully
        """
        recipient = to_email or self.notification_email
        
        if not all([self.email_user, self.email_password, recipient]):
            logger.warning("Email not configured. Set EMAIL_USER, EMAIL_PASSWORD, and NOTIFICATION_EMAIL in .env")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = recipient
            
            # Create HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #6366f1;">🎯 TalentLens AI - New Job Alert!</h2>
                <div style="background: #f0f9ff; padding: 15px; border-radius: 8px;">
                    {body}
                </div>
                <hr style="margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    This is an automated notification from TalentLens AI Job Monitor.
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False
    
    def send_job_alert(self, jobs: List[Dict], via_desktop: bool = True, via_email: bool = True) -> Dict:
        """
        Send job alert notifications.
        
        Args:
            jobs: List of matching jobs
            via_desktop: Send desktop notification
            via_email: Send email notification
            
        Returns:
            Status dict with results
        """
        results = {
            'desktop_sent': False,
            'email_sent': False,
            'jobs_count': len(jobs)
        }
        
        if not jobs:
            logger.info("No jobs to notify about")
            return results
        
        # Prepare notification content
        job_count = len(jobs)
        
        # Desktop notification (brief)
        if via_desktop:
            title = f"🎯 {job_count} New Job{'s' if job_count > 1 else ''} Found!"
            
            # Show first 2-3 jobs
            message_parts = []
            for job in jobs[:3]:
                message_parts.append(f"• {job.get('title', 'Job')} at {job.get('company', 'Company')}")
            
            if job_count > 3:
                message_parts.append(f"... and {job_count - 3} more")
            
            message = "\n".join(message_parts)
            results['desktop_sent'] = self.send_desktop_notification(title, message)
        
        # Email notification (detailed)
        if via_email:
            subject = f"🎯 TalentLens AI: {job_count} New Matching Job{'s' if job_count > 1 else ''}"
            
            # Build HTML email body
            job_rows = []
            for job in jobs:
                match_score = job.get('match_score', 0)
                score_color = '#22c55e' if match_score >= 70 else '#f59e0b' if match_score >= 50 else '#64748b'
                
                job_rows.append(f"""
                <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid {score_color};">
                    <h3 style="margin: 0; color: #1e293b;">{job.get('title', 'Unknown Title')}</h3>
                    <p style="margin: 5px 0; color: #64748b;">
                        <strong>{job.get('company', 'Unknown')}</strong> • {job.get('location', 'Remote')}
                    </p>
                    <p style="margin: 5px 0; color: #6366f1; font-weight: bold;">
                        Match Score: {match_score}%
                    </p>
                    <p style="margin: 10px 0; color: #475569; font-size: 14px;">
                        {job.get('description', '')[:200]}...
                    </p>
                    <a href="{job.get('apply_url', '#')}" 
                       style="display: inline-block; background: #6366f1; color: white; 
                              padding: 8px 16px; text-decoration: none; border-radius: 5px;">
                        Apply Now →
                    </a>
                    <span style="color: #94a3b8; font-size: 12px; margin-left: 10px;">
                        Source: {job.get('source', 'Unknown')}
                    </span>
                </div>
                """)
            
            body = f"""
            <p style="color: #1e293b; font-size: 16px;">
                Found <strong>{job_count}</strong> new job{'s' if job_count > 1 else ''} matching your profile:
            </p>
            {''.join(job_rows)}
            <p style="color: #64748b; margin-top: 20px;">
                <a href="http://localhost:5173/recommendations" style="color: #6366f1;">
                    View all recommendations in TalentLens AI →
                </a>
            </p>
            """
            
            results['email_sent'] = self.send_email_notification(subject, body)
        
        return results
    
    def test_notifications(self) -> Dict:
        """Test all notification channels."""
        results = {}
        
        # Test desktop
        results['desktop'] = self.send_desktop_notification(
            "🧪 TalentLens AI Test",
            "Desktop notifications are working!"
        )
        
        # Test email
        results['email'] = self.send_email_notification(
            "🧪 TalentLens AI - Notification Test",
            "<p>Email notifications are working! You will receive job alerts here.</p>"
        )
        
        return results
