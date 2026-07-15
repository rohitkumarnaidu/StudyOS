"""Tests for event type definitions."""

from uuid import UUID, uuid4

import pytest

from studyos_api.services.event_types import (
    EventCategory,
    EventPriority,
    EventTypes,
    StudyOSEvent,
)


class TestEventCategory:
    def test_all_categories_exist(self) -> None:
        assert EventCategory.STUDY.value == "study"
        assert EventCategory.QUIZ.value == "quiz"
        assert EventCategory.ROADMAP.value == "roadmap"
        assert EventCategory.REVISION.value == "revision"
        assert EventCategory.MISTAKE.value == "mistake"
        assert EventCategory.MOCK_TEST.value == "mock_test"
        assert EventCategory.PREDICTION.value == "prediction"
        assert EventCategory.ACHIEVEMENT.value == "achievement"
        assert EventCategory.SYSTEM.value == "system"

    def test_category_count(self) -> None:
        assert len(EventCategory) == 9


class TestEventPriority:
    def test_all_priorities_exist(self) -> None:
        assert EventPriority.LOW.value == "low"
        assert EventPriority.NORMAL.value == "normal"
        assert EventPriority.HIGH.value == "high"
        assert EventPriority.CRITICAL.value == "critical"

    def test_default_priority_is_normal(self) -> None:
        event = StudyOSEvent(
            event_type="test.event",
            category=EventCategory.SYSTEM,
            profile_id=uuid4(),
        )
        assert event.priority == EventPriority.NORMAL


class TestEventTypes:
    def test_study_events(self) -> None:
        assert EventTypes.STUDY_COMPLETED == "study.completed"
        assert EventTypes.STUDY_SESSION_STARTED == "study.session_started"
        assert EventTypes.STUDY_SESSION_ENDED == "study.session_ended"

    def test_quiz_events(self) -> None:
        assert EventTypes.QUIZ_STARTED == "quiz.started"
        assert EventTypes.QUIZ_FINISHED == "quiz.finished"
        assert EventTypes.QUIZ_QUESTION_ANSWERED == "quiz.question_answered"

    def test_roadmap_events(self) -> None:
        assert EventTypes.ROADMAP_GENERATED == "roadmap.generated"
        assert EventTypes.ROADMAP_UPDATED == "roadmap.updated"
        assert EventTypes.ROADMAP_ITEM_COMPLETED == "roadmap.item_completed"

    def test_revision_events(self) -> None:
        assert EventTypes.REVISION_DUE == "revision.due"
        assert EventTypes.REVISION_COMPLETED == "revision.completed"
        assert EventTypes.REVISION_PACK_GENERATED == "revision.pack_generated"

    def test_mistake_events(self) -> None:
        assert EventTypes.MISTAKE_LOGGED == "mistake.logged"
        assert EventTypes.CONCEPT_GAP_DETECTED == "concept_gap.detected"
        assert EventTypes.MISTAKE_PATTERN_FOUND == "mistake.pattern_found"

    def test_mock_test_events(self) -> None:
        assert EventTypes.MOCK_TEST_STARTED == "mock_test.started"
        assert EventTypes.MOCK_TEST_FINISHED == "mock_test.finished"
        assert EventTypes.MOCK_TEST_SCORED == "mock_test.scored"

    def test_prediction_events(self) -> None:
        assert EventTypes.PREDICTION_UPDATED == "prediction.updated"
        assert EventTypes.BURNOUT_ALERT == "burnout.alert"

    def test_achievement_events(self) -> None:
        assert EventTypes.ACHIEVEMENT_UNLOCKED == "achievement.unlocked"
        assert EventTypes.STREAK_UPDATED == "streak.updated"

    def test_system_events(self) -> None:
        assert EventTypes.SYSTEM_ERROR == "system.error"
        assert EventTypes.SYSTEM_COST_ALERT == "system.cost_alert"

    def test_total_event_types(self) -> None:
        attrs = [a for a in dir(EventTypes) if not a.startswith("_")]
        assert len(attrs) == 24


