"""Recovery planner service — generates accelerated plans for struggling students."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)


class RecoveryPlanner:
    """Generate recovery plans for students who are behind schedule."""

    def __init__(self, *, pool: asyncpg.Pool | None) -> None:
        self._pool = pool

    async def generate_recovery_plan(
        self,
        profile_id: UUID,
        roadmap_id: UUID | None,
        exam_date: date,
        trigger_reason: str = "behind_schedule",
    ) -> dict[str, Any]:
        """Generate an accelerated recovery plan."""
        if self._pool is None:
            return {"error": "Database not available"}

        today = date.today()
        days_remaining = (exam_date - today).days

        if days_remaining <= 0:
            return {"error": "Exam date has passed"}

        async with self._pool.acquire() as conn:
            chapters = await conn.fetch(
                """
                SELECT c.id, c.name, c.weightage, c.sort_order,
                       s.name as subject_name
                FROM public.chapters c
                JOIN public.subjects s ON c.subject_id = s.id
                WHERE c.deleted_at IS NULL AND s.deleted_at IS NULL
                ORDER BY c.weightage DESC, c.sort_order
                """
            )

            chapter_statuses = []
            for chapter in chapters:
                progress = await self._get_chapter_progress(conn, profile_id, chapter["id"])
                chapter_statuses.append(
                    {
                        "chapter_id": str(chapter["id"]),
                        "chapter_name": chapter["name"],
                        "subject_name": chapter["subject_name"],
                        "weightage": float(chapter["weightage"] or 1.0),
                        "completion_rate": progress["completion_rate"],
                        "is_completed": progress["completion_rate"] >= 0.9,
                    }
                )

            accelerated = []
            skipped = []

            for ch in chapter_statuses:
                if ch["is_completed"]:
                    continue
                if ch["weightage"] >= 5.0:
                    accelerated.append(
                        {
                            "chapter_id": ch["chapter_id"],
                            "chapter_name": ch["chapter_name"],
                            "subject_name": ch["subject_name"],
                            "weightage": ch["weightage"],
                            "current_completion": ch["completion_rate"],
                            "priority": "high",
                        }
                    )
                elif ch["weightage"] >= 3.0:
                    accelerated.append(
                        {
                            "chapter_id": ch["chapter_id"],
                            "chapter_name": ch["chapter_name"],
                            "subject_name": ch["subject_name"],
                            "weightage": ch["weightage"],
                            "current_completion": ch["completion_rate"],
                            "priority": "medium",
                        }
                    )
                else:
                    skipped.append(
                        {
                            "chapter_id": ch["chapter_id"],
                            "chapter_name": ch["chapter_name"],
                            "subject_name": ch["subject_name"],
                            "weightage": ch["weightage"],
                            "reason": "low_weightage",
                        }
                    )

            total_accelerated = len(accelerated)
            days_per_chapter = max(days_remaining / max(total_accelerated, 1), 0.5)
            daily_hours = min(max(8.0, total_accelerated * 1.5), 14.0)

            revised_completion = today + date.resolution * days_remaining

            plan = await self._save_plan(
                conn,
                profile_id,
                roadmap_id,
                trigger_reason,
                revised_completion,
                accelerated,
                skipped,
                daily_hours,
            )

            return {
                "plan_id": plan["id"],
                "trigger_reason": trigger_reason,
                "days_remaining": days_remaining,
                "revised_completion_date": revised_completion.isoformat(),
                "daily_hours_target": daily_hours,
                "accelerated_chapters": accelerated,
                "skipped_chapters": skipped,
                "summary": {
                    "total_accelerated": total_accelerated,
                    "total_skipped": len(skipped),
                    "days_per_chapter": round(days_per_chapter, 1),
                },
            }

    async def get_active_plan(self, profile_id: UUID) -> dict[str, Any] | None:
        """Get the active recovery plan for a user."""
        if self._pool is None:
            return None

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT *
                FROM public.recovery_plans
                WHERE profile_id = $1 AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                profile_id,
            )

            if not row:
                return None

            return {
                "plan_id": str(row["id"]),
                "trigger_reason": row["trigger_reason"],
                "original_completion_date": (
                    row["original_completion_date"].isoformat()
                    if row["original_completion_date"]
                    else None
                ),
                "revised_completion_date": (
                    row["revised_completion_date"].isoformat()
                    if row["revised_completion_date"]
                    else None
                ),
                "accelerated_chapters": row["accelerated_chapters"],
                "skipped_chapters": row["skipped_chapters"],
                "daily_hours_target": float(row["daily_hours_target"]),
                "status": row["status"],
                "created_at": row["created_at"].isoformat(),
            }

    async def _save_plan(
        self,
        conn: asyncpg.Connection,
        profile_id: UUID,
        roadmap_id: UUID | None,
        trigger_reason: str,
        revised_completion: date,
        accelerated: list[dict[str, Any]],
        skipped: list[dict[str, Any]],
        daily_hours: float,
    ) -> dict[str, Any]:
        row = await conn.fetchrow(
            """
            INSERT INTO public.recovery_plans
                (profile_id, roadmap_id, trigger_reason, revised_completion_date,
                 accelerated_chapters, skipped_chapters, daily_hours_target, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'active')
            RETURNING id, created_at
            """,
            profile_id,
            roadmap_id,
            trigger_reason,
            revised_completion,
            accelerated,
            skipped,
            daily_hours,
        )

        return {"id": str(row["id"]), "created_at": row["created_at"].isoformat()}

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
