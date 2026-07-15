"""Progress endpoints — mark subtopics complete, get progress summaries."""

from typing import Annotated, Any
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Request

from studyos_api.controllers.progress_controller import ProgressController
from studyos_api.core.limiter import limiter
from studyos_api.deps.auth import User, get_current_user
from studyos_api.services.progress_service import ProgressService

router = APIRouter()


def get_db_pool(request: Request) -> asyncpg.Pool | None:
    """Get database pool from app state."""
    return request.app.state.db_pool


def get_progress_service(
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> ProgressService:
    """Create progress service with database pool."""
    return ProgressService(pool=pool)


def get_progress_controller(
    service: Annotated[ProgressService, Depends(get_progress_service)],
) -> ProgressController:
    """Create progress controller with service."""
    return ProgressController(service=service)


@router.post("/subtopics/{subtopic_id}/toggle")
@limiter.limit("120/minute")
async def toggle_subtopic_completion(
    request: Request,
    subtopic_id: UUID,
    controller: Annotated[ProgressController, Depends(get_progress_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Toggle subtopic completion for current user."""
    profile_id = UUID(current_user["sub"])
    return await controller.toggle_subtopic(request, profile_id, subtopic_id)


@router.get("/chapters/{chapter_id}")
@limiter.limit("60/minute")
async def get_chapter_progress(
    request: Request,
    chapter_id: UUID,
    controller: Annotated[ProgressController, Depends(get_progress_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get chapter progress for current user."""
    profile_id = UUID(current_user["sub"])
    return await controller.get_chapter_progress(request, profile_id, chapter_id)


@router.get("/subjects/{subject_id}")
@limiter.limit("60/minute")
async def get_subject_progress(
    request: Request,
    subject_id: UUID,
    controller: Annotated[ProgressController, Depends(get_progress_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get subject progress for current user."""
    profile_id = UUID(current_user["sub"])
    return await controller.get_subject_progress(request, profile_id, subject_id)


@router.get("/exams/{exam_id}")
@limiter.limit("60/minute")
async def get_exam_progress(
    request: Request,
    exam_id: UUID,
    controller: Annotated[ProgressController, Depends(get_progress_controller)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get exam progress for current user."""
    profile_id = UUID(current_user["sub"])
    return await controller.get_exam_progress(request, profile_id, exam_id)


@router.get("/streak")
@limiter.limit("60/minute")
async def get_streak(
    request: Request,
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get current user's study streak."""
    profile_id = UUID(current_user["sub"])

    if pool is None:
        return {"current_streak": 0, "longest_streak": 0, "last_study_date": None}

    row = await pool.fetchrow(
        """
        SELECT current_streak, longest_streak, last_study_date
        FROM public.streaks
        WHERE profile_id = $1 AND deleted_at IS NULL
        """,
        profile_id,
    )

    if row is None:
        return {"current_streak": 0, "longest_streak": 0, "last_study_date": None}

    return {
        "current_streak": row["current_streak"],
        "longest_streak": row["longest_streak"],
        "last_study_date": row["last_study_date"].isoformat() if row["last_study_date"] else None,
    }
