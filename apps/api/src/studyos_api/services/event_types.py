"""Event type definitions for the StudyOS event bus."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class EventCategory(str, Enum):
    STUDY = "study"
    QUIZ = "quiz"
    ROADMAP = "roadmap"
    REVISION = "revision"
    MISTAKE = "mistake"
    MOCK_TEST = "mock_test"
    PREDICTION = "prediction"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"


class EventPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class StudyOSEvent:
    """Immutable event object for the StudyOS event bus."""

    event_type: str
    category: EventCategory
    profile_id: UUID
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: UUID = field(default_factory=uuid4)
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: UUID | None = None
    idempotency_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "category": self.category.value,
            "profile_id": str(self.profile_id),
            "payload": self.payload,
            "priority": self.priority.value,
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
            "idempotency_key": self.idempotency_key,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StudyOSEvent:
        return cls(
            event_type=data["event_type"],
            category=EventCategory(data["category"]),
            profile_id=UUID(data["profile_id"]),
            payload=data.get("payload", {}),
            event_id=UUID(data["event_id"]) if "event_id" in data else uuid4(),
            priority=EventPriority(data.get("priority", "normal")),
            correlation_id=UUID(data["correlation_id"]) if data.get("correlation_id") else None,
            idempotency_key=data.get("idempotency_key"),
        )


class EventTypes:
    """All event types in the system."""

    STUDY_COMPLETED = "study.completed"
    STUDY_SESSION_STARTED = "study.session_started"
    STUDY_SESSION_ENDED = "study.session_ended"

    QUIZ_STARTED = "quiz.started"
    QUIZ_FINISHED = "quiz.finished"
    QUIZ_QUESTION_ANSWERED = "quiz.question_answered"

    ROADMAP_GENERATED = "roadmap.generated"
    ROADMAP_UPDATED = "roadmap.updated"
    ROADMAP_ITEM_COMPLETED = "roadmap.item_completed"

    REVISION_DUE = "revision.due"
    REVISION_COMPLETED = "revision.completed"
    REVISION_PACK_GENERATED = "revision.pack_generated"

    MISTAKE_LOGGED = "mistake.logged"
    CONCEPT_GAP_DETECTED = "concept_gap.detected"
    MISTAKE_PATTERN_FOUND = "mistake.pattern_found"

    MOCK_TEST_STARTED = "mock_test.started"
    MOCK_TEST_FINISHED = "mock_test.finished"
    MOCK_TEST_SCORED = "mock_test.scored"

    PREDICTION_UPDATED = "prediction.updated"
    BURNOUT_ALERT = "burnout.alert"

    ACHIEVEMENT_UNLOCKED = "achievement.unlocked"
    STREAK_UPDATED = "streak.updated"

    SYSTEM_ERROR = "system.error"
    SYSTEM_COST_ALERT = "system.cost_alert"
