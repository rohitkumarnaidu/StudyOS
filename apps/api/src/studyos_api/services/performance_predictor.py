"""Performance prediction service — predicts NEET score with confidence intervals."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog

if TYPE_CHECKING:
    import asyncpg

logger = structlog.get_logger(__name__)


class PerformancePredictor:
    """Predict user performance based on completion rates and quiz scores."""

    def __init__(self, *, pool: asyncpg.Pool | None) -> None:
        self._pool = pool

    async def predict_score(self, profile_id: UUID) -> dict[str, Any]:
        """Generate a score prediction with confidence interval."""
        if self._pool is None:
            return {
                "predicted_score": 0,
                "confidence_lower": 0,
                "confidence_upper": 0,
                "model_version": "v1",
            }

        async with self._pool.acquire() as conn:
            features = await self._compute_features(conn, profile_id)

            predicted_score = self._compute_prediction(features)
            confidence_margin = self._compute_confidence_margin(features)

            confidence_lower = max(0, predicted_score - confidence_margin)
            confidence_upper = min(720, predicted_score + confidence_margin)

            prediction_date = date.today()

            await conn.execute(
                """
                INSERT INTO public.performance_predictions
                    (profile_id, predicted_score, confidence_interval_lower,
                     confidence_interval_upper, prediction_date, model_version, features_used)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                profile_id,
                round(predicted_score, 2),
                round(confidence_lower, 2),
                round(confidence_upper, 2),
                prediction_date,
                "v1",
                features,
            )

            return {
                "predicted_score": round(predicted_score, 2),
                "confidence_lower": round(confidence_lower, 2),
                "confidence_upper": round(confidence_upper, 2),
                "model_version": "v1",
                "prediction_date": prediction_date.isoformat(),
                "features": features,
            }

    async def get_predictions(self, profile_id: UUID, limit: int = 10) -> list[dict[str, Any]]:
        """Get prediction history for a user."""
        if self._pool is None:
            return []

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT *
                FROM public.performance_predictions
                WHERE profile_id = $1
                ORDER BY prediction_date DESC
                LIMIT $2
                """,
                profile_id,
                limit,
            )

            return [
                {
                    "predicted_score": float(row["predicted_score"]),
                    "confidence_lower": float(row["confidence_interval_lower"]),
                    "confidence_upper": float(row["confidence_interval_upper"]),
                    "prediction_date": row["prediction_date"].isoformat(),
                    "model_version": row["model_version"],
                }
                for row in rows
            ]

    async def _compute_features(self, conn: asyncpg.Connection, profile_id: UUID) -> dict[str, Any]:
        progress_row = await conn.fetchrow(
            """
            SELECT
                COUNT(DISTINCT st.id) as total_subtopics,
                COUNT(DISTINCT CASE WHEN sc.id IS NOT NULL THEN st.id END) as completed_subtopics
            FROM public.subtopics st
            LEFT JOIN public.subtopic_completions sc
                ON st.id = sc.subtopic_id AND sc.profile_id = $1 AND sc.deleted_at IS NULL
            WHERE st.deleted_at IS NULL
            """,
            profile_id,
        )

        total = progress_row["total_subtopics"] if progress_row["total_subtopics"] else 0
        completed = (
            progress_row["completed_subtopics"] if progress_row["completed_subtopics"] else 0
        )
        completion_rate = completed / total if total > 0 else 0.0

        quiz_row = await conn.fetchrow(
            """
            SELECT
                COUNT(*) as total_questions,
                AVG(CASE WHEN is_correct THEN 1.0 ELSE 0.0 END) as avg_accuracy
            FROM public.quiz_responses
            WHERE profile_id = $1 AND deleted_at IS NULL
            """,
            profile_id,
        )

        total_questions = quiz_row["total_questions"] if quiz_row["total_questions"] else 0
        avg_accuracy = float(quiz_row["avg_accuracy"]) if quiz_row["avg_accuracy"] else 0.0

        streak_row = await conn.fetchrow(
            """
            SELECT current_streak, longest_streak
            FROM public.streaks
            WHERE profile_id = $1 AND deleted_at IS NULL
            """,
            profile_id,
        )

        current_streak = streak_row["current_streak"] if streak_row else 0
        longest_streak = streak_row["longest_streak"] if streak_row else 0

        return {
            "completion_rate": round(completion_rate, 4),
            "total_subtopics": total,
            "completed_subtopics": completed,
            "avg_accuracy": round(avg_accuracy, 4),
            "total_questions_attempted": total_questions,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
        }

    def _compute_prediction(self, features: dict[str, Any]) -> float:
        completion_rate = features["completion_rate"]
        avg_accuracy = features["avg_accuracy"]
        current_streak = features["current_streak"]

        base_score = 350.0
        completion_contribution = completion_rate * 200.0
        accuracy_contribution = avg_accuracy * 120.0
        streak_bonus = min(current_streak * 2.0, 30.0)

        predicted = base_score + completion_contribution + accuracy_contribution + streak_bonus
        return min(max(predicted, 200), 720)

    def _compute_confidence_margin(self, features: dict[str, Any]) -> float:
        total_questions = features["total_questions_attempted"]
        completion_rate = features["completion_rate"]

        data_confidence = min(total_questions / 100.0, 1.0)
        coverage_confidence = completion_rate

        combined_confidence = data_confidence * 0.6 + coverage_confidence * 0.4
        margin = 80.0 * (1.0 - combined_confidence) + 20.0

        return round(margin, 2)
