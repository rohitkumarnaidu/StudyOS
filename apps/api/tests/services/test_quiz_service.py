"""Tests for quiz_service."""

from studyos_api.services.quiz_service import QuizService, QuizSession, MistakeEntry


class TestQuizSessionModel:
    def test_to_dict(self):
        session = QuizSession(
            id="sess-1",
            profile_id="user-1",
            quiz_type="practice",
            chapter_id=None,
            topic_ids=None,
            question_count=10,
            time_limit_minutes=None,
            difficulty=2,
            started_at="2024-01-01T00:00:00",
        )
        result = session.to_dict()
        assert result["id"] == "sess-1"
        assert result["quiz_type"] == "practice"
        assert result["total_questions"] == 10

    def test_to_dict_with_questions(self):
        session = QuizSession(
            id="sess-2",
            profile_id="user-1",
            quiz_type="timed",
            chapter_id="ch-1",
            topic_ids=None,
            question_count=5,
            time_limit_minutes=30,
            difficulty=3,
            started_at="2024-01-01T00:00:00",
            completed_at="2024-01-01T01:00:00",
            score=85.0,
        )
        result = session.to_dict()
        assert result["id"] == "sess-2"
        assert result["score"] == 85.0
        assert result["completed_at"] is not None


class TestMistakeEntryModel:
    def test_to_dict(self):
        mistake = MistakeEntry(
            id="mist-1",
            profile_id="user-1",
            question_id="q1",
            question_text="What is 2+2?",
            user_answer="B",
            correct_answer="A",
            explanation="2+2=4",
        )
        result = mistake.to_dict()
        assert result["id"] == "mist-1"
        assert result["question_id"] == "q1"
        assert result["user_answer"] == "B"
        assert result["correct_answer"] == "A"
        assert result["reviewed"] is False


class TestQuizService:
    def test_create_session(self):
        svc = QuizService()
        session = svc.create_session(
            profile_id="user-1",
            chapter_id=None,
            topic_ids=None,
            question_count=5,
            quiz_type="practice",
            time_limit_minutes=None,
            difficulty=2,
        )
        assert session is not None
        assert hasattr(session, "id")

    def test_get_session_not_found(self):
        svc = QuizService()
        result = svc.get_session("nonexistent", "user-1")
        assert result is None

    def test_submit_answer_no_session(self):
        svc = QuizService()
        result = svc.submit_answer(
            session_id="nonexistent",
            profile_id="user-1",
            question_id="q1",
            answer="A",
        )
        assert result is None

    def test_finish_session_not_found(self):
        svc = QuizService()
        result = svc.finish_session("nonexistent", "user-1")
        assert result is None

    def test_get_result_not_found(self):
        svc = QuizService()
        result = svc.get_result("nonexistent", "user-1")
        assert result is None

    def test_list_sessions_empty(self):
        svc = QuizService()
        result = svc.list_sessions("user-1")
        assert result == []

    def test_list_mistakes_empty(self):
        svc = QuizService()
        result = svc.list_mistakes("user-1")
        assert result == []

    def test_review_mistake_not_found(self):
        svc = QuizService()
        result = svc.review_mistake("nonexistent", "user-1")
        assert result is False

    def test_delete_mistake_not_found(self):
        svc = QuizService()
        result = svc.delete_mistake("nonexistent", "user-1")
        assert result is False

    def test_find_question_not_found(self):
        svc = QuizService()
        result = svc._find_question("nonexistent")
        assert result is None

    def test_create_and_get_session(self):
        svc = QuizService()
        session = svc.create_session(
            profile_id="user-1",
            chapter_id=None,
            topic_ids=None,
            question_count=3,
            quiz_type="practice",
            time_limit_minutes=None,
            difficulty=2,
        )
        session_id = session.id
        retrieved = svc.get_session(session_id, "user-1")
        assert retrieved is not None
        assert retrieved.id == session_id

    def test_create_timed_session(self):
        svc = QuizService()
        session = svc.create_session(
            profile_id="user-1",
            chapter_id=None,
            topic_ids=None,
            question_count=10,
            quiz_type="timed",
            time_limit_minutes=60,
            difficulty=3,
        )
        assert session is not None

    def test_create_mock_session(self):
        svc = QuizService()
        session = svc.create_session(
            profile_id="user-1",
            chapter_id=None,
            topic_ids=None,
            question_count=180,
            quiz_type="mock",
            time_limit_minutes=180,
            difficulty=4,
        )
        assert session is not None

    def test_select_questions_default(self):
        svc = QuizService()
        questions = svc.select_questions(count=5)
        assert len(questions) <= 5

    def test_select_questions_by_difficulty(self):
        svc = QuizService()
        questions = svc.select_questions(count=10, difficulty=2)
        assert all(q["difficulty"] == 2 for q in questions)

    def test_get_questions_for_session(self):
        svc = QuizService()
        session = svc.create_session(
            profile_id="user-1",
            chapter_id=None,
            topic_ids=None,
            question_count=3,
            quiz_type="practice",
            time_limit_minutes=None,
            difficulty=2,
        )
        questions = svc.get_questions(session.id, "user-1")
        assert questions is not None
        assert len(questions) > 0
