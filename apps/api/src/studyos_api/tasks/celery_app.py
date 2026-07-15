"""Celery application for StudyOS distributed task queue."""

from __future__ import annotations

from typing import Any

from celery import Celery

from studyos_api.core.config import get_settings


def _build_celery_config() -> dict[str, Any]:
    settings = get_settings()
    broker = settings.celery_broker_url or settings.redis_url or "redis://localhost:6379/1"
    backend = settings.celery_result_backend or settings.redis_url or "redis://localhost:6379/2"

    return {
        "broker_url": broker,
        "result_backend": backend,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "timezone": "UTC",
        "enable_utc": True,
        "task_track_started": True,
        "task_acks_late": True,
        "worker_prefetch_multiplier": 1,
        "task_default_retry_delay": settings.celery_task_default_retry_delay,
        "task_max_retries": settings.celery_task_max_retries,
        "task_annotate": {
            "studyos_api.tasks.*": {
                "rate_limit": "100/m",
            },
        },
        "task_routes": {
            "studyos_api.tasks.ai_tasks.*": {"queue": "ai"},
            "studyos_api.tasks.report_tasks.*": {"queue": "reports"},
            "studyos_api.tasks.notification_tasks.*": {"queue": "notifications"},
        },
        "beat_schedule": {
            "cleanup-expired-sessions": {
                "task": "studyos_api.tasks.report_tasks.cleanup_expired_sessions",
                "schedule": 3600.0,
            },
            "send-digest-emails": {
                "task": "studyos_api.tasks.notification_tasks.send_daily_digest",
                "schedule": 86400.0,
            },
        },
    }


def _create_celery_app() -> Celery:
    app = Celery("studyos")
    app.config_from_object(_build_celery_config)
    return app


celery_app = _create_celery_app()
