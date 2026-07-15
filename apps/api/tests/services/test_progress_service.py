"""Tests for progress_service."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from studyos_api.services.progress_service import ProgressService


def _make_mock_pool():
    """Create a mock asyncpg pool with acquire context manager."""
    mock_conn = AsyncMock()
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.execute = AsyncMock()

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_pool, mock_conn


class TestProgressServiceNoPool:
    """Test service behavior when pool is None."""

    def test_toggle_no_pool(self):
        service = ProgressService(pool=None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.toggle_subtopic_completion(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result == {}

    def test_chapter_progress_no_pool(self):
        service = ProgressService(pool=None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_chapter_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result == {}

    def test_subject_progress_no_pool(self):
        service = ProgressService(pool=None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_subject_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result == {}

    def test_exam_progress_no_pool(self):
        service = ProgressService(pool=None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_exam_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result == {}


class TestToggleSubtopicCompletion:
    """Test toggle_subtopic_completion with mocked DB."""

    def test_create_new_completion(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(side_effect=[
            None,  # No existing completion
            {"id": "new-id", "profile_id": "p1", "subtopic_id": "s1", "completed_at": "now", "created_at": "now"},
        ])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.toggle_subtopic_completion(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["id"] == "new-id"

    def test_soft_delete_existing_completion(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {"id": "existing-id", "deleted_at": None},  # Existing, not deleted
            {"id": "existing-id", "profile_id": "p1", "subtopic_id": "s1", "completed_at": "now", "deleted_at": "now"},
        ])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.toggle_subtopic_completion(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["id"] == "existing-id"
        assert result["deleted_at"] is not None

    def test_restore_soft_deleted_completion(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {"id": "existing-id", "deleted_at": "2024-01-01"},  # Existing, soft-deleted
            {"id": "existing-id", "profile_id": "p1", "subtopic_id": "s1", "completed_at": "now", "created_at": "now"},
        ])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.toggle_subtopic_completion(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["id"] == "existing-id"


class TestGetChapterProgress:
    """Test get_chapter_progress with mocked DB."""

    def test_chapter_progress_with_data(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {"total": 10},  # Total subtopics
            {"completed": 5},  # Completed subtopics
        ])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_chapter_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["total_subtopics"] == 10
        assert result["completed_subtopics"] == 5
        assert result["progress_pct"] == 50.0

    def test_chapter_progress_zero_total(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {"total": 0},
            {"completed": 0},
        ])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_chapter_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["progress_pct"] == 0

    def test_chapter_progress_no_rows(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetchrow = AsyncMock(side_effect=[None, None])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_chapter_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["total_subtopics"] == 0
        assert result["completed_subtopics"] == 0


class TestGetSubjectProgress:
    """Test get_subject_progress with mocked DB."""

    def test_subject_progress_with_chapters(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetch = AsyncMock(return_value=[
            {"id": "ch1", "name": "Chapter 1", "total_subtopics": 10, "completed_subtopics": 5},
            {"id": "ch2", "name": "Chapter 2", "total_subtopics": 8, "completed_subtopics": 8},
        ])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_subject_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["total_subtopics"] == 18
        assert result["completed_subtopics"] == 13
        assert len(result["chapters"]) == 2
        assert result["chapters"][0]["chapter_name"] == "Chapter 1"

    def test_subject_progress_empty(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetch = AsyncMock(return_value=[])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_subject_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["total_subtopics"] == 0
        assert result["progress_pct"] == 0
        assert result["chapters"] == []


class TestGetExamProgress:
    """Test get_exam_progress with mocked DB."""

    def test_exam_progress_with_subjects(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetch = AsyncMock(return_value=[
            {"id": "s1", "name": "Physics", "total_subtopics": 20, "completed_subtopics": 10},
            {"id": "s2", "name": "Chemistry", "total_subtopics": 15, "completed_subtopics": 15},
        ])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_exam_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["total_subtopics"] == 35
        assert result["completed_subtopics"] == 25
        assert len(result["subjects"]) == 2
        assert result["subjects"][0]["subject_name"] == "Physics"

    def test_exam_progress_empty(self):
        mock_pool, mock_conn = _make_mock_pool()
        mock_conn.fetch = AsyncMock(return_value=[])
        service = ProgressService(pool=mock_pool)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                service.get_exam_progress(uuid4(), uuid4())
            )
        finally:
            loop.close()
        assert result["total_subtopics"] == 0
        assert result["progress_pct"] == 0
        assert result["subjects"] == []
