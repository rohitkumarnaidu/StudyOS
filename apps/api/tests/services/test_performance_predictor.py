"""Tests for performance_predictor service."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from studyos_api.services.performance_predictor import PerformancePredictor


class MockAsyncpgRow(dict):
    """Mock asyncpg Row that supports dict-like access."""

    def __getitem__(self, key: str) -> object:
        return dict.get(self, key)


class MockAsyncContextManager:
    """Mock async context manager for pool.acquire()."""

    def __init__(self, conn: AsyncMock) -> None:
        self._conn = conn

    async def __aenter__(self) -> AsyncMock:
        return self._conn

    async def __aexit__(self, *args: object) -> None:
        pass


class TestPerformancePredictorInit:
    def test_init_with_pool(self) -> None:
        pool = AsyncMock()
        pred = PerformancePredictor(pool=pool)
        assert pred._pool is pool

    def test_init_without_pool(self) -> None:
        pred = PerformancePredictor(pool=None)
        assert pred._pool is None


class TestPerformancePredictorPredictScore:
    @pytest.mark.asyncio
    async def test_returns_defaults_when_no_pool(self) -> None:
        pred = PerformancePredictor(pool=None)
        result = await pred.predict_score(uuid4())
        assert result["predicted_score"] == 0
        assert result["confidence_lower"] == 0
        assert result["confidence_upper"] == 0
        assert result["model_version"] == "v1"

    @pytest.mark.asyncio
    async def test_predict_score_success(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": 100, "completed_subtopics": 50}),
            MockAsyncpgRow({"total_questions": 200, "avg_accuracy": 0.7}),
            MockAsyncpgRow({"current_streak": 10, "longest_streak": 25}),
        ]
        conn.execute.return_value = None

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        pred = PerformancePredictor(pool=pool)
        result = await pred.predict_score(uuid4())

        assert "predicted_score" in result
        assert "confidence_lower" in result
        assert "confidence_upper" in result
        assert result["model_version"] == "v1"
        assert "prediction_date" in result
        assert "features" in result

    @pytest.mark.asyncio
    async def test_predict_score_clamps_to_range(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": 1000, "completed_subtopics": 1000}),
            MockAsyncpgRow({"total_questions": 5000, "avg_accuracy": 1.0}),
            MockAsyncpgRow({"current_streak": 100, "longest_streak": 200}),
        ]
        conn.execute.return_value = None

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        pred = PerformancePredictor(pool=pool)
        result = await pred.predict_score(uuid4())

        assert result["predicted_score"] <= 720
        assert result["confidence_upper"] <= 720
        assert result["confidence_lower"] >= 0

    @pytest.mark.asyncio
    async def test_predict_score_low_performance(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": 100, "completed_subtopics": 0}),
            MockAsyncpgRow({"total_questions": 5, "avg_accuracy": 0.1}),
            MockAsyncpgRow({"current_streak": 0, "longest_streak": 0}),
        ]
        conn.execute.return_value = None

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        pred = PerformancePredictor(pool=pool)
        result = await pred.predict_score(uuid4())

        assert result["predicted_score"] >= 200
        assert result["confidence_lower"] >= 0

    @pytest.mark.asyncio
    async def test_predict_score_features_structure(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": 100, "completed_subtopics": 50}),
            MockAsyncpgRow({"total_questions": 200, "avg_accuracy": 0.7}),
            MockAsyncpgRow({"current_streak": 10, "longest_streak": 25}),
        ]
        conn.execute.return_value = None

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        pred = PerformancePredictor(pool=pool)
        result = await pred.predict_score(uuid4())

        features = result["features"]
        assert "completion_rate" in features
        assert "total_subtopics" in features
        assert "completed_subtopics" in features
        assert "avg_accuracy" in features
        assert "total_questions_attempted" in features
        assert "current_streak" in features
        assert "longest_streak" in features

    @pytest.mark.asyncio
    async def test_predict_score_confidence_interval(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": 100, "completed_subtopics": 50}),
            MockAsyncpgRow({"total_questions": 200, "avg_accuracy": 0.7}),
            MockAsyncpgRow({"current_streak": 10, "longest_streak": 25}),
        ]
        conn.execute.return_value = None

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        pred = PerformancePredictor(pool=pool)
        result = await pred.predict_score(uuid4())

        assert result["confidence_lower"] <= result["predicted_score"]
        assert result["confidence_upper"] >= result["predicted_score"]


class TestPerformancePredictorGetPredictions:
    @pytest.mark.asyncio
    async def test_returns_empty_when_no_pool(self) -> None:
        pred = PerformancePredictor(pool=None)
        result = await pred.get_predictions(uuid4())
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_predictions(self) -> None:
        conn = AsyncMock()
        today = date.today()
        rows = [
            MockAsyncpgRow({
                "predicted_score": 520.0,
                "confidence_interval_lower": 480.0,
                "confidence_interval_upper": 560.0,
                "prediction_date": today,
                "model_version": "v1",
            }),
            MockAsyncpgRow({
                "predicted_score": 500.0,
                "confidence_interval_lower": 450.0,
                "confidence_interval_upper": 550.0,
                "prediction_date": today,
                "model_version": "v1",
            }),
        ]
        conn.fetch.return_value = rows

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        pred = PerformancePredictor(pool=pool)
        result = await pred.get_predictions(uuid4(), limit=10)

        assert len(result) == 2
        assert result[0]["predicted_score"] == 520.0
        assert result[0]["model_version"] == "v1"

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_rows(self) -> None:
        conn = AsyncMock()
        conn.fetch.return_value = []

        pool = MagicMock()
        pool.acquire = MagicMock(return_value=MockAsyncContextManager(conn))

        pred = PerformancePredictor(pool=pool)
        result = await pred.get_predictions(uuid4())

        assert result == []


class TestPerformancePredictorComputeFeatures:
    @pytest.mark.asyncio
    async def test_compute_features_structure(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": 200, "completed_subtopics": 100}),
            MockAsyncpgRow({"total_questions": 500, "avg_accuracy": 0.65}),
            MockAsyncpgRow({"current_streak": 15, "longest_streak": 30}),
        ]

        pred = PerformancePredictor(pool=None)
        features = await pred._compute_features(conn, uuid4())

        assert features["completion_rate"] == 0.5
        assert features["total_subtopics"] == 200
        assert features["completed_subtopics"] == 100
        assert features["avg_accuracy"] == 0.65
        assert features["total_questions_attempted"] == 500
        assert features["current_streak"] == 15
        assert features["longest_streak"] == 30

    @pytest.mark.asyncio
    async def test_compute_features_null_values(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": None, "completed_subtopics": None}),
            MockAsyncpgRow({"total_questions": None, "avg_accuracy": None}),
            None,
        ]

        pred = PerformancePredictor(pool=None)
        features = await pred._compute_features(conn, uuid4())

        assert features["completion_rate"] == 0.0
        assert features["total_subtopics"] == 0
        assert features["avg_accuracy"] == 0.0
        assert features["current_streak"] == 0
        assert features["longest_streak"] == 0

    @pytest.mark.asyncio
    async def test_compute_features_zero_total(self) -> None:
        conn = AsyncMock()
        conn.fetchrow.side_effect = [
            MockAsyncpgRow({"total_subtopics": 0, "completed_subtopics": 0}),
            MockAsyncpgRow({"total_questions": 0, "avg_accuracy": 0.0}),
            MockAsyncpgRow({"current_streak": 0, "longest_streak": 0}),
        ]

        pred = PerformancePredictor(pool=None)
        features = await pred._compute_features(conn, uuid4())

        assert features["completion_rate"] == 0.0
        assert features["avg_accuracy"] == 0.0


class TestPerformancePredictorComputePrediction:
    def test_base_score_with_no_progress(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "completion_rate": 0.0,
            "avg_accuracy": 0.0,
            "current_streak": 0,
        }
        score = pred._compute_prediction(features)
        assert score == 350.0

    def test_full_progress_max_score(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "completion_rate": 1.0,
            "avg_accuracy": 1.0,
            "current_streak": 100,
        }
        score = pred._compute_prediction(features)
        assert score == 700.0
        assert score <= 720.0

    def test_clamped_minimum(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "completion_rate": 0.0,
            "avg_accuracy": 0.0,
            "current_streak": 0,
        }
        score = pred._compute_prediction(features)
        assert score >= 200

    def test_streak_bonus_capped(self) -> None:
        pred = PerformancePredictor(pool=None)
        features_low = {
            "completion_rate": 0.0,
            "avg_accuracy": 0.0,
            "current_streak": 10,
        }
        features_high = {
            "completion_rate": 0.0,
            "avg_accuracy": 0.0,
            "current_streak": 100,
        }
        score_low = pred._compute_prediction(features_low)
        score_high = pred._compute_prediction(features_high)
        assert score_high - score_low <= 30.0

    def test_completion_contribution(self) -> None:
        pred = PerformancePredictor(pool=None)
        features_half = {
            "completion_rate": 0.5,
            "avg_accuracy": 0.0,
            "current_streak": 0,
        }
        features_full = {
            "completion_rate": 1.0,
            "avg_accuracy": 0.0,
            "current_streak": 0,
        }
        score_half = pred._compute_prediction(features_half)
        score_full = pred._compute_prediction(features_full)
        assert abs((score_full - score_half) - 100.0) < 0.01

    def test_accuracy_contribution(self) -> None:
        pred = PerformancePredictor(pool=None)
        features_half = {
            "completion_rate": 0.0,
            "avg_accuracy": 0.5,
            "current_streak": 0,
        }
        features_full = {
            "completion_rate": 0.0,
            "avg_accuracy": 1.0,
            "current_streak": 0,
        }
        score_half = pred._compute_prediction(features_half)
        score_full = pred._compute_prediction(features_full)
        assert abs((score_full - score_half) - 60.0) < 0.01


class TestPerformancePredictorComputeConfidenceMargin:
    def test_high_confidence_narrow_margin(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "total_questions_attempted": 500,
            "completion_rate": 1.0,
        }
        margin = pred._compute_confidence_margin(features)
        assert margin < 50.0

    def test_low_confidence_wide_margin(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "total_questions_attempted": 0,
            "completion_rate": 0.0,
        }
        margin = pred._compute_confidence_margin(features)
        assert margin > 80.0

    def test_minimum_margin(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "total_questions_attempted": 1000,
            "completion_rate": 1.0,
        }
        margin = pred._compute_confidence_margin(features)
        assert margin >= 20.0

    def test_medium_confidence(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "total_questions_attempted": 50,
            "completion_rate": 0.5,
        }
        margin = pred._compute_confidence_margin(features)
        assert 20.0 <= margin <= 100.0

    def test_rounded_to_2_decimals(self) -> None:
        pred = PerformancePredictor(pool=None)
        features = {
            "total_questions_attempted": 37,
            "completion_rate": 0.43,
        }
        margin = pred._compute_confidence_margin(features)
        assert len(str(margin).split(".")[-1]) <= 2

    def test_data_confidence_weight(self) -> None:
        pred = PerformancePredictor(pool=None)
        features_high_data = {
            "total_questions_attempted": 200,
            "completion_rate": 0.0,
        }
        features_low_data = {
            "total_questions_attempted": 10,
            "completion_rate": 0.0,
        }
        margin_high = pred._compute_confidence_margin(features_high_data)
        margin_low = pred._compute_confidence_margin(features_low_data)
        assert margin_high < margin_low

    def test_coverage_confidence_weight(self) -> None:
        pred = PerformancePredictor(pool=None)
        features_high_cov = {
            "total_questions_attempted": 0,
            "completion_rate": 1.0,
        }
        features_low_cov = {
            "total_questions_attempted": 0,
            "completion_rate": 0.0,
        }
        margin_high = pred._compute_confidence_margin(features_high_cov)
        margin_low = pred._compute_confidence_margin(features_low_cov)
        assert margin_high < margin_low
