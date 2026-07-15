"""Tests for Phase 8 roadmap services."""

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest

from studyos_api.services.exam_optimizer import ExamOptimizer
from studyos_api.services.performance_predictor import PerformancePredictor
from studyos_api.services.priority_scorer import PriorityScorer
from studyos_api.services.recovery_planner import RecoveryPlanner


@pytest.fixture
def mock_pool():
    pool = MagicMock()
    pool.acquire = AsyncMock()
    return pool


@pytest.fixture
def mock_conn():
    conn = MagicMock()
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchrow = AsyncMock(return_value=None)
    conn.execute = AsyncMock()
    return conn


class TestPriorityScorer:
    def test_init_with_pool(self, mock_pool):
        scorer = PriorityScorer(pool=mock_pool)
        assert scorer._pool is mock_pool

    def test_init_without_pool(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._pool is None

    @pytest.mark.asyncio
    async def test_compute_all_scores_no_pool(self):
        scorer = PriorityScorer(pool=None)
        result = await scorer.compute_all_scores(uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_get_scores_no_pool(self):
        scorer = PriorityScorer(pool=None)
        result = await scorer.get_scores(uuid4())
        assert result == []

    def test_weightage_factor_high(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._compute_weightage_factor(10.0) == 1.0
        assert scorer._compute_weightage_factor(15.0) == 1.0

    def test_weightage_factor_low(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._compute_weightage_factor(3.0) == 0.3

    def test_weak_area_factor_strong(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._compute_weak_area_factor(0.9, 0.8) == 0.2

    def test_weak_area_factor_moderate(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._compute_weak_area_factor(0.6, 0.6) == 0.5

    def test_weak_area_factor_weak(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._compute_weak_area_factor(0.2, 0.3) == 1.0

    def test_exam_proximity_critical(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._compute_exam_proximity_factor(15) == 1.0

    def test_exam_proximity_far(self):
        scorer = PriorityScorer(pool=None)
        assert scorer._compute_exam_proximity_factor(180) == 0.4


class TestPerformancePredictor:
    def test_init_with_pool(self, mock_pool):
        predictor = PerformancePredictor(pool=mock_pool)
        assert predictor._pool is mock_pool

    @pytest.mark.asyncio
    async def test_predict_score_no_pool(self):
        predictor = PerformancePredictor(pool=None)
        result = await predictor.predict_score(uuid4())
        assert result["predicted_score"] == 0
        assert result["model_version"] == "v1"

    @pytest.mark.asyncio
    async def test_get_predictions_no_pool(self):
        predictor = PerformancePredictor(pool=None)
        result = await predictor.get_predictions(uuid4())
        assert result == []

    def test_prediction_bounds(self):
        predictor = PerformancePredictor(pool=None)
        features = {
            "completion_rate": 1.0,
            "avg_accuracy": 1.0,
            "current_streak": 100,
            "total_questions_attempted": 500,
        }
        score = predictor._compute_prediction(features)
        assert 200 <= score <= 720

    def test_prediction_low_performance(self):
        predictor = PerformancePredictor(pool=None)
        features = {
            "completion_rate": 0.0,
            "avg_accuracy": 0.0,
            "current_streak": 0,
            "total_questions_attempted": 0,
        }
        score = predictor._compute_prediction(features)
        assert score == 350.0

    def test_confidence_margin_high_data(self):
        predictor = PerformancePredictor(pool=None)
        features = {
            "completion_rate": 0.9,
            "total_questions_attempted": 200,
        }
        margin = predictor._compute_confidence_margin(features)
        assert margin < 50

    def test_confidence_margin_low_data(self):
        predictor = PerformancePredictor(pool=None)
        features = {
            "completion_rate": 0.1,
            "total_questions_attempted": 5,
        }
        margin = predictor._compute_confidence_margin(features)
        assert margin > 60


class TestRecoveryPlanner:
    def test_init_with_pool(self, mock_pool):
        planner = RecoveryPlanner(pool=mock_pool)
        assert planner._pool is mock_pool

    @pytest.mark.asyncio
    async def test_generate_recovery_no_pool(self):
        planner = RecoveryPlanner(pool=None)
        result = await planner.generate_recovery_plan(uuid4(), None, date.today() + timedelta(days=90))
        assert "error" in result

    @pytest.mark.asyncio
    async def test_generate_recovery_exam_passed(self, mock_pool):
        planner = RecoveryPlanner(pool=mock_pool)
        past_date = date.today() - timedelta(days=1)
        result = await planner.generate_recovery_plan(uuid4(), None, past_date)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_active_plan_no_pool(self):
        planner = RecoveryPlanner(pool=None)
        result = await planner.get_active_plan(uuid4())
        assert result is None


class TestExamOptimizer:
    def test_init_with_pool(self, mock_pool):
        optimizer = ExamOptimizer(pool=mock_pool)
        assert optimizer._pool is mock_pool

    @pytest.mark.asyncio
    async def test_optimize_no_pool(self):
        optimizer = ExamOptimizer(pool=None)
        result = await optimizer.optimize_plan(uuid4(), date.today() + timedelta(days=90))
        assert "error" in result

    @pytest.mark.asyncio
    async def test_optimize_exam_passed(self, mock_pool):
        optimizer = ExamOptimizer(pool=mock_pool)
        past_date = date.today() - timedelta(days=1)
        result = await optimizer.optimize_plan(uuid4(), past_date)
        assert "error" in result

    def test_phase_crash(self):
        optimizer = ExamOptimizer(pool=None)
        assert optimizer._determine_phase(15) == "crash"

    def test_phase_intensive(self):
        optimizer = ExamOptimizer(pool=None)
        assert optimizer._determine_phase(45) == "intensive"

    def test_phase_focused(self):
        optimizer = ExamOptimizer(pool=None)
        assert optimizer._determine_phase(75) == "focused"

    def test_phase_foundational(self):
        optimizer = ExamOptimizer(pool=None)
        assert optimizer._determine_phase(180) == "foundational"

    def test_daily_hours_crash(self):
        optimizer = ExamOptimizer(pool=None)
        hours = optimizer._compute_daily_hours("crash", [])
        assert hours == 12.0

    def test_daily_hours_foundational_low_progress(self):
        optimizer = ExamOptimizer(pool=None)
        subjects = [{"completion_rate": 0.2}]
        hours = optimizer._compute_daily_hours("foundational", subjects)
        assert hours == 8.0

    def test_week_focus_crash(self):
        optimizer = ExamOptimizer(pool=None)
        focus = optimizer._get_week_focus("crash", 1, [])
        assert "Revision" in focus

    def test_weekly_milestones_positive(self):
        optimizer = ExamOptimizer(pool=None)
        subjects = [{"total_chapters": 10, "completion_rate": 0.3, "subject_name": "Physics"}]
        milestones = optimizer._compute_weekly_milestones("focused", 60, subjects)
        assert len(milestones) > 0
        assert milestones[0]["week"] == 1
