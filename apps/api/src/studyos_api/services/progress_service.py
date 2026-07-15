"""Progress tracking data access and orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)


class ProgressService:
    """Handle progress data queries and updates."""

    def __init__(self, *, pool: asyncpg.Pool | None) -> None:
        self._pool = pool

    async def toggle_subtopic_completion(
        self, profile_id: UUID, subtopic_id: UUID
    ) -> dict[str, Any]:
        """
        Toggle subtopic completion status.
        Returns the updated/created completion record.
        """
        if self._pool is None:
            return {}

        async with self._pool.acquire() as conn:
            # Check if already completed
            existing = await conn.fetchrow(
                """
                SELECT id, deleted_at
                FROM public.subtopic_completions
                WHERE profile_id = $1 AND subtopic_id = $2
                """,
                profile_id,
                subtopic_id,
            )

            if existing is None:
                # Create new completion
                row = await conn.fetchrow(
                    """
                    INSERT INTO public.subtopic_completions
                    (profile_id, subtopic_id, completed_at, source)
                    VALUES ($1, $2, now(), 'app')
                    RETURNING id, profile_id, subtopic_id, completed_at, created_at
                    """,
                    profile_id,
                    subtopic_id,
                )
                return dict(row) if row else {}
            elif existing["deleted_at"] is None:
                # Already completed, soft-delete to mark incomplete
                row = await conn.fetchrow(
                    """
                    UPDATE public.subtopic_completions
                    SET deleted_at = now(), updated_at = now()
                    WHERE id = $1
                    RETURNING id, profile_id, subtopic_id, completed_at, deleted_at
                    """,
                    existing["id"],
                )
                return dict(row) if row else {}
            else:
                # Was incomplete, restore
                row = await conn.fetchrow(
                    """
                    UPDATE public.subtopic_completions
                    SET deleted_at = NULL, updated_at = now()
                    WHERE id = $1
                    RETURNING id, profile_id, subtopic_id, completed_at, created_at
                    """,
                    existing["id"],
                )
                return dict(row) if row else {}

    async def get_chapter_progress(
        self, profile_id: UUID, chapter_id: UUID
    ) -> dict[str, Any]:
        """Get progress for a specific chapter (completion %, subtopics completed)."""
        if self._pool is None:
            return {}

        async with self._pool.acquire() as conn:
            # Get total subtopics in chapter
            total_row = await conn.fetchrow(
                """
                SELECT COUNT(*) as total
                FROM public.subtopics st
                INNER JOIN public.topics t ON st.topic_id = t.id
                WHERE t.chapter_id = $1 AND st.deleted_at IS NULL
                """,
                chapter_id,
            )

            # Get completed subtopics for this user in this chapter
            completed_row = await conn.fetchrow(
                """
                SELECT COUNT(*) as completed
                FROM public.subtopic_completions sc
                INNER JOIN public.subtopics st ON sc.subtopic_id = st.id
                INNER JOIN public.topics t ON st.topic_id = t.id
                WHERE t.chapter_id = $1 AND sc.profile_id = $2 AND sc.deleted_at IS NULL
                """,
                chapter_id,
                profile_id,
            )

            total = total_row["total"] if total_row else 0
            completed = completed_row["completed"] if completed_row else 0

            progress_pct = (
                (completed / total * 100) if total > 0 else 0
            )

            return {
                "chapter_id": str(chapter_id),
                "profile_id": str(profile_id),
                "total_subtopics": total,
                "completed_subtopics": completed,
                "progress_pct": round(progress_pct, 2),
            }

    async def get_subject_progress(
        self, profile_id: UUID, subject_id: UUID
    ) -> dict[str, Any]:
        """Get aggregated progress for a subject (completion %, chapters breakdown)."""
        if self._pool is None:
            return {}

        async with self._pool.acquire() as conn:
            # Get all chapters in subject with completion info
            chapters_rows = await conn.fetch(
                """
                SELECT
                  c.id,
                  c.name,
                  COUNT(DISTINCT st.id) as total_subtopics,
                  COUNT(DISTINCT CASE WHEN sc.id IS NOT NULL THEN st.id END) as completed_subtopics
                FROM public.chapters c
                LEFT JOIN public.topics t ON c.id = t.chapter_id AND t.deleted_at IS NULL
                LEFT JOIN public.subtopics st ON t.id = st.topic_id AND st.deleted_at IS NULL
                LEFT JOIN public.subtopic_completions sc ON
                  st.id = sc.subtopic_id AND sc.profile_id = $1 AND sc.deleted_at IS NULL
                WHERE c.subject_id = $2 AND c.deleted_at IS NULL
                GROUP BY c.id, c.name
                ORDER BY c.sort_order ASC
                """,
                profile_id,
                subject_id,
            )

            chapters = []
            total_subtopics = 0
            total_completed = 0

            for row in chapters_rows:
                total = row["total_subtopics"]
                completed = row["completed_subtopics"]
                total_subtopics += total
                total_completed += completed

                chapters.append({
                    "chapter_id": str(row["id"]),
                    "chapter_name": row["name"],
                    "total_subtopics": total,
                    "completed_subtopics": completed,
                    "progress_pct": round((completed / total * 100) if total > 0 else 0, 2),
                })

            overall_pct = (
                (total_completed / total_subtopics * 100)
                if total_subtopics > 0
                else 0
            )

            return {
                "subject_id": str(subject_id),
                "profile_id": str(profile_id),
                "total_subtopics": total_subtopics,
                "completed_subtopics": total_completed,
                "progress_pct": round(overall_pct, 2),
                "chapters": chapters,
            }

    async def get_exam_progress(
        self, profile_id: UUID, exam_id: UUID
    ) -> dict[str, Any]:
        """Get aggregated progress for entire exam (all subjects)."""
        if self._pool is None:
            return {}

        async with self._pool.acquire() as conn:
            # Get all subjects with completion info
            subjects_rows = await conn.fetch(
                """
                SELECT
                  s.id,
                  s.name,
                  COUNT(DISTINCT st.id) as total_subtopics,
                  COUNT(DISTINCT CASE WHEN sc.id IS NOT NULL THEN st.id END) as completed_subtopics
                FROM public.subjects s
                LEFT JOIN public.chapters c ON s.id = c.subject_id AND c.deleted_at IS NULL
                LEFT JOIN public.topics t ON c.id = t.chapter_id AND t.deleted_at IS NULL
                LEFT JOIN public.subtopics st ON t.id = st.topic_id AND st.deleted_at IS NULL
                LEFT JOIN public.subtopic_completions sc ON
                  st.id = sc.subtopic_id AND sc.profile_id = $1 AND sc.deleted_at IS NULL
                WHERE s.exam_profile_id = $2
                GROUP BY s.id, s.name
                ORDER BY s.sort_order ASC
                """,
                profile_id,
                exam_id,
            )

            subjects = []
            total_subtopics = 0
            total_completed = 0

            for row in subjects_rows:
                total = row["total_subtopics"]
                completed = row["completed_subtopics"]
                total_subtopics += total
                total_completed += completed

                subjects.append({
                    "subject_id": str(row["id"]),
                    "subject_name": row["name"],
                    "total_subtopics": total,
                    "completed_subtopics": completed,
                    "progress_pct": round((completed / total * 100) if total > 0 else 0, 2),
                })

            overall_pct = (
                (total_completed / total_subtopics * 100)
                if total_subtopics > 0
                else 0
            )

            return {
                "exam_id": str(exam_id),
                "profile_id": str(profile_id),
                "total_subtopics": total_subtopics,
                "completed_subtopics": total_completed,
                "progress_pct": round(overall_pct, 2),
                "subjects": subjects,
            }
