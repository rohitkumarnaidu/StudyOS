"""Roadmap endpoints — Phase 8 enterprise features."""

from datetime import date
from typing import Annotated, Any
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Request

from studyos_api.controllers.roadmap_controller import RoadmapController
from studyos_api.core.limiter import limiter
from studyos_api.deps.auth import User, get_current_user
from studyos_api.services.exam_optimizer import ExamOptimizer
from studyos_api.services.performance_predictor import PerformancePredictor
from studyos_api.services.priority_scorer import PriorityScorer
from studyos_api.services.recovery_planner import RecoveryPlanner

router = APIRouter()


def get_db_pool(request: Request) -> asyncpg.Pool | None:
    return request.app.state.db_pool


def get_priority_scorer(
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> PriorityScorer:
    return PriorityScorer(pool=pool)


def get_performance_predictor(
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> PerformancePredictor:
    return PerformancePredictor(pool=pool)


def get_recovery_planner(
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> RecoveryPlanner:
    return RecoveryPlanner(pool=pool)


def get_exam_optimizer(
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> ExamOptimizer:
    return ExamOptimizer(pool=pool)


def get_roadmap_controller(
    priority_scorer: Annotated[PriorityScorer, Depends(get_priority_scorer)],
    performance_predictor: Annotated[PerformancePredictor, Depends(get_performance_predictor)],
    recovery_planner: Annotated[RecoveryPlanner, Depends(get_recovery_planner)],
    exam_optimizer: Annotated[ExamOptimizer, Depends(get_exam_optimizer)],
) -> RoadmapController:
    return RoadmapController(
        priority_scorer=priority_scorer,
        performance_predictor=performance_predictor,
        recovery_planner=recovery_planner,
        exam_optimizer=exam_optimizer,
    )


@router.post("/generate")
@limiter.limit("30/minute")
async def generate_roadmap(
    request: Request,
    controller: Annotated[RoadmapController, Depends(get_roadmap_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
    exam_date: date | None = None,
) -> dict[str, Any]:
    """Generate new roadmap with priority scoring and performance prediction."""
    profile_id = UUID(current_user["sub"])
    return await controller.generate_roadmap(request, profile_id, exam_date)


@router.get("/priority-scores")
@limiter.limit("60/minute")
async def get_priority_scores(
    request: Request,
    controller: Annotated[RoadmapController, Depends(get_roadmap_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get all chapter priority scores."""
    profile_id = UUID(current_user["sub"])
    scores = await controller.get_priority_scores(profile_id)
    return {"scores": scores}


@router.get("/predict")
@limiter.limit("30/minute")
async def get_prediction(
    request: Request,
    controller: Annotated[RoadmapController, Depends(get_roadmap_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get performance prediction."""
    profile_id = UUID(current_user["sub"])
    prediction = await controller.get_prediction(profile_id)
    return {"prediction": prediction}


@router.get("/predictions/history")
@limiter.limit("30/minute")
async def get_prediction_history(
    request: Request,
    controller: Annotated[RoadmapController, Depends(get_roadmap_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
) -> dict[str, Any]:
    """Get prediction history."""
    profile_id = UUID(current_user["sub"])
    history = await controller.get_prediction_history(profile_id, limit)
    return {"history": history}


@router.post("/recovery")
@limiter.limit("10/minute")
async def generate_recovery_plan(
    request: Request,
    controller: Annotated[RoadmapController, Depends(get_roadmap_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
    exam_date: date,
    trigger_reason: str = "behind_schedule",
) -> dict[str, Any]:
    """Generate recovery plan for struggling students."""
    profile_id = UUID(current_user["sub"])
    plan = await controller.generate_recovery_plan(profile_id, exam_date, trigger_reason)
    return {"plan": plan}


@router.get("/recovery/active")
@limiter.limit("30/minute")
async def get_active_recovery_plan(
    request: Request,
    controller: Annotated[RoadmapController, Depends(get_roadmap_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get active recovery plan."""
    profile_id = UUID(current_user["sub"])
    plan = await controller.get_active_recovery_plan(profile_id)
    return {"plan": plan} if plan else {"plan": None}


@router.post("/optimize")
@limiter.limit("10/minute")
async def optimize_for_exam(
    request: Request,
    controller: Annotated[RoadmapController, Depends(get_roadmap_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
    exam_date: date,
) -> dict[str, Any]:
    """Optimize study plan for exam date."""
    profile_id = UUID(current_user["sub"])
    optimization = await controller.optimize_for_exam(profile_id, exam_date)
    return {"optimization": optimization}
