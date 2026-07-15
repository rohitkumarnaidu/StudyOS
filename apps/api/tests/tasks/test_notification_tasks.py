"""Tests for notification Celery tasks."""

from studyos_api.tasks.notification_tasks import (
    send_burnout_alert,
    send_daily_digest,
    send_email,
    send_achievement_notification,
    send_push_notification,
    send_revision_reminder,
)


class TestSendEmail:
    def test_send_email_success(self) -> None:
        result = send_email(
            to_email="user@example.com",
            subject="Welcome to StudyOS",
            template="welcome",
            context={"name": "Test User"},
        )
        assert result["to_email"] == "user@example.com"
        assert result["subject"] == "Welcome to StudyOS"
        assert result["template"] == "welcome"
        assert result["status"] == "sent"

    def test_send_email_without_context(self) -> None:
        result = send_email(
            to_email="user@example.com",
            subject="Test",
            template="test",
        )
        assert result["status"] == "sent"

    def test_send_email_retry_config(self) -> None:
        task = send_email
        assert task.max_retries == 3
        assert task.default_retry_delay == 60
        assert task.queue == "notifications"


class TestSendPushNotification:
    def test_send_push_notification_success(self) -> None:
        result = send_push_notification(
            profile_id="user-123",
            title="Study Reminder",
            body="Time to study Physics!",
            action_url="/study/physics",
        )
        assert result["profile_id"] == "user-123"
        assert result["title"] == "Study Reminder"
        assert result["body"] == "Time to study Physics!"
        assert result["action_url"] == "/study/physics"
        assert result["status"] == "delivered"

    def test_send_push_notification_without_action_url(self) -> None:
        result = send_push_notification(
            profile_id="user-456",
            title="Alert",
            body="Something happened",
        )
        assert result["action_url"] is None

    def test_send_push_notification_retry_config(self) -> None:
        task = send_push_notification
        assert task.max_retries == 2
        assert task.default_retry_delay == 30


class TestSendRevisionReminder:
    def test_send_revision_reminder_success(self) -> None:
        result = send_revision_reminder(
            profile_id="user-123",
            items_due=5,
            subject="Biology",
        )
        assert result["profile_id"] == "user-123"
        assert result["items_due"] == 5
        assert result["subject"] == "Biology"
        assert result["status"] == "sent"

    def test_send_revision_reminder_without_subject(self) -> None:
        result = send_revision_reminder(
            profile_id="user-456",
            items_due=10,
        )
        assert result["subject"] is None

    def test_send_revision_reminder_retry_config(self) -> None:
        task = send_revision_reminder
        assert task.max_retries == 3
        assert task.default_retry_delay == 120


class TestSendDailyDigest:
    def test_send_daily_digest_success(self) -> None:
        result = send_daily_digest()
        assert result["status"] == "completed"
        assert "emails_sent" in result
        assert "push_sent" in result


class TestSendAchievementNotification:
    def test_send_achievement_notification_success(self) -> None:
        result = send_achievement_notification(
            profile_id="user-123",
            achievement_code="first_quiz",
            achievement_name="First Quiz Completed",
        )
        assert result["profile_id"] == "user-123"
        assert result["achievement_code"] == "first_quiz"
        assert result["achievement_name"] == "First Quiz Completed"
        assert result["status"] == "delivered"

    def test_send_achievement_notification_retry_config(self) -> None:
        task = send_achievement_notification
        assert task.max_retries == 3
        assert task.default_retry_delay == 60


class TestSendBurnoutAlert:
    def test_send_burnout_alert_success(self) -> None:
        result = send_burnout_alert(
            profile_id="user-123",
            alert_level="critical",
            recommended_actions=["Take a break", "Sleep well"],
        )
        assert result["profile_id"] == "user-123"
        assert result["alert_level"] == "critical"
        assert result["recommended_actions"] == ["Take a break", "Sleep well"]
        assert result["status"] == "delivered"

    def test_send_burnout_alert_default_values(self) -> None:
        result = send_burnout_alert(profile_id="user-456")
        assert result["alert_level"] == "warning"
        assert result["recommended_actions"] == []

    def test_send_burnout_alert_retry_config(self) -> None:
        task = send_burnout_alert
        assert task.max_retries == 2
        assert task.default_retry_delay == 90
