"""HTTP orchestration for mistake intelligence endpoints."""

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from starlette.requests import Request

from studyos_api.core.responses import response_meta
from studyos_api.services.concept_gap_analyzer import ConceptGapAnalyzer
from studyos_api.services.mistake_predictor import MistakePredictor
from studyos_api.services.mistake_tracker import MistakeTracker, MistakeType
from studyos_api.services.semantic_clusterer import SemanticClusterer


class MistakeIntelligenceController:
    """Map mistake intelligence requests to services and format responses."""

    def __init__(
        self,
        tracker: MistakeTracker | None = None,
        gap_analyzer: ConceptGapAnalyzer | None = None,
        predictor: MistakePredictor | None = None,
        clusterer: SemanticClusterer | None = None,
    ) -> None:
        self._tracker = tracker or MistakeTracker()
        self._gap_analyzer = gap_analyzer or ConceptGapAnalyzer()
        self._predictor = predictor or MistakePredictor()
        self._clusterer = clusterer or SemanticClusterer()

    async def log_mistake(
        self,
        request: Request,
        profile_id: UUID,
        question_id: str,
        mistake_type: str,
        concept_tags: list[str] | None = None,
        confidence_level: float = 0.0,
        time_taken_seconds: float = 0.0,
        correct_answer: str = "",
        user_answer: str = "",
        timestamp: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Log a new mistake."""
        try:
            mtype = MistakeType(mistake_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid mistake type: {mistake_type}. Must be one of: {[t.value for t in MistakeType]}",
            )

        import uuid as _uuid

        mistake_id = str(_uuid.uuid4())

        record = self._tracker.log_mistake(
            mistake_id=mistake_id,
            profile_id=str(profile_id),
            question_id=question_id,
            mistake_type=mtype,
            concept_tags=concept_tags or [],
            confidence_level=confidence_level,
            time_taken_seconds=time_taken_seconds,
            correct_answer=correct_answer,
            user_answer=user_answer,
            timestamp=timestamp,
            metadata=metadata or {},
        )

        return {
            "data": record.to_dict(),
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_user_mistakes(
        self,
        request: Request,
        profile_id: UUID,
        mistake_type: str | None = None,
        concept: str | None = None,
    ) -> dict[str, Any]:
        """Get user's mistakes with optional filters."""
        if mistake_type:
            try:
                mtype = MistakeType(mistake_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid mistake type: {mistake_type}",
                )
            mistakes = self._tracker.get_mistakes_by_type(str(profile_id), mtype)
        elif concept:
            mistakes = self._tracker.get_mistakes_by_concept(str(profile_id), concept)
        else:
            mistakes = self._tracker.get_user_mistakes(str(profile_id))

        return {
            "data": {
                "mistakes": [m.to_dict() for m in mistakes],
                "total": len(mistakes),
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_mistake_stats(
        self,
        request: Request,
        profile_id: UUID,
    ) -> dict[str, Any]:
        """Get mistake statistics for a user."""
        stats = self._tracker.get_mistake_stats(str(profile_id))
        return {
            "data": stats,
            "meta": response_meta(request, api_version="v1"),
        }

    async def analyze_gaps(
        self,
        request: Request,
        profile_id: UUID,
        min_attempts: int = 3,
    ) -> dict[str, Any]:
        """Analyze knowledge gaps for a user."""
        gaps = self._gap_analyzer.analyze_gaps(min_attempts=min_attempts)
        return {
            "data": {
                "gaps": [g.to_dict() for g in gaps],
                "total": len(gaps),
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_weak_concepts(
        self,
        request: Request,
        profile_id: UUID,
        top_n: int = 5,
    ) -> dict[str, Any]:
        """Get top N weakest concepts."""
        weak = self._gap_analyzer.get_weak_concepts(top_n=top_n)
        return {
            "data": {
                "weak_concepts": [g.to_dict() for g in weak],
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_mastery_level(
        self,
        request: Request,
        profile_id: UUID,
        concept: str,
    ) -> dict[str, Any]:
        """Get mastery level for a specific concept."""
        level = self._gap_analyzer.get_mastery_level(concept)
        return {
            "data": {
                "concept": concept,
                "mastery_level": level,
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_study_plan(
        self,
        request: Request,
        profile_id: UUID,
        max_concepts: int = 5,
    ) -> dict[str, Any]:
        """Generate a prioritized study plan."""
        plan = self._gap_analyzer.get_study_plan(max_concepts=max_concepts)
        return {
            "data": {"study_plan": plan},
            "meta": response_meta(request, api_version="v1"),
        }

    async def predict_mistakes(
        self,
        request: Request,
        profile_id: UUID,
        concepts: list[str] | None = None,
    ) -> dict[str, Any]:
        """Predict likely future mistakes."""
        predictions = self._predictor.get_predictions(concepts=concepts)
        return {
            "data": {
                "predictions": [p.to_dict() for p in predictions],
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_high_risk_concepts(
        self,
        request: Request,
        profile_id: UUID,
        threshold: float = 0.7,
    ) -> dict[str, Any]:
        """Get concepts with high mistake probability."""
        high_risk = self._predictor.get_high_risk_concepts(threshold=threshold)
        return {
            "data": {
                "high_risk_concepts": high_risk,
                "threshold": threshold,
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_improvement_trend(
        self,
        request: Request,
        profile_id: UUID,
        concept: str,
    ) -> dict[str, Any]:
        """Get improvement trend for a concept."""
        trend = self._predictor.get_improvement_trend(concept)
        return {
            "data": {
                "concept": concept,
                "trend": trend,
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def cluster_mistakes(
        self,
        request: Request,
        profile_id: UUID,
        min_cluster_size: int = 2,
    ) -> dict[str, Any]:
        """Cluster mistakes by semantic similarity."""
        clusters = self._clusterer.cluster(min_cluster_size=min_cluster_size)
        return {
            "data": {
                "clusters": [c.to_dict() for c in clusters],
                "stats": self._clusterer.get_cluster_stats(),
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_cluster_stats(
        self,
        request: Request,
        profile_id: UUID,
    ) -> dict[str, Any]:
        """Get clustering statistics."""
        stats = self._clusterer.get_cluster_stats()
        return {
            "data": stats,
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_full_intelligence_report(
        self,
        request: Request,
        profile_id: UUID,
    ) -> dict[str, Any]:
        """Get a comprehensive mistake intelligence report."""
        mistake_stats = self._tracker.get_mistake_stats(str(profile_id))
        gaps = self._gap_analyzer.analyze_gaps(min_attempts=1)
        predictions = self._predictor.get_predictions()
        clusters = self._clusterer.cluster(min_cluster_size=1)
        study_plan = self._gap_analyzer.get_study_plan(max_concepts=5)

        return {
            "data": {
                "mistake_stats": mistake_stats,
                "knowledge_gaps": [g.to_dict() for g in gaps],
                "predictions": [p.to_dict() for p in predictions[:5]],
                "clusters": [c.to_dict() for c in clusters[:5]],
                "study_plan": study_plan,
            },
            "meta": response_meta(request, api_version="v1"),
        }
