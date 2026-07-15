"""Active recall service — generates and manages active recall sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog
from datetime import UTC

logger = structlog.get_logger(__name__)


@dataclass
class RecallQuestion:
    """A single active recall question."""

    question_id: str
    question: str
    answer: str
    difficulty: str = "medium"
    hint: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question": self.question,
            "answer": self.answer,
            "difficulty": self.difficulty,
            "hint": self.hint,
            "metadata": self.metadata,
        }


@dataclass
class RecallSession:
    """An active recall session."""

    session_id: str
    questions: list[RecallQuestion] = field(default_factory=list)
    current_index: int = 0
    score: int = 0
    total: int = 0
    started_at: str = ""
    completed_at: str = ""

    @property
    def is_complete(self) -> bool:
        return self.current_index >= len(self.questions)

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.score / self.total, 3)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_index": self.current_index,
            "total_questions": len(self.questions),
            "score": self.score,
            "total_answered": self.total,
            "accuracy": self.accuracy,
            "is_complete": self.is_complete,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class ActiveRecallEngine:
    """Manages active recall sessions for self-testing."""

    def __init__(self) -> None:
        self._sessions: dict[str, RecallSession] = {}

    def create_session(
        self,
        session_id: str,
        questions: list[dict[str, Any]],
        started_at: str,
    ) -> RecallSession:
        """Create a new active recall session."""
        recall_questions = [
            RecallQuestion(
                question_id=q.get("question_id", f"q_{i}"),
                question=q["question"],
                answer=q["answer"],
                difficulty=q.get("difficulty", "medium"),
                hint=q.get("hint", ""),
                metadata=q.get("metadata", {}),
            )
            for i, q in enumerate(questions)
        ]

        session = RecallSession(
            session_id=session_id,
            questions=recall_questions,
            started_at=started_at,
        )
        self._sessions[session_id] = session
        logger.info("active_recall.session_created", session_id=session_id, questions=len(questions))
        return session

    def get_current_question(self, session_id: str) -> RecallQuestion | None:
        """Get the current question in a session."""
        session = self._sessions.get(session_id)
        if not session or session.is_complete:
            return None
        return session.questions[session.current_index]

    def submit_answer(
        self,
        session_id: str,
        user_answer: str,
        correct: bool,
    ) -> dict[str, Any]:
        """Submit an answer and get feedback."""
        session = self._sessions.get(session_id)
        if not session or session.is_complete:
            return {"error": "Session not found or completed"}

        question = session.questions[session.current_index]
        session.total += 1
        if correct:
            session.score += 1

        session.current_index += 1

        result = {
            "correct": correct,
            "correct_answer": question.answer,
            "question": question.question,
            "session_progress": {
                "current": session.current_index,
                "total": len(session.questions),
                "score": session.score,
                "accuracy": session.accuracy,
            },
        }

        if session.is_complete:
            session.completed_at = self._now_iso()
            result["session_complete"] = True
            result["final_score"] = session.score
            result["final_accuracy"] = session.accuracy

        logger.info(
            "active_recall.answer_submitted",
            session_id=session_id,
            correct=correct,
            accuracy=session.accuracy,
        )
        return result

    def get_session(self, session_id: str) -> RecallSession | None:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def get_session_results(self, session_id: str) -> dict[str, Any] | None:
        """Get final results for a completed session."""
        session = self._sessions.get(session_id)
        if not session or not session.is_complete:
            return None

        return {
            "session_id": session_id,
            "score": session.score,
            "total": session.total,
            "accuracy": session.accuracy,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
        }

    def list_sessions(self) -> list[dict[str, Any]]:
        """List all sessions."""
        return [
            {
                "session_id": s.session_id,
                "total_questions": len(s.questions),
                "score": s.score,
                "accuracy": s.accuracy,
                "is_complete": s.is_complete,
                "started_at": s.started_at,
            }
            for s in self._sessions.values()
        ]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def reset(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()

    @staticmethod
    def _now_iso() -> str:
        from datetime import datetime
        return datetime.now(UTC).isoformat()
