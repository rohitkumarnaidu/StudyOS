"""Tests for roadmap schemas."""

from datetime import date

import pytest
from pydantic import ValidationError

from studyos_api.schemas.roadmap import (
    ActiveRecoveryPlanResponse,
    ExamOptimizationResponse,
    GenerateRecoveryRequest,
    GenerateRoadmapRequest,
    OptimizeExamRequest,
    PerformancePredictionResponse,
    PredictionHistoryItem,
    PriorityScoreResponse,
    RecoveryPlanResponse,
)


@pytest.mark.unit
class TestPriorityScoreResponse:
    def test_valid_priority_score(self) -> None:
        resp = PriorityScoreResponse(
            chapter_id="ch-1",
            chapter_name="Biology",
            subject_name="Science",
            score=0.85,
            weightage_factor=0.3,
            weak_area_factor=0.2,
            time_remaining_factor=0.15,
            exam_proximity_factor=0.2,
        )
        assert resp.chapter_id == "ch-1"
        assert resp.score == 0.85
        assert resp.computed_at is None

    def test_with_computed_at(self) -> None:
        resp = PriorityScoreResponse(
            chapter_id="ch-2",
            chapter_name="Physics",
            subject_name="Science",
            score=0.7,
            weightage_factor=0.25,
            weak_area_factor=0.25,
            time_remaining_factor=0.2,
            exam_proximity_factor=0.3,
            computed_at="2024-01-15T10:00:00Z",
        )
        assert resp.computed_at == "2024-01-15T10:00:00Z"

    def test_serialization(self) -> None:
        resp = PriorityScoreResponse(
            chapter_id="ch-3",
            chapter_name="Chemistry",
            subject_name="Science",
            score=0.9,
            weightage_factor=0.4,
            weak_area_factor=0.1,
            time_remaining_factor=0.2,
            exam_proximity_factor=0.3,
        )
        data = resp.model_dump()
        assert data["chapter_id"] == "ch-3"
        assert data["score"] == 0.9


@pytest.mark.unit
class TestPerformancePredictionResponse:
    def test_valid_prediction(self) -> None:
        resp = PerformancePredictionResponse(
            predicted_score=72.5,
            confidence_lower=68.0,
            confidence_upper=77.0,
            model_version="v2.1",
        )
        assert resp.predicted_score == 72.5
        assert resp.prediction_date is None
        assert resp.features is None

    def test_with_features(self) -> None:
        resp = PerformancePredictionResponse(
            predicted_score=80.0,
            confidence_lower=75.0,
            confidence_upper=85.0,
            model_version="v3.0",
            prediction_date="2024-06-01",
            features={"study_hours": 120, "completion_rate": 0.85},
        )
        assert resp.features is not None
        assert resp.features["study_hours"] == 120

    def test_serialization(self) -> None:
        resp = PerformancePredictionResponse(
            predicted_score=65.0,
            confidence_lower=60.0,
            confidence_upper=70.0,
            model_version="v1.0",
        )
        data = resp.model_dump()
        assert data["predicted_score"] == 65.0


@pytest.mark.unit
class TestPredictionHistoryItem:
    def test_valid_history_item(self) -> None:
        item = PredictionHistoryItem(
            predicted_score=70.0,
            confidence_lower=65.0,
            confidence_upper=75.0,
            prediction_date="2024-01-01",
            model_version="v1.0",
        )
        assert item.predicted_score == 70.0
        assert item.prediction_date == "2024-01-01"

    def test_missing_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            PredictionHistoryItem(
                predicted_score=70.0,
                confidence_lower=65.0,
                confidence_upper=75.0,
            )


