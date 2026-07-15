"""Roadmap schemas for Phase 8 enterprise features."""

from datetime import date
from typing import Any

from pydantic import BaseModel


class PriorityScoreResponse(BaseModel):
    chapter_id: str
    chapter_name: str
    subject_name: str
    score: float
    weightage_factor: float
    weak_area_factor: float
    time_remaining_factor: float
    exam_proximity_factor: float
    computed_at: str | None = None


class PerformancePredictionResponse(BaseModel):
    predicted_score: float
    confidence_lower: float
    confidence_upper: float
    model_version: str
    prediction_date: str | None = None
    features: dict[str, Any] | None = None


class PredictionHistoryItem(BaseModel):
    predicted_score: float
    confidence_lower: float
    confidence_upper: float
    prediction_date: str
    model_version: str


class RecoveryPlanResponse(BaseModel):
    plan_id: str
    trigger_reason: str
    days_remaining: int
    revised_completion_date: str
    daily_hours_target: float
    accelerated_chapters: list[dict[str, Any]]
    skipped_chapters: list[dict[str, Any]]
    summary: dict[str, Any]


class ActiveRecoveryPlanResponse(BaseModel):
    plan_id: str
    trigger_reason: str
    original_completion_date: str | None
    revised_completion_date: str | None
    accelerated_chapters: list[dict[str, Any]]
    skipped_chapters: list[dict[str, Any]]
    daily_hours_target: float
    status: str
    created_at: str


class ExamOptimizationResponse(BaseModel):
    exam_date: str
    days_remaining: int
    phase: str
    subject_analysis: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    daily_target_hours: float
    weekly_milestones: list[dict[str, Any]]


class GenerateRoadmapRequest(BaseModel):
    exam_date: date | None = None
    target_score: float | None = None


class GenerateRecoveryRequest(BaseModel):
    exam_date: date
    trigger_reason: str = "behind_schedule"


class OptimizeExamRequest(BaseModel):
    exam_date: date
