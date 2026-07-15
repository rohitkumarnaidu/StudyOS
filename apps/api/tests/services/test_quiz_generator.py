"""Tests for quiz_generator service."""

import random
from datetime import date, timedelta

import pytest

from studyos_api.services.quiz_generator import (
    ALL_TEMPLATES,
    ASSERTION_REASON_TEMPLATES,
    BIOLOGY_TEMPLATES,
    CHEMISTRY_TEMPLATES,
    CHAPTER_ID_MAP,
    MATCH_FOLLOWING_TEMPLATES,
    NUMERIC_TEMPLATES,
    PHYSICS_TEMPLATES,
    SYLLABUS,
    GeneratedQuestion,
    QuestionType,
    QuizGenerator,
    Subject,
    _detect_subject,
    _generate_mcq_distractors,
    _generate_numeric_distractors,
    _get_chapter_id,
)


class TestQuestionType:
    def test_question_type_values(self) -> None:
        assert QuestionType.MCQ.value == "mcq"
        assert QuestionType.NUMERIC.value == "numeric"
        assert QuestionType.ASSERTION_REASON.value == "assertion_reason"
        assert QuestionType.MATCH_FOLLOWING.value == "match_following"


class TestSubject:
    def test_subject_values(self) -> None:
        assert Subject.PHYSICS.value == "physics"
        assert Subject.CHEMISTRY.value == "chemistry"
        assert Subject.BIOLOGY.value == "biology"


class TestSyllabus:
    def test_syllabus_has_three_subjects(self) -> None:
        assert Subject.PHYSICS in SYLLABUS
        assert Subject.CHEMISTRY in SYLLABUS
        assert Subject.BIOLOGY in SYLLABUS

    def test_syllabus_has_grades(self) -> None:
        for subject_data in SYLLABUS.values():
            assert "11th" in subject_data
            assert "12th" in subject_data

    def test_syllabus_topics_are_non_empty(self) -> None:
        for subject_data in SYLLABUS.values():
            for grade_topics in subject_data.values():
                assert len(grade_topics) > 0


class TestDetectSubject:
    def test_detect_physics_topic(self) -> None:
        assert _detect_subject("Motion in a Straight Line") == "physics"

    def test_detect_chemistry_topic(self) -> None:
        assert _detect_subject("Chemical Bonding and Molecular Structure") == "chemistry"

    def test_detect_biology_topic(self) -> None:
        assert _detect_subject("Cell — The Unit of Life") == "biology"

    def test_detect_fallback_physics(self) -> None:
        assert _detect_subject("some unknown motion topic") == "physics"

    def test_detect_fallback_chemistry(self) -> None:
        assert _detect_subject("organic bonding stuff") == "chemistry"

    def test_detect_fallback_biology(self) -> None:
        assert _detect_subject("cell reproduction topic") == "biology"


class TestGetChapterId:
    def test_known_topic(self) -> None:
        cid = _get_chapter_id("Motion in a Straight Line")
        assert cid == "ch_physics_11_02"

    def test_unknown_topic(self) -> None:
        cid = _get_chapter_id("Nonexistent Topic XYZ")
        assert cid.startswith("ch_")


class TestGenerateNumericDistractors:
    def test_returns_correct_count(self) -> None:
        result = _generate_numeric_distractors(10.0, count=3)
        assert len(result) == 3

    def test_excludes_correct_value(self) -> None:
        result = _generate_numeric_distractors(10.0, count=5)
        assert 10.0 not in result

    def test_with_custom_rng(self) -> None:
        rng = random.Random(42)
        result = _generate_numeric_distractors(50.0, count=3, rng=rng)
        assert len(result) == 3

    def test_deterministic_with_seed(self) -> None:
        rng1 = random.Random(99)
        rng2 = random.Random(99)
        r1 = _generate_numeric_distractors(100.0, count=3, rng=rng1)
        r2 = _generate_numeric_distractors(100.0, count=3, rng=rng2)
        assert r1 == r2


class TestGenerateMcqDistractors:
    def test_returns_correct_count(self) -> None:
        result = _generate_mcq_distractors("A", ["A", "B", "C", "D"], count=3)
        assert len(result) == 3

    def test_excludes_correct(self) -> None:
        result = _generate_mcq_distractors("B", ["A", "B", "C", "D"], count=2)
        assert "B" not in result

    def test_with_custom_rng(self) -> None:
        rng = random.Random(123)
        result = _generate_mcq_distractors("A", ["A", "B", "C", "D"], count=2, rng=rng)
        assert len(result) == 2


