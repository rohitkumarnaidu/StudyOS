"""Syllabus endpoints — exams, chapters, topics, subtopics."""

from typing import Annotated, Any
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Request

from studyos_api.controllers.syllabus_controller import SyllabusController
from studyos_api.core.limiter import limiter
from studyos_api.services.syllabus_service import SyllabusService

router = APIRouter()


def get_db_pool(request: Request) -> asyncpg.Pool | None:
    """Get database pool from app state."""
    return request.app.state.db_pool


def get_syllabus_service(
    pool: Annotated[asyncpg.Pool | None, Depends(get_db_pool)],
) -> SyllabusService:
    """Create syllabus service with database pool."""
    return SyllabusService(pool=pool)


def get_syllabus_controller(
    service: Annotated[SyllabusService, Depends(get_syllabus_service)],
) -> SyllabusController:
    """Create syllabus controller with service."""
    return SyllabusController(service=service)


@router.get(
    "/exams",
    summary="List all exams",
    description="Returns all available exam profiles (e.g., NEET 2026, JEE Main 2026).",
    responses={
        200: {
            "description": "List of exams",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "code": "NEET_2026",
                                "title": "NEET 2026",
                                "description": "National Eligibility cum Entrance Test",
                            }
                        ]
                    }
                }
            },
        }
    },
)
@limiter.limit("60/minute")
async def list_exams(
    request: Request,
    controller: Annotated[SyllabusController, Depends(get_syllabus_controller)],
) -> dict[str, Any]:
    """List all available exams (e.g., NEET 2026)."""
    return await controller.list_exams(request)


@router.get(
    "/chapters",
    summary="List chapters",
    description="List chapters, optionally filtered by exam or subject ID.",
    responses={
        200: {
            "description": "List of chapters",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440001",
                                "name": "Mechanics",
                                "sort_order": 1,
                            }
                        ]
                    }
                }
            },
        }
    },
)
@limiter.limit("60/minute")
async def list_chapters(
    request: Request,
    controller: Annotated[SyllabusController, Depends(get_syllabus_controller)],
    exam_id: UUID | None = None,
    subject_id: UUID | None = None,
) -> dict[str, Any]:
    """List chapters, optionally filtered by exam or subject."""
    return await controller.list_chapters(request, exam_id=exam_id, subject_id=subject_id)


@router.get(
    "/chapters/{chapter_id}",
    summary="Get chapter detail",
    description="Get a chapter with all its topics and subtopics.",
    responses={
        200: {
            "description": "Chapter with topics and subtopics",
        },
        404: {"description": "Chapter not found"},
    },
)
@limiter.limit("60/minute")
async def get_chapter_detail(
    request: Request,
    chapter_id: UUID,
    controller: Annotated[SyllabusController, Depends(get_syllabus_controller)],
) -> dict[str, Any]:
    """Get chapter with all topics and subtopics."""
    return await controller.get_chapter_detail(request, chapter_id)