@pytest.mark.unit
class TestRecoveryPlanResponse:
    def test_valid_recovery_plan(self) -> None:
        resp = RecoveryPlanResponse(
            plan_id="plan-1",
            trigger_reason="behind_schedule",
            days_remaining=30,
            revised_completion_date="2024-07-01",
            daily_hours_target=4.5,
            accelerated_chapters=[{"id": "ch-1", "name": "Biology"}],
            skipped_chapters=[{"id": "ch-2", "name": "Art"}],
            summary={"total_chapters": 20, "accelerated": 5},
        )
        assert resp.plan_id == "plan-1"
        assert len(resp.accelerated_chapters) == 1
        assert len(resp.skipped_chapters) == 1

    def test_empty_lists(self) -> None:
        resp = RecoveryPlanResponse(
            plan_id="plan-2",
            trigger_reason="exam_date_changed",
            days_remaining=15,
            revised_completion_date="2024-06-15",
            daily_hours_target=6.0,
            accelerated_chapters=[],
            skipped_chapters=[],
            summary={},
        )
        assert resp.accelerated_chapters == []


@pytest.mark.unit
class TestActiveRecoveryPlanResponse:
    def test_valid_active_plan(self) -> None:
        resp = ActiveRecoveryPlanResponse(
            plan_id="active-1",
            trigger_reason="behind_schedule",
            original_completion_date="2024-08-01",
            revised_completion_date="2024-07-15",
            accelerated_chapters=[{"id": "ch-1"}],
            skipped_chapters=[],
            daily_hours_target=5.0,
            status="active",
            created_at="2024-01-01T00:00:00Z",
        )
        assert resp.status == "active"
        assert resp.original_completion_date == "2024-08-01"

    def test_nullable_dates(self) -> None:
        resp = ActiveRecoveryPlanResponse(
            plan_id="active-2",
            trigger_reason="new_plan",
            original_completion_date=None,
            revised_completion_date=None,
            accelerated_chapters=[],
            skipped_chapters=[],
            daily_hours_target=3.0,
            status="draft",
            created_at="2024-01-01",
        )
        assert resp.original_completion_date is None


@pytest.mark.unit
class TestExamOptimizationResponse:
    def test_valid_optimization(self) -> None:
        resp = ExamOptimizationResponse(
            exam_date="2024-09-01",
            days_remaining=60,
            phase="revision",
            subject_analysis=[{"name": "Biology", "score": 75.0}],
            recommendations=[{"action": "focus_on_weak_areas"}],
            daily_target_hours=4.0,
            weekly_milestones=[{"week": 1, "target": "complete_chapter_1"}],
        )
        assert resp.phase == "revision"
        assert resp.daily_target_hours == 4.0


@pytest.mark.unit
class TestGenerateRoadmapRequest:
    def test_with_all_fields(self) -> None:
        req = GenerateRoadmapRequest(
            exam_date=date(2024, 9, 1),
            target_score=85.0,
        )
        assert req.exam_date == date(2024, 9, 1)
        assert req.target_score == 85.0

    def test_all_optional(self) -> None:
        req = GenerateRoadmapRequest()
        assert req.exam_date is None
        assert req.target_score is None

    def test_only_exam_date(self) -> None:
        req = GenerateRoadmapRequest(exam_date=date(2024, 12, 1))
        assert req.exam_date == date(2024, 12, 1)
        assert req.target_score is None


@pytest.mark.unit
class TestGenerateRecoveryRequest:
    def test_valid_recovery_request(self) -> None:
        req = GenerateRecoveryRequest(
            exam_date=date(2024, 8, 1),
            trigger_reason="behind_schedule",
        )
        assert req.exam_date == date(2024, 8, 1)
        assert req.trigger_reason == "behind_schedule"

    def test_default_trigger_reason(self) -> None:
        req = GenerateRecoveryRequest(exam_date=date(2024, 7, 1))
        assert req.trigger_reason == "behind_schedule"

    def test_missing_exam_date(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRecoveryRequest()


@pytest.mark.unit
class TestOptimizeExamRequest:
    def test_valid_optimize_request(self) -> None:
        req = OptimizeExamRequest(exam_date=date(2024, 10, 1))
        assert req.exam_date == date(2024, 10, 1)

    def test_missing_exam_date(self) -> None:
        with pytest.raises(ValidationError):
            OptimizeExamRequest()
