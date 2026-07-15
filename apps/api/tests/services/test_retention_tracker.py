"""Tests for retention tracker service."""

import pytest

from studyos_api.services.retention_tracker import (
    ForgettingCurveModel,
    RetentionRecord,
    RetentionTracker,
)


class TestForgettingCurveModel:
    def test_predict_fresh_retention(self) -> None:
        model = ForgettingCurveModel()
        assert model.predict_retention(0) == 1.0

    def test_predict_decay(self) -> None:
        model = ForgettingCurveModel()
        r1 = model.predict_retention(1)
        r2 = model.predict_retention(3)
        r3 = model.predict_retention(7)
        assert 1.0 >= r1 >= r2 >= r3 >= 0.0
        assert r1 > r3

    def test_optimal_review_interval(self) -> None:
        model = ForgettingCurveModel(decay_rate=0.3)
        interval_80 = model.optimal_review_interval(target_retention=0.8)
        interval_50 = model.optimal_review_interval(target_retention=0.5)
        assert interval_50 > interval_80

    def test_optimal_interval_minimum(self) -> None:
        model = ForgettingCurveModel()
        interval = model.optimal_review_interval(target_retention=1.0)
        assert interval >= 1


class TestRetentionRecord:
    def test_to_dict(self) -> None:
        record = RetentionRecord(
            item_id="t1",
            days_since_review=3,
            predicted_retention=0.85,
            actual_retention=0.80,
            quality_score=4.0,
            timestamp="2026-05-19",
        )
        d = record.to_dict()
        assert d["item_id"] == "t1"
        assert d["days_since_review"] == 3


class TestRetentionTracker:
    @pytest.fixture
    def tracker(self) -> RetentionTracker:
        return RetentionTracker()

    def test_record_retention(self, tracker: RetentionTracker) -> None:
        record = tracker.record("t1", 3, 4.0, "2026-05-19")
        assert record.item_id == "t1"
        assert record.days_since_review == 3
        assert 0.0 <= record.predicted_retention <= 1.0
        assert record.actual_retention == 0.8

    def test_get_item_retention(self, tracker: RetentionTracker) -> None:
        tracker.record("t1", 1, 5.0)
        tracker.record("t1", 3, 4.0)
        tracker.record("t2", 2, 3.0)
        records = tracker.get_item_retention("t1")
        assert len(records) == 2

    def test_get_average_retention(self, tracker: RetentionTracker) -> None:
        tracker.record("t1", 3, 4.0)
        tracker.record("t2", 3, 3.0)
        avg = tracker.get_average_retention(3)
        assert avg == pytest.approx(0.7, abs=0.01)

    def test_get_average_retention_empty(self, tracker: RetentionTracker) -> None:
        assert tracker.get_average_retention(5) == 0.0

    def test_get_model_accuracy(self, tracker: RetentionTracker) -> None:
        tracker.record("t1", 1, 5.0)
        tracker.record("t2", 3, 4.0)
        accuracy = tracker.get_model_accuracy()
        assert 0.0 <= accuracy <= 1.0

    def test_get_model_accuracy_empty(self, tracker: RetentionTracker) -> None:
        assert tracker.get_model_accuracy() == 0.0

    def test_get_weak_items(self, tracker: RetentionTracker) -> None:
        tracker.record("strong", 1, 5.0)
        tracker.record("weak", 5, 1.0)
        weak = tracker.get_weak_items(threshold=0.5)
        assert "weak" in weak
        assert "strong" not in weak

    def test_get_retention_summary(self, tracker: RetentionTracker) -> None:
        tracker.record("t1", 1, 5.0)
        tracker.record("t2", 3, 3.0)
        summary = tracker.get_retention_summary()
        assert summary["total_records"] == 2
        assert summary["unique_items"] == 2
        assert "avg_actual_retention" in summary

    def test_get_retention_summary_empty(self, tracker: RetentionTracker) -> None:
        summary = tracker.get_retention_summary()
        assert summary["total_records"] == 0

    def test_reset(self, tracker: RetentionTracker) -> None:
        tracker.record("t1", 1, 5.0)
        tracker.reset()
        assert tracker.get_retention_summary()["total_records"] == 0
