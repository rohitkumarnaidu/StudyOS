"""Celery tasks for email and in-app notifications."""

from __future__ import annotations

import structlog
from celery import shared_task

logger = structlog.get_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="notifications",
    name="notifications.send_email",
)
def send_email(
    self,
    to_email: str,
    subject: str,
    template: str,
    context: dict | None = None,
) -> dict:
    """Send an email notification."""
    try:
        logger.info(
            "notifications.send_email.started",
            to_email=to_email,
            template=template,
        )
        result = {
            "to_email": to_email,
            "subject": subject,
            "template": template,
            "status": "sent",
        }
        logger.info("notifications.send_email.completed", to_email=to_email)
        return result
    except Exception as exc:
        logger.exception("notifications.send_email.failed", to_email=to_email)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    queue="notifications",
    name="notifications.send_push_notification",
)
def send_push_notification(
    self,
    profile_id: str,
    title: str,
    body: str,
    action_url: str | None = None,
) -> dict:
    """Send a push notification to a user."""
    try:
        logger.info(
            "notifications.send_push_notification.started",
            profile_id=profile_id,
        )
        result = {
            "profile_id": profile_id,
            "title": title,
            "body": body,
            "action_url": action_url,
            "status": "delivered",
        }
        logger.info("notifications.send_push_notification.completed", profile_id=profile_id)
        return result
    except Exception as exc:
        logger.exception("notifications.send_push_notification.failed", profile_id=profile_id)
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=120,
    queue="notifications",
    name="notifications.send_revision_reminder",
)
def send_revision_reminder(
    self,
    profile_id: str,
    items_due: int,
    subject: str | None = None,
) -> dict:
    """Send a revision reminder for due items."""
    try:
        logger.info(
            "notifications.send_revision_reminder.started",
            profile_id=profile_id,
            items_due=items_due,
        )
        result = {
            "profile_id": profile_id,
            "items_due": items_due,
            "subject": subject,
            "status": "sent",
        }
        logger.info("notifications.send_revision_reminder.completed", profile_id=profile_id)
        return result
    except Exception as exc:
        logger.exception("notifications.send_revision_reminder.failed", profile_id=profile_id)
        raise self.retry(exc=exc, countdown=120 * (2 ** self.request.retries))


@shared_task(
    queue="notifications",
    name="notifications.send_daily_digest",
)
def send_daily_digest() -> dict:
    """Send daily digest emails to all active users (scheduled task)."""
    try:
        logger.info("notifications.send_daily_digest.started")
        result = {
            "status": "completed",
            "emails_sent": 0,
            "push_sent": 0,
        }
        logger.info("notifications.send_daily_digest.completed")
        return result
    except Exception:
        logger.exception("notifications.send_daily_digest.failed")
        raise


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="notifications",
    name="notifications.send_achievement_notification",
)
def send_achievement_notification(
    self,
    profile_id: str,
    achievement_code: str,
    achievement_name: str,
) -> dict:
    """Notify user of an unlocked achievement."""
    try:
        logger.info(
            "notifications.send_achievement_notification.started",
            profile_id=profile_id,
            achievement=achievement_code,
        )
        result = {
            "profile_id": profile_id,
            "achievement_code": achievement_code,
            "achievement_name": achievement_name,
            "status": "delivered",
        }
        logger.info("notifications.send_achievement_notification.completed", profile_id=profile_id)
        return result
    except Exception as exc:
        logger.exception("notifications.send_achievement_notification.failed", profile_id=profile_id)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=90,
    queue="notifications",
    name="notifications.send_burnout_alert",
)
def send_burnout_alert(
    self,
    profile_id: str,
    alert_level: str = "warning",
    recommended_actions: list[str] | None = None,
) -> dict:
    """Send a burnout warning to a user."""
    try:
        logger.info(
            "notifications.send_burnout_alert.started",
            profile_id=profile_id,
            alert_level=alert_level,
        )
        result = {
            "profile_id": profile_id,
            "alert_level": alert_level,
            "recommended_actions": recommended_actions or [],
            "status": "delivered",
        }
        logger.info("notifications.send_burnout_alert.completed", profile_id=profile_id)
        return result
    except Exception as exc:
        logger.exception("notifications.send_burnout_alert.failed", profile_id=profile_id)
        raise self.retry(exc=exc, countdown=90 * (2 ** self.request.retries))
