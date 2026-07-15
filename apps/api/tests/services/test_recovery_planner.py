"""Tests for recovery_planner service."""

import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from studyos_api.services.recovery_planner import RecoveryPlanner


def _make_mock_pool():
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.execute = AsyncMock()

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_pool, mock_conn


class TestRecoveryPlannerNoPool:
    """Test service behavior when pool is None."""

    def test_generate_plan_no_pool(self):
        planner = RecoveryPlanner(pool=None)
        future_date = date.today() + timedelta(days=180)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                planner.generate_recovery_plan(uuid4(), None, future_date)
            )
        finally:
            loop.close()
        assert result == {"error": "Database not available"}

    def test_get_active_plan_no_pool(self):
        planner = RecoveryPlanner(pool=None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(planner.get_active_plan(uuid4()))
        finally:
            loop.close()
        assert result is None


class TestRecoveryPlannerWithMockDB:
    """Test recovery planner with mocked DB."""

    def test_generate_plan_exam_passed(self):
        mock_pool, _ = _make_mock_pool()
        planner = RecoveryPlanner(pool=mock_pool)
        past_date = date.today() - timedelta(days=10)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                planner.generate_recovery_plan(uuid4(), None, past_date)
            )
        finally:
            loop.close()
        assert result == {"error": "Exam date has passed"}

    def test_generate_plan_empty_chapters(self):
        from datetime import datetime
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetch = AsyncMock(return_value=[])
        mock_conn.fetchrow = AsyncMock(return_value={"id": uuid4(), "created_at": datetime.now()})
        planner = RecoveryPlanner(pool=mock_pool)
        future_date = date.today() + timedelta(days=180)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                planner.generate_recovery_plan(uuid4(), None, future_date)
            )
        finally:
            loop.close()
        assert "plan_id" in result
        assert result["days_remaining"] == 180
        assert result["accelerated_chapters"] == []
        assert result["skipped_chapters"] == []

    def test_get_active_plan_empty(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        planner = RecoveryPlanner(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(planner.get_active_plan(uuid4()))
        finally:
            loop.close()
        assert result is None

    def test_get_active_plan_found(self):
        from datetime import datetime
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": uuid4(),
            "trigger_reason": "behind_schedule",
            "original_completion_date": date.today() + timedelta(days=180),
            "revised_completion_date": date.today() + timedelta(days=120),
            "accelerated_chapters": [{"chapter_id": "ch1"}],
            "skipped_chapters": [],
            "daily_hours_target": 10.0,
            "status": "active",
            "created_at": datetime(2024, 1, 1),
        })
        planner = RecoveryPlanner(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(planner.get_active_plan(uuid4()))
        finally:
            loop.close()
        assert result is not None
        assert result["plan_id"] is not None
        assert result["status"] == "active"
        assert result["daily_hours_target"] == 10.0
