"""Tests for revision pack generator and active recall engine."""

import pytest

from studyos_api.services.active_recall import ActiveRecallEngine, RecallSession
from studyos_api.services.revision_pack_generator import RevisionPack, RevisionPackGenerator


class TestRevisionPackGenerator:
    @pytest.fixture
    def generator(self) -> RevisionPackGenerator:
        return RevisionPackGenerator()

    def test_generate_due_pack(self, generator: RevisionPackGenerator) -> None:
        due_items = [
            {"item_id": "t1", "next_review": "2026-05-18"},
            {"item_id": "t2", "next_review": "2026-05-19"},
            {"item_id": "t3", "next_review": "2026-05-17"},
        ]
        pack = generator.generate_due_pack("pack-1", due_items, max_items=2)
        assert pack.pack_id == "pack-1"
        assert pack.pack_type == "due_review"
        assert len(pack.items) == 2

    def test_generate_weak_pack(self, generator: RevisionPackGenerator) -> None:
        weak_items = [
            {"item_id": "t1", "retention_score": 0.3},
            {"item_id": "t2", "retention_score": 0.6},
            {"item_id": "t3", "retention_score": 0.2},
        ]
        pack = generator.generate_weak_pack("pack-2", weak_items, max_items=2)
        assert pack.pack_type == "weak_focus"
        assert len(pack.items) == 2
        assert pack.items[0]["retention_score"] <= pack.items[1]["retention_score"]

    def test_generate_mixed_pack(self, generator: RevisionPackGenerator) -> None:
        due = [{"item_id": f"d{i}"} for i in range(10)]
        weak = [{"item_id": f"w{i}", "retention_score": 0.3} for i in range(10)]
        pack = generator.generate_mixed_pack("pack-3", due, weak, max_items=10, weak_ratio=0.4)
        assert pack.pack_type == "mixed"
        assert len(pack.items) == 10
        assert pack.metadata["weak_items"] == 4
        assert pack.metadata["due_items"] == 6

    def test_generate_cram_pack(self, generator: RevisionPackGenerator) -> None:
        all_items = [{"item_id": f"t{i}", "retention_score": 0.5} for i in range(100)]
        pack = generator.generate_cram_pack("pack-4", all_items, max_items=50)
        assert pack.pack_type == "cram"
        assert len(pack.items) == 50
        assert pack.metadata["strategy"] == "exam_cram"

    def test_get_pack(self, generator: RevisionPackGenerator) -> None:
        generator.generate_due_pack("pack-1", [{"item_id": "t1"}])
        pack = generator.get_pack("pack-1")
        assert pack is not None
        assert pack.pack_id == "pack-1"

    def test_get_pack_nonexistent(self, generator: RevisionPackGenerator) -> None:
        assert generator.get_pack("nonexistent") is None

    def test_list_packs(self, generator: RevisionPackGenerator) -> None:
        generator.generate_due_pack("p1", [{"item_id": "t1"}])
        generator.generate_weak_pack("p2", [{"item_id": "t2"}])
        packs = generator.list_packs()
        assert len(packs) == 2

    def test_delete_pack(self, generator: RevisionPackGenerator) -> None:
        generator.generate_due_pack("p1", [{"item_id": "t1"}])
        assert generator.delete_pack("p1") is True
        assert generator.get_pack("p1") is None

    def test_delete_pack_nonexistent(self, generator: RevisionPackGenerator) -> None:
        assert generator.delete_pack("nonexistent") is False

    def test_reset(self, generator: RevisionPackGenerator) -> None:
        generator.generate_due_pack("p1", [{"item_id": "t1"}])
        generator.reset()
        assert generator.list_packs() == []


