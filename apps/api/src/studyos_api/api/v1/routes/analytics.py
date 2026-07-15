"""Analytics API endpoints — overview, daily progress, subjects, quiz trends, weak areas."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request

from studyos_api.core.limiter import limiter
from studyos_api.core.responses import response_meta
from studyos_api.deps.auth import User, get_current_user

router = APIRouter()


@router.get("/overview")
@limiter.limit("30/minute")
async def get_analytics_overview(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get overall analytics overview for the current user."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_overview(current_user["sub"])
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/daily")
@limiter.limit("30/minute")
async def get_daily_progress(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get daily progress for the last N days."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_daily_progress(current_user["sub"], days=days)
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/subjects")
@limiter.limit("30/minute")
async def get_subject_progress(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get per-subject completion breakdown."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_subject_progress(current_user["sub"])
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/quiz-trends")
@limiter.limit("30/minute")
async def get_quiz_trends(
    request: Request,
    days: int = Query(30, ge=1, le=365),
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get quiz score trends over the last N days."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_quiz_trends(current_user["sub"], days=days)
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/weak-areas")
@limiter.limit("30/minute")
async def get_weak_areas(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get chapters with low completion or poor quiz performance."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_weak_areas(current_user["sub"])
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/heatmap")
@limiter.limit("30/minute")
async def get_heatmap(
    request: Request,
    days: int = Query(90, ge=1, le=365),
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get study activity heatmap data."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_heatmap_data(current_user["sub"], days=days)
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/streak-calendar")
@limiter.limit("30/minute")
async def get_streak_calendar(
    request: Request,
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get streak calendar data for a given month."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_streak_calendar(current_user["sub"], month=month)
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/prediction")
@limiter.limit("30/minute")
async def get_performance_prediction(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get performance prediction and recommendations."""
    from studyos_api.services import analytics_service as svc

    data = svc.get_performance_prediction(current_user["sub"])
    return {
        "data": data,
        "meta": response_meta(request, api_version="v1"),
    }
