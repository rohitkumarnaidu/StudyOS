"""Syllabus data access and orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)


class SyllabusService:
    """Handle syllabus data queries."""

    def __init__(self, *, pool: asyncpg.Pool | None) -> None:
        self._pool = pool

    async def list_exams(self) -> list[dict[str, Any]]:
        """Get all exams (NEET, JEE, etc.)."""
        if self._pool is None:
            return []

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, code, title, description
                FROM public.exam_profiles
                WHERE deleted_at IS NULL
                ORDER BY created_at ASC
                """
            )
        return [dict(row) for row in rows]

    async def list_subjects(self, exam_id: UUID) -> list[dict[str, Any]]:
        """Get all subjects for an exam."""
        if self._pool is None:
            return []

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, name, sort_order
                FROM public.subjects
                WHERE exam_profile_id = $1 AND deleted_at IS NULL
                ORDER BY sort_order ASC
                """,
                exam_id,
            )
        return [dict(row) for row in rows]

    async def list_chapters(
        self, exam_id: UUID | None = None, subject_id: UUID | None = None
    ) -> list[dict[str, Any]]:
        """Get chapters, optionally filtered by exam or subject."""
        if self._pool is None:
            return []

        if subject_id is not None:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, name, sort_order
                    FROM public.chapters
                    WHERE subject_id = $1 AND deleted_at IS NULL
                    ORDER BY sort_order ASC
                    """,
                    subject_id,
                )
            return [dict(row) for row in rows]

        if exam_id is not None:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT c.id, c.name, c.sort_order
                    FROM public.chapters c
                    INNER JOIN public.subjects s ON c.subject_id = s.id
                    WHERE s.exam_profile_id = $1 AND c.deleted_at IS NULL
                    ORDER BY s.sort_order, c.sort_order ASC
                    """,
                    exam_id,
                )
            return [dict(row) for row in rows]

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, name, sort_order
                FROM public.chapters
                WHERE deleted_at IS NULL
                ORDER BY sort_order ASC
                """
            )
        return [dict(row) for row in rows]

    async def get_chapter_with_topics(self, chapter_id: UUID) -> dict[str, Any] | None:
        """Get chapter with all topics and subtopics."""
        if self._pool is None:
            return None

        async with self._pool.acquire() as conn:
            chapter_row = await conn.fetchrow(
                """
                SELECT id, name, sort_order
                FROM public.chapters
                WHERE id = $1 AND deleted_at IS NULL
                """,
                chapter_id,
            )

            if chapter_row is None:
                return None

            topics_rows = await conn.fetch(
                """
                SELECT id, name, sort_order
                FROM public.topics
                WHERE chapter_id = $1 AND deleted_at IS NULL
                ORDER BY sort_order ASC
                """,
                chapter_id,
            )

            chapter = dict(chapter_row)
            topics = []

            for topic_row in topics_rows:
                topic = dict(topic_row)
                subtopics_rows = await conn.fetch(
                    """
                    SELECT id, name, sort_order, estimated_minutes
                    FROM public.subtopics
                    WHERE topic_id = $1 AND deleted_at IS NULL
                    ORDER BY sort_order ASC
                    """,
                    topic["id"],
                )
                topic["subtopics"] = [dict(row) for row in subtopics_rows]
                topics.append(topic)

            chapter["topics"] = topics
            return chapter
