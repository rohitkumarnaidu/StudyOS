"""Exam optimizer service — optimizes study plans based on exam date."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)


class ExamOptimizer:
    """Optimize study plans based on exam proximity and user performance."""

    def __init__(self, *, pool: asyncpg.Pool | None) -> None:
        self._pool = pool

    async def optimize_plan(self, profile_id: UUID, exam_date: date) -> dict[str, Any]:
        """Generate an optimized study plan for the exam date."""
        if self._pool is None:
            return {"error": "Database not available"}

        today = date.today()
        days_to_exam = (exam_date - today).days

        if days_to_exam <= 0:
            return {"error": "Exam date has passed"}

        async with self._pool.acquire() as conn:
            subjects = await conn.fetch(
                """
                SELECT s.id, s.name,
                       COUNT(DISTINCT c.id) as chapter_count
                FROM public.subjects s
                LEFT JOIN public.chapters c ON s.id = c.subject_id AND c.deleted_at IS NULL
                WHERE s.deleted_at IS NULL
                GROUP BY s.id, s.name
                """
            )

            subject_analysis = []
            for subject in subjects:
                subject_id = subject["id"]
                analysis = await self._analyze_subject(conn, profile_id, subject_id)
                subject_analysis.append(analysis)

            phase = self._determine_phase(days_to_exam)
            recommendations = self._generate_recommendations(subject_analysis, phase, days_to_exam)

            return {
                "exam_date": exam_date.isoformat(),
                "days_remaining": days_to_exam,
                "phase": phase,
                "subject_analysis": subject_analysis,
                "recommendations": recommendations,
                "daily_target_hours": self._compute_daily_hours(
                    phase, subject_analysis,
                ),
                "weekly_milestones": self._compute_weekly_milestones(
                    phase, days_to_exam, subject_analysis,
                ),
            }

    async def _analyze_subject(
        self, conn: asyncpg.Connection, profile_id: UUID, subject_id: UUID,
    ) -> dict[str, Any]:
        chapters = await conn.fetch(
            """
            SELECT c.id, c.name, c.weightage,
                   COUNT(DISTINCT st.id) as total_subtopics,
                   COUNT(DISTINCT CASE WHEN sc.id IS NOT NULL THEN st.id END) as completed_subtopics
            FROM public.chapters c
            LEFT JOIN public.topics t ON c.id = t.chapter_id AND t.deleted_at IS NULL
            LEFT JOIN public.subtopics st ON t.id = st.topic_id AND st.deleted_at IS NULL
            LEFT JOIN public.subtopic_completions sc
                ON st.id = sc.subtopic_id AND sc.profile_id = $1 AND sc.deleted_at IS NULL
            WHERE c.subject_id = $2 AND c.deleted_at IS NULL
            GROUP BY c.id, c.name, c.weightage
            ORDER BY c.weightage DESC
            """,
            profile_id,
            subject_id,
        )

        total_subtopics = 0
        completed_subtopics = 0
        weak_chapters = []
        strong_chapters = []

        for ch in chapters:
            total = ch["total_subtopics"] or 0
            completed = ch["completed_subtopics"] or 0
            total_subtopics += total
            completed_subtopics += completed

            completion_rate = completed / total if total > 0 else 0.0

            chapter_info = {
                "chapter_id": str(ch["id"]),
                "chapter_name": ch["name"],
                "weightage": float(ch["weightage"] or 1.0),
                "completion_rate": round(completion_rate, 2),
            }

            if completion_rate < 0.5:
                weak_chapters.append(chapter_info)
            elif completion_rate >= 0.8:
                strong_chapters.append(chapter_info)

        subject_completion = completed_subtopics / total_subtopics if total_subtopics > 0 else 0.0

        return {
            "subject_id": str(subject_id),
            "subject_name": chapters[0]["name"] if chapters else "Unknown",
            "total_chapters": len(chapters),
            "total_subtopics": total_subtopics,
            "completed_subtopics": completed_subtopics,
            "completion_rate": round(subject_completion, 2),
            "weak_chapters": weak_chapters,
            "strong_chapters": strong_chapters,
        }

    def _determine_phase(self, days_to_exam: int) -> str:
        if days_to_exam <= 30:
            return "crash"
        if days_to_exam <= 60:
            return "intensive"
        if days_to_exam <= 90:
            return "focused"
        return "foundational"

    def _generate_recommendations(
        self,
        subject_analysis: list[dict[str, Any]],
        phase: str,
        days_to_exam: int,
    ) -> list[dict[str, Any]]:
        recommendations = []

        for subject in subject_analysis:
            if subject["completion_rate"] < 0.3:
                recommendations.append({
                    "type": "priority_focus",
                    "subject": subject["subject_name"],
                    "message": (
                        f"Focus on {subject['subject_name']} — "
                        f"only {subject['completion_rate']*100:.0f}% complete"
                    ),
                    "priority": "critical",
                })
            elif subject["completion_rate"] < 0.6:
                recommendations.append({
                    "type": "accelerate",
                    "subject": subject["subject_name"],
                    "message": (
                        f"Accelerate {subject['subject_name']} — "
                        f"{subject['completion_rate']*100:.0f}% complete"
                    ),
                    "priority": "high",
                })

        if phase == "crash":
            recommendations.append({
                "type": "strategy",
                "message": "Crash phase: Focus only on high-weightage chapters and revision",
                "priority": "critical",
            })
        elif phase == "intensive":
            recommendations.append({
                "type": "strategy",
                "message": "Intensive phase: Complete remaining chapters + start mock tests",
                "priority": "high",
            })

        weak_count = sum(len(s["weak_chapters"]) for s in subject_analysis)
        if weak_count > 10:
            recommendations.append({
                "type": "warning",
                "message": (
                    f"{weak_count} chapters need significant attention — "
                    "consider recovery plan"
                ),
                "priority": "high",
            })

        return recommendations

    def _compute_daily_hours(self, phase: str, subject_analysis: list[dict[str, Any]]) -> float:
        avg_completion = (
            sum(s["completion_rate"] for s in subject_analysis)
            / max(len(subject_analysis), 1)
        )

        if phase == "crash":
            return 12.0
        if phase == "intensive":
            return 10.0
        if phase == "focused":
            return 8.0

        if avg_completion < 0.3:
            return 8.0
        if avg_completion < 0.6:
            return 6.0
        return 4.0

    def _compute_weekly_milestones(
        self,
        phase: str,
        days_to_exam: int,
        subject_analysis: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        weeks = max(days_to_exam // 7, 1)
        milestones = []

        total_chapters = sum(s["total_chapters"] for s in subject_analysis)
        chapters_per_week = max(total_chapters / weeks, 1)

        for week in range(1, min(weeks, 12) + 1):
            target_completion = min(week * chapters_per_week / max(total_chapters, 1), 1.0)
            milestones.append({
                "week": week,
                "target_chapters": round(week * chapters_per_week),
                "target_completion_pct": round(target_completion * 100, 1),
                "focus": self._get_week_focus(phase, week, subject_analysis),
            })

        return milestones

    def _get_week_focus(
        self,
        phase: str,
        week: int,
        subject_analysis: list[dict[str, Any]],
    ) -> str:
        if phase == "crash":
            return "Revision + mock tests"
        if phase == "intensive":
            if week <= 2:
                return "Complete weak chapters"
            return "Mock tests + revision"
        if phase == "focused":
            weak_subjects = [
                s["subject_name"] for s in subject_analysis
                if s["completion_rate"] < 0.5
            ]
            if weak_subjects and week <= len(weak_subjects):
                return f"Focus on {weak_subjects[week - 1]}"
            return "Balanced progress"

        return "Foundation building"
