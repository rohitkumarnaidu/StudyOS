"""Roadmap controller — orchestrates Phase 8 enterprise roadmap features."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog

if TYPE_CHECKING:
    from fastapi import Request

    from studyos_api.services.exam_optimizer import ExamOptimizer
    from studyos_api.services.performance_predictor import PerformancePredictor
    from studyos_api.services.priority_scorer import PriorityScorer
    from studyos_api.services.recovery_planner import RecoveryPlanner

logger = structlog.get_logger(__name__)


class RoadmapController:
    """Handle roadmap feature requests and orchestrate services."""

    def __init__(
        self,
        *,
        priority_scorer: PriorityScorer,
        performance_predictor: PerformancePredictor,
        recovery_planner: RecoveryPlanner,
        exam_optimizer: ExamOptimizer,
    ) -> None:
        self._priority_scorer = priority_scorer
        self._performance_predictor = performance_predictor
        self._recovery_planner = recovery_planner
        self._exam_optimizer = exam_optimizer

    async def generate_roadmap(
        self,
        request: Request,
        profile_id: UUID,
        exam_date: date | None = None,
    ) -> dict[str, Any]:
        """Generate a new roadmap with priority scoring."""
        logger.info("roadmap.generate", profile_id=str(profile_id))

        scores = await self._priority_scorer.compute_all_scores(profile_id, exam_date)
        prediction = await self._performance_predictor.predict_score(profile_id)

        return {
            "priority_scores": scores,
            "prediction": prediction,
            "generated_at": date.today().isoformat(),
        }

    async def get_priority_scores(self, profile_id: UUID) -> list[dict[str, Any]]:
        """Get current priority scores."""
        return await self._priority_scorer.get_scores(profile_id)

    async def get_prediction(self, profile_id: UUID) -> dict[str, Any]:
        """Get latest performance prediction."""
        return await self._performance_predictor.predict_score(profile_id)

    async def get_prediction_history(
        self,
        profile_id: UUID,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get prediction history."""
        return await self._performance_predictor.get_predictions(profile_id, limit)

    async def generate_recovery_plan(
        self,
        profile_id: UUID,
        exam_date: date,
        trigger_reason: str = "behind_schedule",
    ) -> dict[str, Any]:
        """Generate a recovery plan."""
        return await self._recovery_planner.generate_recovery_plan(
            profile_id, None, exam_date, trigger_reason
        )

    async def get_active_recovery_plan(self, profile_id: UUID) -> dict[str, Any] | None:
        """Get active recovery plan."""
        return await self._recovery_planner.get_active_plan(profile_id)

    async def optimize_for_exam(
        self,
        profile_id: UUID,
        exam_date: date,
    ) -> dict[str, Any]:
        """Optimize study plan for exam date."""
        return await self._exam_optimizer.optimize_plan(profile_id, exam_date)
