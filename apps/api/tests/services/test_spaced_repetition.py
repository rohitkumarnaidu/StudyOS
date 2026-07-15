"""Tests for spaced repetition service (SM-2 algorithm)."""

import pytest

from studyos_api.services.spaced_repetition import SM2Item, SpacedRepetitionEngine


class TestSM2Item:
    def test_create_item(self) -> None:
        item = SM2Item(item_id="topic-1")
        assert item.item_id == "topic-1"
        assert item.ease_factor == 2.5
        assert item.interval == 0
        assert item.repetitions == 0

    def test_item_to_dict(self) -> None:
        item = SM2Item(
            item_id="topic-1",
            ease_factor=2.6,
            interval=5,
            repetitions=2,
            next_review="2026-05-20",
            last_quality=4.0,
        )
        d = item.to_dict()
        assert d["item_id"] == "topic-1"
        assert d["ease_factor"] == 2.6
        assert d["interval"] == 5

    def test_item_from_dict(self) -> None:
        data = {
            "item_id": "topic-2",
            "ease_factor": 2.8,
            "interval": 10,
            "repetitions": 3,
            "next_review": "2026-05-25",
            "last_quality": 5.0,
        }
        item = SM2Item.from_dict(data)
        assert item.item_id == "topic-2"
        assert item.ease_factor == 2.8


class TestSpacedRepetitionEngine:
    @pytest.fixture
    def engine(self) -> SpacedRepetitionEngine:
        return SpacedRepetitionEngine()

    def test_review_perfect_score(self, engine: SpacedRepetitionEngine) -> None:
        item = SM2Item(item_id="t1")
        result = engine.review(item, 5.0, "2026-05-19")
        assert result.repetitions == 1
        assert result.interval == 1
        assert result.ease_factor > 2.5

    def test_review_good_score(self, engine: SpacedRepetitionEngine) -> None:
        item = SM2Item(item_id="t1")
        result = engine.review(item, 4.0, "2026-05-19")
        assert result.repetitions == 1
        assert result.interval == 1

    def test_review_poor_score_resets(self, engine: SpacedRepetitionEngine) -> None:
        item = SM2Item(item_id="t1", repetitions=5, interval=20, ease_factor=2.8)
        result = engine.review(item, 2.0, "2026-05-19")
        assert result.repetitions == 0
        assert result.interval == 1

    def test_review_increases_interval(self, engine: SpacedRepetitionEngine) -> None:
        item = SM2Item(item_id="t1", repetitions=2, interval=6, ease_factor=2.5)
        result = engine.review(item, 4.0, "2026-05-19")
        assert result.interval == round(6 * 2.5)
        assert result.repetitions == 3

    def test_review_clamps_quality(self, engine: SpacedRepetitionEngine) -> None:
        item = SM2Item(item_id="t1")
        r1 = engine.review(item, 10.0, "2026-05-19")
        r2 = engine.review(SM2Item(item_id="t2"), -5.0, "2026-05-19")
        assert r1.last_quality == 5.0
        assert r2.last_quality == 0.0

    def test_review_minimum_ease_factor(self, engine: SpacedRepetitionEngine) -> None:
        item = SM2Item(item_id="t1", ease_factor=1.5, repetitions=2, interval=10)
        result = engine.review(item, 3.0, "2026-05-19")
        assert result.ease_factor >= 1.3

    def test_get_due_items(self, engine: SpacedRepetitionEngine) -> None:
        items = [
            SM2Item(item_id="t1", next_review="2026-05-18"),
            SM2Item(item_id="t2", next_review="2026-05-19"),
            SM2Item(item_id="t3", next_review="2026-05-20"),
        ]
        due = engine.get_due_items(items, "2026-05-19")
        assert len(due) == 2
        assert {i.item_id for i in due} == {"t1", "t2"}

    def test_get_overdue_items(self, engine: SpacedRepetitionEngine) -> None:
        items = [
            SM2Item(item_id="t1", next_review="2026-05-18"),
            SM2Item(item_id="t2", next_review="2026-05-19"),
        ]
        overdue = engine.get_overdue_items(items, "2026-05-19")
        assert len(overdue) == 1
        assert overdue[0].item_id == "t1"

    def test_get_predicted_retention(self, engine: SpacedRepetitionEngine) -> None:
        item = SM2Item(item_id="t1", interval=10, ease_factor=2.5)
        r1 = engine.get_predicted_retention(item, 0)
        r2 = engine.get_predicted_retention(item, 10)
        r3 = engine.get_predicted_retention(item, 50)
        assert r1 == 1.0
        assert r2 > r3
        assert 0.0 <= r3 < 1.0

    def test_create_new_item(self, engine: SpacedRepetitionEngine) -> None:
        item = engine.create_new_item("new-topic", "2026-05-19")
        assert item.item_id == "new-topic"
        assert item.next_review == "2026-05-19"
        assert item.repetitions == 0

    def test_get_review_stats(self, engine: SpacedRepetitionEngine) -> None:
        items = [
            SM2Item(item_id="t1", next_review="2026-05-18", ease_factor=2.5, interval=5),
            SM2Item(item_id="t2", next_review="2026-05-19", ease_factor=2.8, interval=10),
            SM2Item(item_id="t3", next_review="2026-05-20", ease_factor=2.0, interval=3),
        ]
        stats = engine.get_review_stats(items, "2026-05-19")
        assert stats["total_items"] == 3
        assert stats["due_today"] == 2
        assert stats["overdue"] == 1
        assert stats["upcoming"] == 1

    def test_add_days(self, engine: SpacedRepetitionEngine) -> None:
        assert engine._add_days("2026-05-19", 1) == "2026-05-20"
        assert engine._add_days("2026-05-19", 7) == "2026-05-26"
        assert engine._add_days("2026-12-31", 1) == "2027-01-01"
