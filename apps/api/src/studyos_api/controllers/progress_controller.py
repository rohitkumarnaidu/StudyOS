"""HTTP orchestration for progress endpoints."""

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from starlette.requests import Request

from studyos_api.core.responses import response_meta
from studyos_api.services.progress_service import ProgressService


class ProgressController:
    """Map progress requests to service and format responses."""

    def __init__(self, service: ProgressService | None = None) -> None:
        self._service = service or ProgressService(pool=None)

    async def toggle_subtopic(
        self, request: Request, profile_id: UUID, subtopic_id: UUID
    ) -> dict[str, Any]:
        """Toggle subtopic completion status."""
        result = await self._service.toggle_subtopic_completion(profile_id, subtopic_id)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update subtopic completion",
            )

        return {
            "data": {
                "id": result.get("id"),
                "subtopic_id": str(result.get("subtopic_id")),
                "completed_at": result.get("completed_at"),
                "deleted_at": result.get("deleted_at"),
            },
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_chapter_progress(
        self, request: Request, profile_id: UUID, chapter_id: UUID
    ) -> dict[str, Any]:
        """Get chapter progress."""
        progress = await self._service.get_chapter_progress(profile_id, chapter_id)

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch chapter progress",
            )

        return {
            "data": progress,
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_subject_progress(
        self, request: Request, profile_id: UUID, subject_id: UUID
    ) -> dict[str, Any]:
        """Get subject progress."""
        progress = await self._service.get_subject_progress(profile_id, subject_id)

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch subject progress",
            )

        return {
            "data": progress,
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_exam_progress(
        self, request: Request, profile_id: UUID, exam_id: UUID
    ) -> dict[str, Any]:
        """Get exam progress."""
        progress = await self._service.get_exam_progress(profile_id, exam_id)

        if not progress:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch exam progress",
            )

        return {
            "data": progress,
            "meta": response_meta(request, api_version="v1"),
        }