class TestStudyOSEvent:
    def test_create_event(self) -> None:
        profile_id = uuid4()
        event = StudyOSEvent(
            event_type="study.completed",
            category=EventCategory.STUDY,
            profile_id=profile_id,
        )
        assert event.event_type == "study.completed"
        assert event.category == EventCategory.STUDY
        assert event.profile_id == profile_id
        assert event.payload == {}
        assert event.priority == EventPriority.NORMAL
        assert event.correlation_id is None
        assert event.idempotency_key is None
        assert isinstance(event.event_id, UUID)

    def test_event_is_immutable(self) -> None:
        event = StudyOSEvent(
            event_type="test.event",
            category=EventCategory.SYSTEM,
            profile_id=uuid4(),
        )
        with pytest.raises(Exception):
            event.event_type = "modified"

    def test_event_with_payload(self) -> None:
        event = StudyOSEvent(
            event_type="quiz.finished",
            category=EventCategory.QUIZ,
            profile_id=uuid4(),
            payload={"score": 85, "total": 100},
        )
        assert event.payload == {"score": 85, "total": 100}

    def test_event_with_priority(self) -> None:
        event = StudyOSEvent(
            event_type="system.error",
            category=EventCategory.SYSTEM,
            profile_id=uuid4(),
            priority=EventPriority.CRITICAL,
        )
        assert event.priority == EventPriority.CRITICAL

    def test_event_with_correlation_id(self) -> None:
        corr_id = uuid4()
        event = StudyOSEvent(
            event_type="roadmap.generated",
            category=EventCategory.ROADMAP,
            profile_id=uuid4(),
            correlation_id=corr_id,
        )
        assert event.correlation_id == corr_id

    def test_event_with_idempotency_key(self) -> None:
        event = StudyOSEvent(
            event_type="study.completed",
            category=EventCategory.STUDY,
            profile_id=uuid4(),
            idempotency_key="study-123-2026-05-18",
        )
        assert event.idempotency_key == "study-123-2026-05-18"

    def test_to_dict(self) -> None:
        profile_id = uuid4()
        event_id = uuid4()
        corr_id = uuid4()
        event = StudyOSEvent(
            event_type="quiz.finished",
            category=EventCategory.QUIZ,
            profile_id=profile_id,
            payload={"score": 90},
            event_id=event_id,
            priority=EventPriority.HIGH,
            correlation_id=corr_id,
            idempotency_key="quiz-456",
        )
        d = event.to_dict()
        assert d["event_id"] == str(event_id)
        assert d["event_type"] == "quiz.finished"
        assert d["category"] == "quiz"
        assert d["profile_id"] == str(profile_id)
        assert d["payload"] == {"score": 90}
        assert d["priority"] == "high"
        assert d["correlation_id"] == str(corr_id)
        assert d["idempotency_key"] == "quiz-456"

    def test_to_dict_without_optional_fields(self) -> None:
        profile_id = uuid4()
        event = StudyOSEvent(
            event_type="study.completed",
            category=EventCategory.STUDY,
            profile_id=profile_id,
        )
        d = event.to_dict()
        assert d["correlation_id"] is None
        assert d["idempotency_key"] is None

    def test_from_dict(self) -> None:
        profile_id = uuid4()
        event_id = uuid4()
        corr_id = uuid4()
        data = {
            "event_id": str(event_id),
            "event_type": "roadmap.generated",
            "category": "roadmap",
            "profile_id": str(profile_id),
            "payload": {"items": 5},
            "priority": "normal",
            "correlation_id": str(corr_id),
            "idempotency_key": "roadmap-789",
        }
        event = StudyOSEvent.from_dict(data)
        assert event.event_id == event_id
        assert event.event_type == "roadmap.generated"
        assert event.category == EventCategory.ROADMAP
        assert event.profile_id == profile_id
        assert event.payload == {"items": 5}
        assert event.priority == EventPriority.NORMAL
        assert event.correlation_id == corr_id
        assert event.idempotency_key == "roadmap-789"

    def test_from_dict_without_event_id(self) -> None:
        profile_id = uuid4()
        data = {
            "event_type": "mistake.logged",
            "category": "mistake",
            "profile_id": str(profile_id),
        }
        event = StudyOSEvent.from_dict(data)
        assert event.event_type == "mistake.logged"
        assert isinstance(event.event_id, UUID)

    def test_from_dict_without_optional_fields(self) -> None:
        profile_id = uuid4()
        data = {
            "event_type": "achievement.unlocked",
            "category": "achievement",
            "profile_id": str(profile_id),
        }
        event = StudyOSEvent.from_dict(data)
        assert event.correlation_id is None
        assert event.idempotency_key is None
        assert event.payload == {}

    def test_roundtrip(self) -> None:
        profile_id = uuid4()
        original = StudyOSEvent(
            event_type="mock_test.scored",
            category=EventCategory.MOCK_TEST,
            profile_id=profile_id,
            payload={"score": 720, "max": 720},
            priority=EventPriority.HIGH,
            idempotency_key="mock-001",
        )
        restored = StudyOSEvent.from_dict(original.to_dict())
        assert restored.event_type == original.event_type
        assert restored.category == original.category
        assert restored.profile_id == original.profile_id
        assert restored.payload == original.payload
        assert restored.priority == original.priority
        assert restored.idempotency_key == original.idempotency_key
