"""Priority scoring service — computes dynamic priority scores per chapter."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)


class PriorityScorer:
    """Compute dynamic priority scores for chapters based on multiple factors."""

    def __init__(self, *, pool: asyncpg.Pool | None) -> None:
        self._pool = pool

    async def compute_all_scores(
        self,
        profile_id: UUID,
        exam_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Compute priority scores for all chapters for a user."""
        if self._pool is None:
            return []

        today = date.today()
        days_to_exam = (exam_date - today).days if exam_date else 180
        days_to_exam = max(days_to_exam, 1)

        async with self._pool.acquire() as conn:
            chapters = await conn.fetch(
                """
                SELECT c.id, c.name, c.weightage, c.sort_order,
                       s.name as subject_name
                FROM public.chapters c
                JOIN public.subjects s ON c.subject_id = s.id
                WHERE c.deleted_at IS NULL AND s.deleted_at IS NULL
                ORDER BY c.sort_order
                """
            )

            scores = []
            for chapter in chapters:
                chapter_id = chapter["id"]
                weightage = float(chapter["weightage"] or 1.0)

                progress = await self._get_chapter_progress(conn, profile_id, chapter_id)
                completion_rate = progress["completion_rate"]

                quiz_avg = await self._get_chapter_quiz_avg(conn, profile_id, chapter_id)

                weightage_factor = self._compute_weightage_factor(weightage)
                weak_area_factor = self._compute_weak_area_factor(completion_rate, quiz_avg)
                time_factor = self._compute_time_factor(completion_rate, days_to_exam)
                exam_proximity_factor = self._compute_exam_proximity_factor(days_to_exam)

                score = (
                    weightage_factor * 0.25
                    + weak_area_factor * 0.35
                    + time_factor * 0.25
                    + exam_proximity_factor * 0.15
                ) * 100

                score = min(max(score, 0), 100)

                await conn.execute(
                    """
                    INSERT INTO public.priority_scores
                        (profile_id, chapter_id, score, weightage_factor,
                         time_remaining_factor, weak_area_factor,
                         exam_proximity_factor, computed_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, now())
                    ON CONFLICT (profile_id, chapter_id)
                    DO UPDATE SET
                        score = EXCLUDED.score,
                        weightage_factor = EXCLUDED.weightage_factor,
                        time_remaining_factor = EXCLUDED.time_remaining_factor,
                        weak_area_factor = EXCLUDED.weak_area_factor,
                        exam_proximity_factor = EXCLUDED.exam_proximity_factor,
                        computed_at = now()
                    """,
                    profile_id,
                    chapter_id,
                    round(score, 2),
                    round(weightage_factor, 2),
                    round(time_factor, 2),
                    round(weak_area_factor, 2),
                    round(exam_proximity_factor, 2),
                )

                scores.append(
                    {
                        "chapter_id": str(chapter_id),
                        "chapter_name": chapter["name"],
                        "subject_name": chapter["subject_name"],
                        "score": round(score, 2),
                        "weightage_factor": round(weightage_factor, 2),
                        "weak_area_factor": round(weak_area_factor, 2),
                        "time_remaining_factor": round(time_factor, 2),
                        "exam_proximity_factor": round(exam_proximity_factor, 2),
                        "completion_rate": completion_rate,
                        "quiz_avg": quiz_avg,
                    }
                )

            scores.sort(key=lambda x: x["score"], reverse=True)
            return scores

    async def get_scores(self, profile_id: UUID) -> list[dict[str, Any]]:
        """Get current priority scores for a user."""
        if self._pool is None:
            return []

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT ps.*, c.name as chapter_name, s.name as subject_name
                FROM public.priority_scores ps
                JOIN public.chapters c ON ps.chapter_id = c.id
                JOIN public.subjects s ON c.subject_id = s.id
                WHERE ps.profile_id = $1 AND c.deleted_at IS NULL
                ORDER BY ps.score DESC
                """,
                profile_id,
            )

            return [
                {
                    "chapter_id": str(row["chapter_id"]),
                    "chapter_name": row["chapter_name"],
                    "subject_name": row["subject_name"],
                    "score": float(row["score"]),
                    "weightage_factor": float(row["weightage_factor"]),
                    "weak_area_factor": float(row["weak_area_factor"]),
                    "time_remaining_factor": float(row["time_remaining_factor"]),
                    "exam_proximity_factor": float(row["exam_proximity_factor"]),
                    "computed_at": row["computed_at"].isoformat(),
                }
                for row in rows
            ]

    def _compute_weightage_factor(self, weightage: float) -> float:
        return min(weightage / 10.0, 1.0)

    def _compute_weak_area_factor(self, completion_rate: float, quiz_avg: float) -> float:
        if completion_rate >= 0.8 and quiz_avg >= 0.7:
            return 0.2
        if completion_rate >= 0.5 and quiz_avg >= 0.5:
            return 0.5
        if completion_rate < 0.3 or quiz_avg < 0.4:
            return 1.0
        return 0.7

    def _compute_time_factor(self, completion_rate: float, days_to_exam: float) -> float:
        if completion_rate >= 0.9:
            return 0.1
        chapters_remaining = 1.0 - completion_rate
        daily_capacity = 1.0 / max(days_to_exam, 1)
        if chapters_remaining > daily_capacity * 30:
            return 1.0
        if chapters_remaining > daily_capacity * 14:
            return 0.7
        return 0.4

    def _compute_exam_proximity_factor(self, days_to_exam: int) -> float:
        if days_to_exam <= 30:
            return 1.0
        if days_to_exam <= 60:
            return 0.8
        if days_to_exam <= 90:
            return 0.6
        return 0.4

    async def _get_chapter_progress(
        self,
        conn: asyncpg.Connection,
        profile_id: UUID,
        chapter_id: UUID,
    ) -> dict[str, float]:
        row = await conn.fetchrow(
            """
            SELECT
                COUNT(DISTINCT st.id) as total,
                COUNT(DISTINCT CASE WHEN sc.id IS NOT NULL THEN st.id END) as completed
            FROM public.subtopics st
            JOIN public.topics t ON st.topic_id = t.id
            LEFT JOIN public.subtopic_completions sc
                ON st.id = sc.subtopic_id AND sc.profile_id = $1 AND sc.deleted_at IS NULL
            WHERE t.chapter_id = $2 AND st.deleted_at IS NULL AND t.deleted_at IS NULL
            """,
            profile_id,
            chapter_id,
        )

        total = row["total"] if row and row["total"] else 0
        completed = row["completed"] if row and row["completed"] else 0
        completion_rate = completed / total if total > 0 else 0.0

        return {"total": total, "completed": completed, "completion_rate": completion_rate}

    async def _get_chapter_quiz_avg(
        self,
        conn: asyncpg.Connection,
        profile_id: UUID,
        chapter_id: UUID,
    ) -> float:
        row = await conn.fetchrow(
            """
            SELECT AVG(
                CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END
            ) as avg_score
            FROM public.quiz_responses qr
            JOIN public.questions q ON qr.question_id = q.id
            JOIN public.subtopics st ON q.subtopic_id = st.id
            JOIN public.topics t ON st.topic_id = t.id
            WHERE t.chapter_id = $1 AND qr.profile_id = $2 AND qr.deleted_at IS NULL
            """,
            chapter_id,
            profile_id,
        )

        return float(row["avg_score"]) if row and row["avg_score"] else 0.0
