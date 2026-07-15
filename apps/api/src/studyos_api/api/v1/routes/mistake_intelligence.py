"""Mistake Intelligence endpoints — track, analyze, predict, and cluster mistakes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request

from studyos_api.controllers.mistake_intelligence_controller import MistakeIntelligenceController
from studyos_api.core.limiter import limiter
from studyos_api.deps.auth import User, get_current_user

router = APIRouter()


def get_mistake_controller() -> MistakeIntelligenceController:
    """Create mistake intelligence controller with services."""
    return MistakeIntelligenceController()


@router.post("/mistakes")
@limiter.limit("60/minute")
async def log_mistake(
    request: Request,
    question_id: str,
    mistake_type: str,
    concept_tags: Annotated[list[str] | None, Query()] = None,
    confidence_level: float = 0.0,
    time_taken_seconds: float = 0.0,
    correct_answer: str = "",
    user_answer: str = "",
    timestamp: str = "",
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Log a new mistake."""
    profile_id = current_user["sub"]
    return await controller.log_mistake(
        request=request,
        profile_id=profile_id,
        question_id=question_id,
        mistake_type=mistake_type,
        concept_tags=concept_tags,
        confidence_level=confidence_level,
        time_taken_seconds=time_taken_seconds,
        correct_answer=correct_answer,
        user_answer=user_answer,
        timestamp=timestamp,
    )


@router.get("/mistakes")
@limiter.limit("60/minute")
async def get_user_mistakes(
    request: Request,
    mistake_type: str | None = None,
    concept: str | None = None,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get user's mistakes with optional filters."""
    profile_id = current_user["sub"]
    return await controller.get_user_mistakes(
        request=request,
        profile_id=profile_id,
        mistake_type=mistake_type,
        concept=concept,
    )


@router.get("/mistakes/stats")
@limiter.limit("30/minute")
async def get_mistake_stats(
    request: Request,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get mistake statistics for current user."""
    profile_id = current_user["sub"]
    return await controller.get_mistake_stats(request=request, profile_id=profile_id)


@router.get("/mistakes/gaps")
@limiter.limit("30/minute")
async def analyze_gaps(
    request: Request,
    min_attempts: int = 3,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Analyze knowledge gaps for current user."""
    profile_id = current_user["sub"]
    return await controller.analyze_gaps(
        request=request,
        profile_id=profile_id,
        min_attempts=min_attempts,
    )


@router.get("/mistakes/weak-concepts")
@limiter.limit("30/minute")
async def get_weak_concepts(
    request: Request,
    top_n: int = 5,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get top N weakest concepts."""
    profile_id = current_user["sub"]
    return await controller.get_weak_concepts(
        request=request,
        profile_id=profile_id,
        top_n=top_n,
    )


@router.get("/mistakes/mastery/{concept}")
@limiter.limit("30/minute")
async def get_mastery_level(
    request: Request,
    concept: str,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get mastery level for a specific concept."""
    profile_id = current_user["sub"]
    return await controller.get_mastery_level(
        request=request,
        profile_id=profile_id,
        concept=concept,
    )


@router.get("/mistakes/study-plan")
@limiter.limit("30/minute")
async def get_study_plan(
    request: Request,
    max_concepts: int = 5,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Generate a prioritized study plan."""
    profile_id = current_user["sub"]
    return await controller.get_study_plan(
        request=request,
        profile_id=profile_id,
        max_concepts=max_concepts,
    )


@router.get("/mistakes/predictions")
@limiter.limit("30/minute")
async def predict_mistakes(
    request: Request,
    concepts: list[str] | None = None,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Predict likely future mistakes."""
    profile_id = current_user["sub"]
    return await controller.predict_mistakes(
        request=request,
        profile_id=profile_id,
        concepts=concepts,
    )


@router.get("/mistakes/high-risk")
@limiter.limit("30/minute")
async def get_high_risk_concepts(
    request: Request,
    threshold: float = 0.7,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get concepts with high mistake probability."""
    profile_id = current_user["sub"]
    return await controller.get_high_risk_concepts(
        request=request,
        profile_id=profile_id,
        threshold=threshold,
    )


@router.get("/mistakes/trend/{concept}")
@limiter.limit("30/minute")
async def get_improvement_trend(
    request: Request,
    concept: str,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get improvement trend for a concept."""
    profile_id = current_user["sub"]
    return await controller.get_improvement_trend(
        request=request,
        profile_id=profile_id,
        concept=concept,
    )


@router.post("/mistakes/cluster")
@limiter.limit("20/minute")
async def cluster_mistakes(
    request: Request,
    min_cluster_size: int = 2,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Cluster mistakes by semantic similarity."""
    profile_id = current_user["sub"]
    return await controller.cluster_mistakes(
        request=request,
        profile_id=profile_id,
        min_cluster_size=min_cluster_size,
    )


@router.get("/mistakes/cluster/stats")
@limiter.limit("30/minute")
async def get_cluster_stats(
    request: Request,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get clustering statistics."""
    profile_id = current_user["sub"]
    return await controller.get_cluster_stats(
        request=request,
        profile_id=profile_id,
    )


@router.get("/mistakes/report")
@limiter.limit("10/minute")
async def get_full_intelligence_report(
    request: Request,
    controller: Annotated[MistakeIntelligenceController, Depends(get_mistake_controller)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get a comprehensive mistake intelligence report."""
    profile_id = current_user["sub"]
    return await controller.get_full_intelligence_report(
        request=request,
        profile_id=profile_id,
    )
