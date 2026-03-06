"""Email notification service for scheduled analysis results."""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings

logger = logging.getLogger(__name__)


def send_notification(subject: str, body_html: str) -> bool:
    """Send an email notification. Returns True if successful."""
    if not settings.smtp_host or not settings.notify_email:
        logger.debug("Email not configured, skipping notification")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = settings.notify_email
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from, settings.notify_email, msg.as_string())

        logger.info(f"Email sent: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def notify_analysis_complete(module: str, query: str, report_id: str, summary: str | None = None):
    """Send notification when a scheduled analysis completes."""
    subject = f"[SEO Dashboard] {module.upper()} phan tich hoan thanh: {query}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #2563eb; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">SEO Dashboard</h2>
            <p style="margin: 5px 0 0; opacity: 0.9;">Phan tich tu dong hoan thanh</p>
        </div>
        <div style="background: white; padding: 20px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px 0; color: #6b7280;">Module:</td><td style="padding: 8px 0; font-weight: bold;">{module}</td></tr>
                <tr><td style="padding: 8px 0; color: #6b7280;">Query:</td><td style="padding: 8px 0; font-weight: bold;">{query}</td></tr>
                <tr><td style="padding: 8px 0; color: #6b7280;">Report ID:</td><td style="padding: 8px 0;">{report_id}</td></tr>
            </table>
            {f'<div style="margin-top: 16px; padding: 12px; background: #f9fafb; border-radius: 6px;"><p style="margin: 0; color: #374151;">{summary}</p></div>' if summary else ''}
            <div style="margin-top: 20px;">
                <a href="http://localhost:3000/reports/{report_id}" style="display: inline-block; background: #2563eb; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none;">Xem bao cao</a>
            </div>
        </div>
    </body>
    </html>
    """
    send_notification(subject, body)


def notify_analysis_failed(module: str, query: str, error: str):
    """Send notification when a scheduled analysis fails."""
    subject = f"[SEO Dashboard] {module.upper()} phan tich THAT BAI: {query}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #dc2626; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0;">SEO Dashboard</h2>
            <p style="margin: 5px 0 0; opacity: 0.9;">Phan tich tu dong that bai</p>
        </div>
        <div style="background: white; padding: 20px; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px 0; color: #6b7280;">Module:</td><td style="padding: 8px 0; font-weight: bold;">{module}</td></tr>
                <tr><td style="padding: 8px 0; color: #6b7280;">Query:</td><td style="padding: 8px 0; font-weight: bold;">{query}</td></tr>
            </table>
            <div style="margin-top: 16px; padding: 12px; background: #fef2f2; border-radius: 6px; border: 1px solid #fecaca;">
                <p style="margin: 0; color: #991b1b;">{error}</p>
            </div>
        </div>
    </body>
    </html>
    """
    send_notification(subject, body)
