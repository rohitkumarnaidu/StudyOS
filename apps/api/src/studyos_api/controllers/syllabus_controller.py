"""HTTP orchestration for syllabus endpoints."""

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from starlette.requests import Request

from studyos_api.core.responses import response_meta
from studyos_api.services.syllabus_service import SyllabusService


class SyllabusController:
    """Map syllabus requests to service and format responses."""

    def __init__(self, service: SyllabusService | None = None) -> None:
        self._service = service or SyllabusService(pool=None)

    async def list_exams(self, request: Request) -> dict[str, Any]:
        """List all exams."""
        exams = await self._service.list_exams()
        return {
            "data": [
                {
                    "id": exam["id"],
                    "code": exam["code"],
                    "title": exam["title"],
                    "description": exam.get("description"),
                }
                for exam in exams
            ],
            "meta": response_meta(request, api_version="v1"),
        }

    async def list_chapters(
        self,
        request: Request,
        exam_id: UUID | None = None,
        subject_id: UUID | None = None,
    ) -> dict[str, Any]:
        """List chapters, optionally filtered."""
        chapters = await self._service.list_chapters(exam_id=exam_id, subject_id=subject_id)
        return {
            "data": [
                {
                    "id": chapter["id"],
                    "name": chapter["name"],
                    "sort_order": chapter["sort_order"],
                }
                for chapter in chapters
            ],
            "meta": response_meta(request, api_version="v1"),
        }

    async def get_chapter_detail(self, request: Request, chapter_id: UUID) -> dict[str, Any]:
        """Get chapter with topics and subtopics."""
        chapter = await self._service.get_chapter_with_topics(chapter_id)

        if chapter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found",
            )

        return {
            "data": {
                "id": chapter["id"],
                "name": chapter["name"],
                "sort_order": chapter["sort_order"],
                "topics": [
                    {
                        "id": topic["id"],
                        "name": topic["name"],
                        "sort_order": topic["sort_order"],
                        "subtopics": [
                            {
                                "id": subtopic["id"],
                                "name": subtopic["name"],
                                "sort_order": subtopic["sort_order"],
                                "estimated_minutes": subtopic.get("estimated_minutes"),
                            }
                            for subtopic in topic.get("subtopics", [])
                        ],
                    }
                    for topic in chapter.get("topics", [])
                ],
            },
            "meta": response_meta(request, api_version="v1"),
        }
