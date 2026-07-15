"""Weak area detector — analyzes quiz performance to identify and prioritize weak topics."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Recency decay: how quickly older sessions lose influence (days)
RECENCY_HALF_LIFE = 30.0

# Weight multipliers per subject (some subjects are harder / more important)
SUBJECT_WEIGHTS: dict[str, float] = {
    "physics": 1.2,
    "chemistry": 1.1,
    "biology": 1.0,
}

# Minimum number of attempts before a topic is considered for weak area analysis
MIN_ATTEMPTS_FOR_ANALYSIS = 3

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TopicPerformance:
    """Aggregated performance metrics for a single topic."""

    topic: str
    chapter_id: str
    subject: str
    total_attempts: int = 0
    correct_attempts: int = 0
    total_time_seconds: float = 0.0
    last_attempt_at: str = ""
    accuracy_history: list[float] = field(default_factory=list)
    session_ids: list[str] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """Return accuracy as a fraction (0.0 to 1.0)."""
        if self.total_attempts == 0:
            return 0.0
        return self.correct_attempts / self.total_attempts

    @property
    def avg_time_per_question(self) -> float:
        """Return average time per question in seconds."""
        if self.total_attempts == 0:
            return 0.0
        return self.total_time_seconds / self.total_attempts

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "chapter_id": self.chapter_id,
            "subject": self.subject,
            "total_attempts": self.total_attempts,
            "correct_attempts": self.correct_attempts,
            "accuracy": round(self.accuracy, 3),
            "avg_time_per_question": round(self.avg_time_per_question, 1),
            "last_attempt_at": self.last_attempt_at,
            "accuracy_history": self.accuracy_history[-10:],
        }


@dataclass
class QuizSessionResult:
    """Result of a single quiz session."""

    session_id: str
    profile_id: str
    chapter_id: str | None
    topic: str | None
    subject: str | None
    total_questions: int
    correct_answers: int
    score_percent: float
    time_taken_seconds: float
    completed_at: str
    question_results: list[dict[str, Any]] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """Return accuracy as a fraction (0.0 to 1.0)."""
        if self.total_questions == 0:
            return 0.0
        return self.correct_answers / self.total_questions

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "profile_id": self.profile_id,
            "chapter_id": self.chapter_id,
            "topic": self.topic,
            "subject": self.subject,
            "total_questions": self.total_questions,
            "correct_answers": self.correct_answers,
            "score_percent": self.score_percent,
            "accuracy": round(self.accuracy, 3),
            "time_taken_seconds": self.time_taken_seconds,
            "completed_at": self.completed_at,
        }


@dataclass
class WeakAreaReport:
    """A weak area report for a user."""

    profile_id: str
    generated_at: str
    weak_areas: list[dict[str, Any]] = field(default_factory=list)
    subject_breakdown: dict[str, Any] = field(default_factory=dict)
    improvement_trend: dict[str, Any] = field(default_factory=dict)
    recommendations: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "generated_at": self.generated_at,
            "weak_areas": self.weak_areas,
            "subject_breakdown": self.subject_breakdown,
            "improvement_trend": self.improvement_trend,
            "recommendations": self.recommendations,
        }


# ---------------------------------------------------------------------------
# Weakness scoring
# ---------------------------------------------------------------------------

def _recency_factor(last_attempt_at: str, now: datetime | None = None) -> float:
    """Calculate recency factor: more recent = higher influence.

    Uses exponential decay with configurable half-life.
    Returns value in range (0, 1].
    """
    if not last_attempt_at:
        return 0.5

    if now is None:
        now = datetime.now(UTC)

    try:
        last_dt = datetime.fromisoformat(last_attempt_at.replace("Z", "+00:00"))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=UTC)
        days_ago = (now - last_dt).total_seconds() / 86400.0
    except (ValueError, AttributeError):
        return 0.5

    # Exponential decay: factor = 2^(-days/half_life)
    return 2.0 ** (-days_ago / RECENCY_HALF_LIFE)


def _calculate_weakness_score(
    accuracy: float,
    weight: float,
    recency: float,
    total_attempts: int,
) -> float:
    """Calculate weakness score for a topic.

    Formula: weakness_score = (1 - accuracy) * weight * recency_factor * confidence_adjustment

    The confidence_adjustment increases the score for topics with more attempts,
    making the score more reliable.

    Returns a value in range [0, 1].
    """
    # Confidence adjustment: sigmoid-like curve based on attempt count
    # At MIN_ATTEMPTS_FOR_ANALYSIS attempts, confidence ~ 0.5
    # At 3x MIN_ATTEMPTS_FOR_ANALYSIS, confidence ~ 0.9
    confidence = 1.0 - 1.0 / (1.0 + total_attempts / MIN_ATTEMPTS_FOR_ANALYSIS)

    score = (1.0 - accuracy) * weight * recency * confidence
    return round(min(score, 1.0), 4)


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class WeakAreaDetector:
    """Analyzes quiz session results to identify weak topics and generate recommendations."""

    def __init__(self) -> None:
        self._sessions: dict[str, QuizSessionResult] = {}
        self._profile_sessions: dict[str, list[str]] = {}
        self._topic_performance: dict[str, dict[str, TopicPerformance]] = {}
        logger.info("weak_area_detector.initialized")

    # -- session recording -------------------------------------------------

    def record_session(
        self,
        session_id: str,
        profile_id: str,
        chapter_id: str | None,
        topic: str | None,
        subject: str | None,
        total_questions: int,
        correct_answers: int,
        score_percent: float,
        time_taken_seconds: float = 0.0,
        completed_at: str | None = None,
        question_results: list[dict[str, Any]] | None = None,
    ) -> QuizSessionResult:
        """Record a completed quiz session for analysis."""
        now = completed_at or datetime.now(UTC).isoformat()

        result = QuizSessionResult(
            session_id=session_id,
            profile_id=profile_id,
            chapter_id=chapter_id,
            topic=topic,
            subject=subject,
            total_questions=total_questions,
            correct_answers=correct_answers,
            score_percent=score_percent,
            time_taken_seconds=time_taken_seconds,
            completed_at=now,
            question_results=question_results or [],
        )

        self._sessions[session_id] = result
        self._profile_sessions.setdefault(profile_id, []).append(session_id)

        # Update topic performance
        if topic:
            self._update_topic_performance(profile_id, result)

        logger.info(
            "weak_area.session_recorded",
            session_id=session_id,
            profile_id=profile_id,
            topic=topic,
            accuracy=round(result.accuracy, 3),
        )

        return result

    def _update_topic_performance(
        self,
        profile_id: str,
        session: QuizSessionResult,
    ) -> None:
        """Update aggregated performance for a topic."""
        profile_topics = self._topic_performance.setdefault(profile_id, {})

        topic_key = f"{session.subject or 'unknown'}:{session.topic}"

        perf = profile_topics.get(topic_key)
        if perf is None:
            perf = TopicPerformance(
                topic=session.topic or "Unknown",
                chapter_id=session.chapter_id or "",
                subject=session.subject or "unknown",
            )
            profile_topics[topic_key] = perf

        perf.total_attempts += session.total_questions
        perf.correct_attempts += session.correct_answers
        perf.total_time_seconds += session.time_taken_seconds
        perf.last_attempt_at = session.completed_at
        perf.accuracy_history.append(session.accuracy)
        perf.session_ids.append(session.session_id)

    # -- analysis methods --------------------------------------------------

    def analyze_session(self, session_id: str) -> dict[str, Any]:
        """Analyze a single quiz session and return detailed breakdown.

        Args:
            session_id: The session to analyze.

        Returns:
            Dict with session analysis including per-question breakdown,
            time analysis, and topic-level insights.
        """
        session = self._sessions.get(session_id)
        if not session:
            logger.warning("weak_area.session_not_found", session_id=session_id)
            return {"error": "Session not found", "session_id": session_id}

        analysis: dict[str, Any] = {
            "session_id": session_id,
            "profile_id": session.profile_id,
            "topic": session.topic,
            "subject": session.subject,
            "total_questions": session.total_questions,
            "correct": session.correct_answers,
            "incorrect": session.total_questions - session.correct_answers,
            "accuracy": round(session.accuracy, 3),
            "score_percent": session.score_percent,
            "time_taken_seconds": session.time_taken_seconds,
            "avg_time_per_question": round(
                session.time_taken_seconds / max(session.total_questions, 1), 1
            ),
        }

        # Per-question analysis
        if session.question_results:
            correct_times: list[float] = []
            incorrect_times: list[float] = []

            for qr in session.question_results:
                if qr.get("is_correct"):
                    correct_times.append(qr.get("time_taken", 0.0))
                else:
                    incorrect_times.append(qr.get("time_taken", 0.0))

            analysis["avg_time_correct"] = round(
                sum(correct_times) / max(len(correct_times), 1), 1
            )
            analysis["avg_time_incorrect"] = round(
                sum(incorrect_times) / max(len(incorrect_times), 1), 1
            )

            # Difficulty breakdown
            by_difficulty: dict[int, dict[str, int]] = {}
            for qr in session.question_results:
                diff = qr.get("difficulty", 1)
                if diff not in by_difficulty:
                    by_difficulty[diff] = {"total": 0, "correct": 0}
                by_difficulty[diff]["total"] += 1
                if qr.get("is_correct"):
                    by_difficulty[diff]["correct"] += 1

            analysis["by_difficulty"] = {
                str(k): {
                    "total": v["total"],
                    "correct": v["correct"],
                    "accuracy": round(v["correct"] / max(v["total"], 1), 3),
                }
                for k, v in sorted(by_difficulty.items())
            }

        return analysis

    def get_weak_areas(
        self,
        profile_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get the top weak areas for a profile.

        Uses the scoring algorithm:
            weakness_score = (1 - accuracy) * weight * recency_factor * confidence

        Args:
            profile_id: The user profile.
            limit: Maximum number of weak areas to return.

        Returns:
            List of weak area dicts sorted by weakness_score descending.
        """
        profile_topics = self._topic_performance.get(profile_id, {})
        now = datetime.now(UTC)

        scored_areas: list[dict[str, Any]] = []

        for _topic_key, perf in profile_topics.items():
            if perf.total_attempts < MIN_ATTEMPTS_FOR_ANALYSIS:
                continue

            accuracy = perf.accuracy
            weight = SUBJECT_WEIGHTS.get(perf.subject, 1.0)
            recency = _recency_factor(perf.last_attempt_at, now)
            score = _calculate_weakness_score(accuracy, weight, recency, perf.total_attempts)

            # Determine severity level
            if score >= 0.6:
                severity = "critical"
            elif score >= 0.4:
                severity = "high"
            elif score >= 0.2:
                severity = "moderate"
            else:
                severity = "low"

            scored_areas.append({
                "topic": perf.topic,
                "chapter_id": perf.chapter_id,
                "subject": perf.subject,
                "accuracy": round(accuracy, 3),
                "total_attempts": perf.total_attempts,
                "correct_attempts": perf.correct_attempts,
                "weakness_score": score,
                "severity": severity,
                "recency_factor": round(recency, 3),
                "weight": weight,
                "avg_time_per_question": round(perf.avg_time_per_question, 1),
                "last_attempt_at": perf.last_attempt_at,
                "accuracy_trend": self._compute_trend(perf.accuracy_history),
            })

        # Sort by weakness score descending
        scored_areas.sort(key=lambda x: x["weakness_score"], reverse=True)

        result = scored_areas[:limit]

        logger.info(
            "weak_area.weak_areas_retrieved",
            profile_id=profile_id,
            count=len(result),
            limit=limit,
        )

        return result

    def get_subject_breakdown(self, profile_id: str) -> dict[str, Any]:
        """Get accuracy breakdown per subject for a profile.

        Args:
            profile_id: The user profile.

        Returns:
            Dict with per-subject accuracy, total questions, and session count.
        """
        profile_topics = self._topic_performance.get(profile_id, {})

        subject_stats: dict[str, dict[str, Any]] = {}

        for _topic_key, perf in profile_topics.items():
            subj = perf.subject
            if subj not in subject_stats:
                subject_stats[subj] = {
                    "subject": subj,
                    "total_attempts": 0,
                    "correct_attempts": 0,
                    "session_count": 0,
                    "topics_covered": 0,
                    "accuracy_history": [],
                }

            stats = subject_stats[subj]
            stats["total_attempts"] += perf.total_attempts
            stats["correct_attempts"] += perf.correct_attempts
            stats["topics_covered"] += 1

            # Count unique sessions
            stats["session_count"] = len(set(perf.session_ids))

            # Aggregate accuracy history
            stats["accuracy_history"].extend(perf.accuracy_history)

        # Compute final accuracy and recent trend
        for subj, stats in subject_stats.items():
            stats["accuracy"] = round(
                stats["correct_attempts"] / max(stats["total_attempts"], 1), 3
            )
            stats["weight"] = SUBJECT_WEIGHTS.get(subj, 1.0)

            # Recent trend: compare last 5 sessions to overall
            history = stats["accuracy_history"]
            if len(history) >= 5:
                recent = history[-5:]
                older = history[:-5]
                recent_avg = sum(recent) / len(recent)
                older_avg = sum(older) / len(older) if older else recent_avg
                stats["trend"] = "improving" if recent_avg > older_avg else (
                    "declining" if recent_avg < older_avg else "stable"
                )
                stats["recent_accuracy"] = round(recent_avg, 3)
            else:
                stats["trend"] = "insufficient_data"
                stats["recent_accuracy"] = stats["accuracy"]

        logger.info(
            "weak_area.subject_breakdown",
            profile_id=profile_id,
            subjects=list(subject_stats.keys()),
        )

        return subject_stats

    def get_improvement_trend(self, profile_id: str) -> dict[str, Any]:
        """Get accuracy trend over time for a profile.

        Args:
            profile_id: The user profile.

        Returns:
            Dict with overall trend, monthly breakdown, and trajectory.
        """
        profile_sessions = self._profile_sessions.get(profile_id, [])

        if not profile_sessions:
            return {
                "profile_id": profile_id,
                "total_sessions": 0,
                "trend": "no_data",
                "monthly_breakdown": [],
                "trajectory": "unknown",
            }

        # Sort sessions by completion time
        sessions = [self._sessions[sid] for sid in profile_sessions if sid in self._sessions]
        sessions.sort(key=lambda s: s.completed_at)

        # Overall trend
        if len(sessions) < 2:
            return {
                "profile_id": profile_id,
                "total_sessions": len(sessions),
                "trend": "insufficient_data",
                "overall_accuracy": round(sessions[0].accuracy, 3) if sessions else 0.0,
                "monthly_breakdown": [],
                "trajectory": "unknown",
            }

        # Split into first half and second half
        mid = len(sessions) // 2
        first_half = sessions[:mid]
        second_half = sessions[mid:]

        first_avg = sum(s.accuracy for s in first_half) / len(first_half)
        second_avg = sum(s.accuracy for s in second_half) / len(second_half)

        change = second_avg - first_avg
        if change > 0.05:
            trajectory = "improving"
        elif change < -0.05:
            trajectory = "declining"
        else:
            trajectory = "stable"

        # Monthly breakdown
        monthly: dict[str, dict[str, Any]] = {}
        for s in sessions:
            try:
                dt = datetime.fromisoformat(s.completed_at.replace("Z", "+00:00"))
                month_key = dt.strftime("%Y-%m")
            except (ValueError, AttributeError):
                month_key = "unknown"

            if month_key not in monthly:
                monthly[month_key] = {
                    "month": month_key,
                    "sessions": 0,
                    "total_questions": 0,
                    "correct_answers": 0,
                    "total_time_seconds": 0.0,
                }

            m = monthly[month_key]
            m["sessions"] += 1
            m["total_questions"] += s.total_questions
            m["correct_answers"] += s.correct_answers
            m["total_time_seconds"] += s.time_taken_seconds

        monthly_list = []
        for month_key in sorted(monthly.keys()):
            m = monthly[month_key]
            m["accuracy"] = round(m["correct_answers"] / max(m["total_questions"], 1), 3)
            m["avg_time_per_question"] = round(
                m["total_time_seconds"] / max(m["total_questions"], 1), 1
            )
            monthly_list.append(m)

        # Recent 5-session rolling average
        recent_5 = sessions[-5:]
        recent_accuracy = round(
            sum(s.accuracy for s in recent_5) / len(recent_5), 3
        )

        result = {
            "profile_id": profile_id,
            "total_sessions": len(sessions),
            "overall_accuracy": round(
                sum(s.accuracy for s in sessions) / len(sessions), 3
            ),
            "first_half_accuracy": round(first_avg, 3),
            "second_half_accuracy": round(second_avg, 3),
            "accuracy_change": round(change, 3),
            "trajectory": trajectory,
            "recent_5_session_accuracy": recent_accuracy,
            "monthly_breakdown": monthly_list,
        }

        logger.info(
            "weak_area.improvement_trend",
            profile_id=profile_id,
            trajectory=trajectory,
            accuracy_change=round(change, 3),
        )

        return result

    def generate_study_recommendations(self, profile_id: str) -> list[dict[str, Any]]:
        """Generate prioritized study recommendations for a profile.

        Recommendations are based on:
        - Weak areas with high weakness scores
        - Topics with declining accuracy trends
        - Subjects with below-average performance
        - Topics not attempted recently (spaced repetition)

        Args:
            profile_id: The user profile.

        Returns:
            List of recommendation dicts sorted by priority.
        """
        weak_areas = self.get_weak_areas(profile_id, limit=20)
        subject_breakdown = self.get_subject_breakdown(profile_id)

        recommendations: list[dict[str, Any]] = []
        seen_topics: set[str] = set()

        # 1. Critical weak areas (highest priority)
        for area in weak_areas:
            if area["severity"] in ("critical", "high"):
                topic_key = f"{area['subject']}:{area['topic']}"
                if topic_key in seen_topics:
                    continue
                seen_topics.add(topic_key)

                recommendations.append({
                    "type": "weak_area",
                    "priority": "critical" if area["severity"] == "critical" else "high",
                    "topic": area["topic"],
                    "chapter_id": area["chapter_id"],
                    "subject": area["subject"],
                    "current_accuracy": area["accuracy"],
                    "weakness_score": area["weakness_score"],
                    "action": f"Practice {area['topic']} — accuracy is {area['accuracy']*100:.0f}%",
                    "suggested_questions": min(20, max(10, int(20 * (1 - area["accuracy"])))),
                    "reason": f"Consistently low accuracy ({area['accuracy']*100:.0f}%) across {area['total_attempts']} attempts",
                })

        # 2. Declining subjects
        for subj, stats in subject_breakdown.items():
            if stats.get("trend") == "declining" and subj not in [r.get("subject") for r in recommendations if r["type"] == "subject_review"]:
                recommendations.append({
                    "type": "subject_review",
                    "priority": "high",
                    "subject": subj,
                    "current_accuracy": stats["accuracy"],
                    "recent_accuracy": stats.get("recent_accuracy", stats["accuracy"]),
                    "action": f"Review {subj} fundamentals — performance is declining",
                    "suggested_questions": 15,
                    "reason": f"Accuracy dropped from historical average to {stats.get('recent_accuracy', stats['accuracy'])*100:.0f}% recently",
                })

        # 3. Low-coverage topics (few attempts, moderate accuracy)
        profile_topics = self._topic_performance.get(profile_id, {})
        for _topic_key, perf in profile_topics.items():
            if perf.total_attempts < MIN_ATTEMPTS_FOR_ANALYSIS:
                topic_key_str = f"{perf.subject}:{perf.topic}"
                if topic_key_str not in seen_topics:
                    seen_topics.add(topic_key_str)
                    recommendations.append({
                        "type": "more_practice",
                        "priority": "medium",
                        "topic": perf.topic,
                        "chapter_id": perf.chapter_id,
                        "subject": perf.subject,
                        "current_accuracy": perf.accuracy,
                        "total_attempts": perf.total_attempts,
                        "action": f"More practice needed for {perf.topic}",
                        "suggested_questions": 10,
                        "reason": f"Only {perf.total_attempts} attempts so far — need more data",
                    })

        # 4. Spaced repetition: topics not attempted recently
        now = datetime.now(UTC)
        for _topic_key, perf in profile_topics.items():
            if not perf.last_attempt_at:
                continue
            try:
                last_dt = datetime.fromisoformat(perf.last_attempt_at.replace("Z", "+00:00"))
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=UTC)
                days_since = (now - last_dt).total_seconds() / 86400.0
            except (ValueError, AttributeError):
                continue

            if days_since > 14 and perf.accuracy < 0.7:
                topic_key_str = f"{perf.subject}:{perf.topic}"
                if topic_key_str not in seen_topics:
                    seen_topics.add(topic_key_str)
                    recommendations.append({
                        "type": "spaced_review",
                        "priority": "medium",
                        "topic": perf.topic,
                        "chapter_id": perf.chapter_id,
                        "subject": perf.subject,
                        "current_accuracy": perf.accuracy,
                        "days_since_last_attempt": round(days_since, 0),
                        "action": f"Review {perf.topic} — last attempted {int(days_since)} days ago",
                        "suggested_questions": 10,
                        "reason": f"Accuracy was {perf.accuracy*100:.0f}% and it's been {int(days_since)} days since last practice",
                    })

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda r: priority_order.get(r.get("priority", "low"), 3))

        logger.info(
            "weak_area.recommendations_generated",
            profile_id=profile_id,
            count=len(recommendations),
        )

        return recommendations

    def generate_full_report(self, profile_id: str) -> WeakAreaReport:
        """Generate a comprehensive weak area report.

        Args:
            profile_id: The user profile.

        Returns:
            WeakAreaReport with all analysis sections.
        """
        now = datetime.now(UTC).isoformat()

        return WeakAreaReport(
            profile_id=profile_id,
            generated_at=now,
            weak_areas=self.get_weak_areas(profile_id),
            subject_breakdown=self.get_subject_breakdown(profile_id),
            improvement_trend=self.get_improvement_trend(profile_id),
            recommendations=self.generate_study_recommendations(profile_id),
        )

    # -- internals ---------------------------------------------------------

    def _compute_trend(self, history: list[float]) -> str:
        """Compute trend direction from accuracy history.

        Uses linear regression slope to determine trend.
        """
        if len(history) < 3:
            return "insufficient_data"

        n = len(history)
        x_mean = (n - 1) / 2.0
        y_mean = sum(history) / n

        numerator = sum((i - x_mean) * (history[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if slope > 0.02:
            return "improving"
        elif slope < -0.02:
            return "declining"
        else:
            return "stable"

    def get_profile_stats(self, profile_id: str) -> dict[str, Any]:
        """Get overall statistics for a profile.

        Args:
            profile_id: The user profile.

        Returns:
            Dict with total sessions, questions, accuracy, and topic coverage.
        """
        profile_sessions = self._profile_sessions.get(profile_id, [])
        profile_topics = self._topic_performance.get(profile_id, {})

        if not profile_sessions:
            return {
                "profile_id": profile_id,
                "total_sessions": 0,
                "total_questions": 0,
                "overall_accuracy": 0.0,
                "topics_covered": 0,
                "subjects_covered": [],
            }

        total_questions = 0
        total_correct = 0
        subjects: set[str] = set()

        for sid in profile_sessions:
            session = self._sessions.get(sid)
            if session:
                total_questions += session.total_questions
                total_correct += session.correct_answers
                if session.subject:
                    subjects.add(session.subject)

        return {
            "profile_id": profile_id,
            "total_sessions": len(profile_sessions),
            "total_questions": total_questions,
            "total_correct": total_correct,
            "overall_accuracy": round(total_correct / max(total_questions, 1), 3),
            "topics_covered": len(profile_topics),
            "subjects_covered": sorted(subjects),
        }

    def reset(self, profile_id: str | None = None) -> None:
        """Clear session data.

        Args:
            profile_id: If provided, only clear data for this profile.
                        If None, clear all data.
        """
        if profile_id is None:
            self._sessions.clear()
            self._profile_sessions.clear()
            self._topic_performance.clear()
            logger.info("weak_area_detector.reset_all")
        else:
            # Remove sessions for this profile
            session_ids = self._profile_sessions.pop(profile_id, [])
            for sid in session_ids:
                self._sessions.pop(sid, None)
            self._topic_performance.pop(profile_id, None)
            logger.info("weak_area_detector.reset_profile", profile_id=profile_id)
