"""Tests for Celery task configuration."""

import os
from unittest.mock import patch

import pytest

from studyos_api.tasks.celery_app import _build_celery_config, celery_app


class TestCeleryConfig:
    def test_default_config(self) -> None:
        config = _build_celery_config()
        assert config["broker_url"] == "redis://localhost:6379/1"
        assert config["result_backend"] == "redis://localhost:6379/2"
        assert config["task_serializer"] == "json"
        assert config["result_serializer"] == "json"
        assert config["accept_content"] == ["json"]
        assert config["timezone"] == "UTC"
        assert config["enable_utc"] is True
        assert config["task_track_started"] is True
        assert config["task_acks_late"] is True
        assert config["worker_prefetch_multiplier"] == 1

    def test_custom_broker_url(self) -> None:
        with patch.dict(os.environ, {"STUDYOS_CELERY_BROKER_URL": "redis://custom:6379/5"}):
            from studyos_api.core.config import get_settings
            get_settings.cache_clear()
            config = _build_celery_config()
            assert config["broker_url"] == "redis://custom:6379/5"
            get_settings.cache_clear()

    def test_fallback_to_redis_url(self) -> None:
        with patch.dict(
            os.environ,
            {
                "STUDYOS_CELERY_BROKER_URL": "",
                "STUDYOS_REDIS_URL": "redis://fallback:6379/0",
            },
        ):
            from studyos_api.core.config import get_settings
            get_settings.cache_clear()
            config = _build_celery_config()
            assert config["broker_url"] == "redis://fallback:6379/0"
            get_settings.cache_clear()

    def test_task_routes(self) -> None:
        config = _build_celery_config()
        routes = config["task_routes"]
        assert "studyos_api.tasks.ai_tasks.*" in routes
        assert routes["studyos_api.tasks.ai_tasks.*"]["queue"] == "ai"
        assert "studyos_api.tasks.report_tasks.*" in routes
        assert routes["studyos_api.tasks.report_tasks.*"]["queue"] == "reports"
        assert "studyos_api.tasks.notification_tasks.*" in routes
        assert routes["studyos_api.tasks.notification_tasks.*"]["queue"] == "notifications"

    def test_beat_schedule(self) -> None:
        config = _build_celery_config()
        beat = config["beat_schedule"]
        assert "cleanup-expired-sessions" in beat
        assert "send-digest-emails" in beat
        assert beat["cleanup-expired-sessions"]["schedule"] == 3600.0
        assert beat["send-digest-emails"]["schedule"] == 86400.0

    def test_custom_retry_settings(self) -> None:
        with patch.dict(
            os.environ,
            {
                "STUDYOS_CELERY_TASK_DEFAULT_RETRY_DELAY": "120",
                "STUDYOS_CELERY_TASK_MAX_RETRIES": "5",
            },
        ):
            from studyos_api.core.config import get_settings
            get_settings.cache_clear()
            config = _build_celery_config()
            assert config["task_default_retry_delay"] == 120
            assert config["task_max_retries"] == 5
            get_settings.cache_clear()


class TestCeleryApp:
    def test_celery_app_name(self) -> None:
        assert celery_app.main == "studyos"

    def test_celery_app_configured(self) -> None:
        config = _build_celery_config()
        assert config["task_serializer"] == "json"
        assert config["result_serializer"] == "json"
        assert config["timezone"] == "UTC"
        assert config["enable_utc"] is True