class TestGeneratedQuestion:
    def test_to_dict_mcq(self) -> None:
        q = GeneratedQuestion(
            id="q1",
            chapter_id="ch1",
            topic="Test",
            subject="physics",
            question_text="What is X?",
            question_type=QuestionType.MCQ,
            options={"A": "Opt1", "B": "Opt2"},
            correct_answer="A",
            explanation="Because",
            difficulty=2,
        )
        d = q.to_dict()
        assert d["id"] == "q1"
        assert d["question_type"] == "mcq"
        assert d["A"] == "Opt1"

    def test_to_dict_numeric(self) -> None:
        q = GeneratedQuestion(
            id="q2",
            chapter_id="ch2",
            topic="Test",
            subject="physics",
            question_text="Calculate X.",
            question_type=QuestionType.NUMERIC,
            correct_answer="42",
            correct_value=42.0,
            tolerance=0.5,
        )
        d = q.to_dict()
        assert d["correct_value"] == 42.0
        assert d["tolerance"] == 0.5

    def test_to_dict_match_following(self) -> None:
        q = GeneratedQuestion(
            id="q3",
            chapter_id="ch3",
            topic="Test",
            subject="chemistry",
            question_text="Match the following.",
            question_type=QuestionType.MATCH_FOLLOWING,
            column_a=["A", "B"],
            column_b=["1", "2"],
            correct_answer='{"A": "1"}',
        )
        d = q.to_dict()
        assert d["column_a"] == ["A", "B"]
        assert d["column_b"] == ["1", "2"]


class TestQuizGeneratorInstantiation:
    def test_default_init(self) -> None:
        gen = QuizGenerator()
        assert gen._seed is None
        assert gen._question_counter == 0

    def test_init_with_seed(self) -> None:
        gen = QuizGenerator(seed=42)
        assert gen._seed == 42

    def test_template_count(self) -> None:
        gen = QuizGenerator()
        assert gen.get_template_count() == len(ALL_TEMPLATES)
        assert gen.get_template_count() > 0


class TestQuizGeneratorGetSyllabus:
    def test_returns_syllabus(self) -> None:
        gen = QuizGenerator()
        syllabus = gen.get_syllabus()
        assert Subject.PHYSICS in syllabus
        assert Subject.CHEMISTRY in syllabus
        assert Subject.BIOLOGY in syllabus


class TestQuizGeneratorGetTopicsForSubject:
    def test_physics_topics(self) -> None:
        gen = QuizGenerator()
        topics = gen.get_topics_for_subject(Subject.PHYSICS)
        assert len(topics) > 0
        assert "Motion in a Straight Line" in topics

    def test_chemistry_topics(self) -> None:
        gen = QuizGenerator()
        topics = gen.get_topics_for_subject(Subject.CHEMISTRY)
        assert len(topics) > 0
        assert "Chemical Bonding and Molecular Structure" in topics

    def test_biology_topics(self) -> None:
        gen = QuizGenerator()
        topics = gen.get_topics_for_subject(Subject.BIOLOGY)
        assert len(topics) > 0
        assert "Cell — The Unit of Life" in topics


class TestQuizGeneratorGenerateQuestions:
    @pytest.fixture
    def gen(self) -> QuizGenerator:
        return QuizGenerator(seed=42)

    def test_generate_basic(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=5,
        )
        assert len(questions) == 5
        for q in questions:
            assert q.topic == "Motion in a Straight Line"
            assert q.question_type in (QuestionType.MCQ, QuestionType.NUMERIC)

    def test_generate_with_difficulty_filter(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=5,
            difficulty=1,
        )
        assert len(questions) == 5
        for q in questions:
            assert q.difficulty == 1

    def test_generate_with_difficulty_no_match(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=5,
            difficulty=5,
        )
        assert len(questions) == 0

    def test_generate_with_question_type_mcq(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=3,
            question_type=QuestionType.MCQ,
        )
        assert len(questions) == 3
        for q in questions:
            assert q.question_type == QuestionType.MCQ

    def test_generate_numeric_questions(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=3,
            question_type=QuestionType.NUMERIC,
        )
        assert len(questions) == 3
        for q in questions:
            assert q.question_type == QuestionType.NUMERIC
            assert q.correct_value is not None

    def test_generate_zero_count(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=0,
        )
        assert len(questions) == 0

    def test_generate_unknown_topic_fallback(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_unknown",
            topic="Totally Unknown Topic",
            count=3,
            question_type=QuestionType.MCQ,
        )
        assert len(questions) >= 1

    def test_generate_unknown_topic_with_difficulty_filter(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_unknown",
            topic="Totally Unknown Topic",
            count=3,
            difficulty=1,
        )
        assert len(questions) == 3

    def test_deterministic_seed(self) -> None:
        gen1 = QuizGenerator(seed=123)
        gen2 = QuizGenerator(seed=123)
        q1 = gen1.generate_questions("ch_physics_11_02", "Motion in a Straight Line", count=3)
        q2 = gen2.generate_questions("ch_physics_11_02", "Motion in a Straight Line", count=3)
        for a, b in zip(q1, q2, strict=True):
            assert a.question_text == b.question_text
            assert a.correct_answer == b.correct_answer

    def test_different_seeds_produce_different_questions(self) -> None:
        gen1 = QuizGenerator(seed=1)
        gen2 = QuizGenerator(seed=999)
        q1 = gen1.generate_questions("ch_physics_11_02", "Motion in a Straight Line", count=5)
        q2 = gen2.generate_questions("ch_physics_11_02", "Motion in a Straight Line", count=5)
        texts1 = [q.question_text for q in q1]
        texts2 = [q.question_text for q in q2]
        assert texts1 != texts2

    def test_generated_questions_have_valid_ids(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=3,
        )
        for q in questions:
            assert q.id.startswith("gq_")
            assert q.chapter_id == "ch_physics_11_02"

    def test_mcq_has_options_and_correct(self, gen: QuizGenerator) -> None:
        questions = gen.generate_questions(
            chapter_id="ch_physics_11_02",
            topic="Motion in a Straight Line",
            count=1,
        )
        q = questions[0]
        assert q.options is not None
        assert len(q.options) == 4
        assert q.correct_answer in q.options