class TestActiveRecallEngine:
    @pytest.fixture
    def engine(self) -> ActiveRecallEngine:
        return ActiveRecallEngine()

    def test_create_session(self, engine: ActiveRecallEngine) -> None:
        questions = [
            {"question_id": "q1", "question": "What is X?", "answer": "X is..."},
            {"question_id": "q2", "question": "What is Y?", "answer": "Y is..."},
        ]
        session = engine.create_session("sess-1", questions, "2026-05-19")
        assert session.session_id == "sess-1"
        assert len(session.questions) == 2
        assert session.current_index == 0

    def test_get_current_question(self, engine: ActiveRecallEngine) -> None:
        questions = [
            {"question_id": "q1", "question": "Q1?", "answer": "A1"},
        ]
        engine.create_session("sess-1", questions, "2026-05-19")
        q = engine.get_current_question("sess-1")
        assert q is not None
        assert q.question_id == "q1"

    def test_submit_answer_correct(self, engine: ActiveRecallEngine) -> None:
        questions = [{"question_id": "q1", "question": "Q?", "answer": "A"}]
        engine.create_session("sess-1", questions, "2026-05-19")
        result = engine.submit_answer("sess-1", "user answer", True)
        assert result["correct"] is True
        assert result["session_progress"]["score"] == 1
        assert result["session_progress"]["accuracy"] == 1.0

    def test_submit_answer_incorrect(self, engine: ActiveRecallEngine) -> None:
        questions = [{"question_id": "q1", "question": "Q?", "answer": "Correct Answer"}]
        engine.create_session("sess-1", questions, "2026-05-19")
        result = engine.submit_answer("sess-1", "wrong", False)
        assert result["correct"] is False
        assert result["correct_answer"] == "Correct Answer"

    def test_session_completion(self, engine: ActiveRecallEngine) -> None:
        questions = [
            {"question_id": "q1", "question": "Q1?", "answer": "A1"},
            {"question_id": "q2", "question": "Q2?", "answer": "A2"},
        ]
        engine.create_session("sess-1", questions, "2026-05-19")
        engine.submit_answer("sess-1", "a1", True)
        result = engine.submit_answer("sess-1", "a2", True)
        assert result["session_complete"] is True
        assert result["final_accuracy"] == 1.0

    def test_submit_answer_completed_session(self, engine: ActiveRecallEngine) -> None:
        questions = [{"question_id": "q1", "question": "Q?", "answer": "A"}]
        engine.create_session("sess-1", questions, "2026-05-19")
        engine.submit_answer("sess-1", "a", True)
        result = engine.submit_answer("sess-1", "a", True)
        assert "error" in result

    def test_get_session(self, engine: ActiveRecallEngine) -> None:
        engine.create_session("sess-1", [{"question_id": "q1", "question": "Q?", "answer": "A"}], "2026-05-19")
        session = engine.get_session("sess-1")
        assert session is not None
        assert session.session_id == "sess-1"

    def test_get_session_results(self, engine: ActiveRecallEngine) -> None:
        questions = [{"question_id": "q1", "question": "Q?", "answer": "A"}]
        engine.create_session("sess-1", questions, "2026-05-19")
        assert engine.get_session_results("sess-1") is None
        engine.submit_answer("sess-1", "a", True)
        results = engine.get_session_results("sess-1")
        assert results is not None
        assert results["score"] == 1

    def test_list_sessions(self, engine: ActiveRecallEngine) -> None:
        engine.create_session("s1", [{"question_id": "q1", "question": "Q?", "answer": "A"}], "2026-05-19")
        engine.create_session("s2", [{"question_id": "q1", "question": "Q?", "answer": "A"}], "2026-05-19")
        sessions = engine.list_sessions()
        assert len(sessions) == 2

    def test_delete_session(self, engine: ActiveRecallEngine) -> None:
        engine.create_session("s1", [{"question_id": "q1", "question": "Q?", "answer": "A"}], "2026-05-19")
        assert engine.delete_session("s1") is True
        assert engine.get_session("s1") is None

    def test_reset(self, engine: ActiveRecallEngine) -> None:
        engine.create_session("s1", [{"question_id": "q1", "question": "Q?", "answer": "A"}], "2026-05-19")
        engine.reset()
        assert engine.list_sessions() == []
