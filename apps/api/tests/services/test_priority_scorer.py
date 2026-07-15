"""Tests for priority_scorer service."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from studyos_api.services.priority_scorer import PriorityScorer


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


class TestPriorityScorerNoPool:
    """Test service behavior when pool is None."""

    @pytest.fixture
    def scorer(self):
        return PriorityScorer(pool=None)

    def test_compute_all_scores_no_pool(self, scorer):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(scorer.compute_all_scores(uuid4()))
        finally:
            loop.close()
        assert result == []

    def test_get_scores_no_pool(self, scorer):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(scorer.get_scores(uuid4()))
        finally:
            loop.close()
        assert result == []


class TestPriorityScorerComputation:
    """Test pure computation methods without DB."""

    @pytest.fixture
    def scorer(self):
        return PriorityScorer(pool=None)

    def test_compute_weightage_factor_low(self, scorer):
        assert scorer._compute_weightage_factor(2.0) == pytest.approx(0.2)

    def test_compute_weightage_factor_medium(self, scorer):
        assert scorer._compute_weightage_factor(5.0) == pytest.approx(0.5)

    def test_compute_weightage_factor_high(self, scorer):
        assert scorer._compute_weightage_factor(10.0) == pytest.approx(1.0)

    def test_compute_weightage_factor_capped(self, scorer):
        assert scorer._compute_weightage_factor(15.0) == pytest.approx(1.0)

    def test_compute_weak_area_factor_strong(self, scorer):
        assert scorer._compute_weak_area_factor(0.9, 0.8) == pytest.approx(0.2)

    def test_compute_weak_area_factor_moderate(self, scorer):
        assert scorer._compute_weak_area_factor(0.6, 0.6) == pytest.approx(0.5)

    def test_compute_weak_area_factor_weak_completion(self, scorer):
        assert scorer._compute_weak_area_factor(0.2, 0.5) == pytest.approx(1.0)

    def test_compute_weak_area_factor_weak_quiz(self, scorer):
        assert scorer._compute_weak_area_factor(0.5, 0.3) == pytest.approx(1.0)

    def test_compute_weak_area_factor_middle(self, scorer):
        assert scorer._compute_weak_area_factor(0.4, 0.45) == pytest.approx(0.7)

    def test_compute_time_factor_complete(self, scorer):
        assert scorer._compute_time_factor(0.95, 30) == pytest.approx(0.1)

    def test_compute_time_factor_urgent(self, scorer):
        result = scorer._compute_time_factor(0.2, 10)
        assert 0.0 <= result <= 1.0

    def test_compute_time_factor_moderate(self, scorer):
        result = scorer._compute_time_factor(0.5, 180)
        assert 0.0 <= result <= 1.0

    def test_compute_exam_proximity_factor_very_close(self, scorer):
        assert scorer._compute_exam_proximity_factor(15) == pytest.approx(1.0)

    def test_compute_exam_proximity_factor_close(self, scorer):
        assert scorer._compute_exam_proximity_factor(45) == pytest.approx(0.8)

    def test_compute_exam_proximity_factor_medium(self, scorer):
        assert scorer._compute_exam_proximity_factor(75) == pytest.approx(0.6)

    def test_compute_exam_proximity_factor_far(self, scorer):
        assert scorer._compute_exam_proximity_factor(120) == pytest.approx(0.4)


class TestPriorityScorerWithMockDB:
    """Test priority scorer with mocked DB."""

    @pytest.fixture
    def scorer(self):
        mock_pool, mock_conn = _make_mock_pool()
        return PriorityScorer(pool=mock_pool), mock_conn

    def test_compute_all_scores_empty_chapters(self, scorer):
        svc, mock_conn = scorer
        mock_conn.fetch = AsyncMock(return_value=[])
        exam_date = date.today().replace(year=date.today().year + 1)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(svc.compute_all_scores(uuid4(), exam_date=exam_date))
        finally:
            loop.close()
        assert result == []

    def test_compute_all_scores_with_chapters(self, scorer):
        svc, mock_conn = scorer
        mock_conn.fetch = AsyncMock(return_value=[
            {"id": "ch1", "name": "Chapter 1", "weightage": 8.0, "sort_order": 1, "subject_name": "Physics"},
            {"id": "ch2", "name": "Chapter 2", "weightage": 5.0, "sort_order": 2, "subject_name": "Chemistry"},
        ])
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {"total": 10, "completed": 2},  # ch1 progress
            None,  # ch1 quiz avg
            {"total": 8, "completed": 6},   # ch2 progress
            None,  # ch2 quiz avg
        ])
        mock_conn.execute = AsyncMock()
        exam_date = date.today().replace(year=date.today().year + 1)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(svc.compute_all_scores(uuid4(), exam_date=exam_date))
        finally:
            loop.close()
        assert len(result) == 2
        assert "score" in result[0]
        assert "weightage_factor" in result[0]
        assert "weak_area_factor" in result[0]
        assert result[0]["score"] >= result[1]["score"]  # Sorted by score desc

    def test_get_scores_empty(self, scorer):
        svc, mock_conn = scorer
        mock_conn.fetch = AsyncMock(return_value=[])

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(svc.get_scores(uuid4()))
        finally:
            loop.close()
        assert result == []

    def test_get_scores_with_data(self, scorer):
        svc, mock_conn = scorer
        from datetime import datetime
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "chapter_id": uuid4(),
                "chapter_name": "Chapter 1",
                "subject_name": "Physics",
                "score": 85.5,
                "weightage_factor": 0.8,
                "weak_area_factor": 0.7,
                "time_remaining_factor": 0.6,
                "exam_proximity_factor": 0.5,
                "computed_at": datetime(2024, 1, 1),
            },
        ])

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(svc.get_scores(uuid4()))
        finally:
            loop.close()
        assert len(result) == 1
        assert result[0]["chapter_name"] == "Chapter 1"
        assert result[0]["score"] == 85.5