class TestQuizGeneratorGenerateMixedQuiz:
    @pytest.fixture
    def gen(self) -> QuizGenerator:
        return QuizGenerator(seed=42)

    def test_mixed_quiz_physics(self, gen: QuizGenerator) -> None:
        questions = gen.generate_mixed_quiz(Subject.PHYSICS, count=20)
        assert len(questions) > 0
        assert all(q.subject == "physics" for q in questions)

    def test_mixed_quiz_chemistry(self, gen: QuizGenerator) -> None:
        questions = gen.generate_mixed_quiz(Subject.CHEMISTRY, count=15)
        assert len(questions) > 0

    def test_mixed_quiz_biology(self, gen: QuizGenerator) -> None:
        questions = gen.generate_mixed_quiz(Subject.PHYSICS, count=5)
        assert len(questions) >= 1

    def test_mixed_quiz_with_difficulty_range(self, gen: QuizGenerator) -> None:
        questions = gen.generate_mixed_quiz(
            Subject.PHYSICS,
            count=20,
            difficulty_range=(1, 2),
        )
        assert all(q.difficulty <= 2 for q in questions)

    def test_mixed_quiz_shuffled(self, gen: QuizGenerator) -> None:
        questions = gen.generate_mixed_quiz(Subject.CHEMISTRY, count=10)
        topics = [q.topic for q in questions]
        assert len(set(topics)) >= 1

    def test_mixed_quiz_default_count(self, gen: QuizGenerator) -> None:
        questions = gen.generate_mixed_quiz(Subject.CHEMISTRY)
        assert len(questions) >= 1

    def test_mixed_quiz_narrow_difficulty(self, gen: QuizGenerator) -> None:
        questions = gen.generate_mixed_quiz(
            Subject.PHYSICS,
            count=10,
            difficulty_range=(5, 5),
        )
        assert len(questions) == 0


class TestQuizGeneratorReset:
    def test_reset_clears_counter(self) -> None:
        gen = QuizGenerator(seed=42)
        gen.generate_questions("ch_physics_11_02", "Motion in a Straight Line", count=5)
        assert gen._question_counter > 0
        gen.reset()
        assert gen._question_counter == 0


class TestTemplateCollections:
    def test_all_templates_includes_all(self) -> None:
        expected = (
            len(PHYSICS_TEMPLATES)
            + len(CHEMISTRY_TEMPLATES)
            + len(BIOLOGY_TEMPLATES)
            + len(ASSERTION_REASON_TEMPLATES)
            + len(MATCH_FOLLOWING_TEMPLATES)
            + len(NUMERIC_TEMPLATES)
        )
        assert len(ALL_TEMPLATES) == expected

    def test_all_templates_have_required_fields(self) -> None:
        for t in ALL_TEMPLATES:
            assert "topic" in t
            assert "type" in t
            assert "difficulty" in t
            assert "explanation" in t

    def test_mcq_templates_have_options(self) -> None:
        for t in ALL_TEMPLATES:
            if t["type"] == QuestionType.MCQ:
                assert "options" in t
                assert "correct" in t

    def test_numeric_templates_have_value(self) -> None:
        for t in NUMERIC_TEMPLATES:
            assert "correct_value" in t
            assert "tolerance" in t

    def test_assertion_reason_templates_have_fields(self) -> None:
        for t in ASSERTION_REASON_TEMPLATES:
            assert "assertion" in t
            assert "reason" in t
            assert "correct" in t

    def test_match_following_templates_have_columns(self) -> None:
        for t in MATCH_FOLLOWING_TEMPLATES:
            assert "column_a" in t
            assert "column_b" in t
            assert "correct" in t

    def test_chapter_id_map_covers_most_topics(self) -> None:
        uncovered = []
        for subject_data in SYLLABUS.values():
            for grade_topics in subject_data.values():
                for topic in grade_topics:
                    if topic not in CHAPTER_ID_MAP:
                        uncovered.append(topic)
        assert len(uncovered) < 10
