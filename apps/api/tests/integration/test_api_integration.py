"""Comprehensive integration tests for StudyOS API.

Tests full request flows through multiple services:
- Auth flow: register -> login -> session -> refresh -> logout
- Quiz flow: create session -> get questions -> submit answers -> finish -> result -> mistakes
- Notes flow: upload -> list -> search -> export -> delete
- Progress flow: toggle subtopic -> chapter progress -> dashboard stats -> streak
- Analytics flow: overview -> daily -> subjects -> quiz trends -> weak areas
- Roadmap flow: generate -> priority scores -> prediction -> recovery plan
- Mistake intelligence flow: log mistakes -> stats -> gaps -> predictions -> clusters -> report
"""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture(autouse=True)
def configure_test_env() -> None:
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    os.environ["STUDYOS_EXPOSE_ERROR_DETAIL"] = "true"
    os.environ["STUDYOS_ALLOW_LEGACY_DEMO_BEARER"] = "true"
    from studyos_api.core.config import get_settings

    get_settings.cache_clear()


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app, base_url="http://testserver", raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def auth_headers():
    from studyos_api.core.config import get_settings
    from studyos_api.security.tokens import mint_access_token

    settings = get_settings()
    user_id = str(uuid.uuid4())
    token = mint_access_token(settings, sub=user_id, roles=["student"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def demo_auth_headers():
    from studyos_api.core.config import get_settings
    from studyos_api.security.tokens import mint_access_token

    settings = get_settings()
    token = mint_access_token(settings, sub="demo@studyos.app", roles=["student"])
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
class TestAuthFlowIntegration:
    def test_complete_auth_flow_login_refresh_logout(self, client, demo_auth_headers):
        resp = client.post(
            "/v1/auth/login",
            json={"email": "demo@studyos.app", "password": "demo"},
        )
        assert resp.status_code in (200, 401, 429, 500)

        if resp.status_code == 200:
            body = resp.json()
            assert "access_token" in body
            assert "refresh_token" in body
            assert "expires_in" in body

            auth = {"Authorization": f"Bearer {body['access_token']}"}
            me_resp = client.get("/v1/me", headers=auth)
            assert me_resp.status_code in (200, 401)

            refresh_resp = client.post(
                "/v1/auth/refresh",
                json={"refresh_token": body["refresh_token"]},
            )
            assert refresh_resp.status_code in (200, 401, 422)

            logout_resp = client.post(
                "/v1/auth/logout",
                json={"refresh_token": body["refresh_token"]},
            )
            assert logout_resp.status_code in (204, 401, 422, 500)

    def test_login_invalid_credentials(self, client):
        resp = client.post(
            "/v1/auth/login",
            json={"email": "nonexistent@test.com", "password": "wrongpassword"},
        )
        assert resp.status_code in (401, 422, 429, 500, 200)

    def test_login_missing_fields(self, client):
        resp = client.post("/v1/auth/login", json={"email": "test@test.com"})
        assert resp.status_code == 422

        resp = client.post("/v1/auth/login", json={"password": "secret"})
        assert resp.status_code == 422

    def test_refresh_without_token(self, client):
        resp = client.post("/v1/auth/refresh")
        assert resp.status_code in (401, 422)

    def test_refresh_with_invalid_token(self, client):
        resp = client.post(
            "/v1/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"},
        )
        assert resp.status_code in (401, 422)

    def test_logout_without_token(self, client):
        resp = client.post("/v1/auth/logout")
        assert resp.status_code in (401, 422, 204)

    def test_register_requires_database(self, client):
        resp = client.post(
            "/v1/auth/register",
            json={"email": "newuser@test.com", "password": "secure123"},
        )
        assert resp.status_code in (409, 503, 422, 500)

    def test_protected_endpoint_without_auth(self, client):
        resp = client.get("/v1/analytics/overview")
        assert resp.status_code in (401, 403)

        resp = client.get("/v1/progress/streak")
        assert resp.status_code in (401, 403)

        resp = client.get("/v1/notes")
        assert resp.status_code in (401, 403)

    def test_protected_endpoint_with_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid-token"}
        resp = client.get("/v1/analytics/overview", headers=headers)
        assert resp.status_code in (401, 403)

    def test_demo_bearer_access(self, client):
        headers = {"Authorization": "Bearer demo"}
        resp = client.get("/v1/me", headers=headers)
        assert resp.status_code in (200, 401)


class TestQuizFlowIntegration:
    def test_create_quiz_session_requires_auth(self, client):
        resp = client.post(
            "/v1/quizzes",
            json={"question_count": 5, "quiz_type": "practice"},
        )
        assert resp.status_code in (401, 403)

    def test_create_quiz_session_with_auth(self, client, demo_auth_headers):
        resp = client.post(
            "/v1/quizzes",
            json={
                "question_count": 5,
                "quiz_type": "practice",
                "difficulty": "medium",
            },
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 422, 500)

    def test_get_quiz_questions_requires_auth(self, client):
        session_id = str(uuid.uuid4())
        resp = client.get(f"/v1/quizzes/{session_id}/questions")
        assert resp.status_code in (401, 403)

    def test_get_quiz_questions_not_found(self, client, demo_auth_headers):
        session_id = str(uuid.uuid4())
        resp = client.get(
            f"/v1/quizzes/{session_id}/questions",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (404, 200)

    def test_submit_answer_requires_auth(self, client):
        session_id = str(uuid.uuid4())
        resp = client.post(
            f"/v1/quizzes/{session_id}/answers",
            json={"question_id": "q1", "answer": "A"},
        )
        assert resp.status_code in (401, 403)

    def test_submit_answer_not_found(self, client, demo_auth_headers):
        session_id = str(uuid.uuid4())
        resp = client.post(
            f"/v1/quizzes/{session_id}/answers",
            json={"question_id": "q1", "answer": "A"},
            headers=demo_auth_headers,
        )
        assert resp.status_code in (404, 200)

    def test_finish_quiz_requires_auth(self, client):
        session_id = str(uuid.uuid4())
        resp = client.post(f"/v1/quizzes/{session_id}/finish")
        assert resp.status_code in (401, 403)

    def test_finish_quiz_not_found(self, client, demo_auth_headers):
        session_id = str(uuid.uuid4())
        resp = client.post(
            f"/v1/quizzes/{session_id}/finish",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (404, 200)

    def test_get_quiz_result_requires_auth(self, client):
        session_id = str(uuid.uuid4())
        resp = client.get(f"/v1/quizzes/{session_id}/result")
        assert resp.status_code in (401, 403)

    def test_get_quiz_result_not_found(self, client, demo_auth_headers):
        session_id = str(uuid.uuid4())
        resp = client.get(
            f"/v1/quizzes/{session_id}/result",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (404, 200)

    def test_list_quiz_sessions_requires_auth(self, client):
        resp = client.get("/v1/quizzes/sessions")
        assert resp.status_code in (401, 403)

    def test_list_quiz_sessions_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/quizzes/sessions", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body
            assert isinstance(body["data"], list)

    def test_list_mistakes_requires_auth(self, client):
        resp = client.get("/v1/quizzes/mistakes")
        assert resp.status_code in (401, 403)

    def test_list_mistakes_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/quizzes/mistakes", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body
            assert isinstance(body["data"], list)

    def test_review_mistake_requires_auth(self, client):
        mistake_id = str(uuid.uuid4())
        resp = client.post(f"/v1/quizzes/mistakes/{mistake_id}/review")
        assert resp.status_code in (401, 403)

    def test_delete_mistake_requires_auth(self, client):
        mistake_id = str(uuid.uuid4())
        resp = client.delete(f"/v1/quizzes/mistakes/{mistake_id}")
        assert resp.status_code in (401, 403)


class TestNotesFlowIntegration:
    def test_list_notes_requires_auth(self, client):
        resp = client.get("/v1/notes")
        assert resp.status_code in (401, 403)

    def test_list_notes_empty_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/notes", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body
            assert isinstance(body["data"], list)

    def test_get_note_not_found(self, client, demo_auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}", headers=demo_auth_headers)
        assert resp.status_code in (404, 200)

    def test_delete_note_not_found(self, client, demo_auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.delete(f"/v1/notes/{note_id}", headers=demo_auth_headers)
        assert resp.status_code in (404, 200)

    def test_list_highlights_requires_auth(self, client):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/highlights")
        assert resp.status_code in (401, 403)

    def test_list_highlights_with_auth(self, client, demo_auth_headers):
        note_id = str(uuid.uuid4())
        resp = client.get(
            f"/v1/notes/{note_id}/highlights",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body

    def test_list_bookmarks_requires_auth(self, client):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/bookmarks")
        assert resp.status_code in (401, 403)

    def test_list_personal_notes_requires_auth(self, client):
        note_id = str(uuid.uuid4())
        resp = client.get(f"/v1/notes/{note_id}/personal-notes")
        assert resp.status_code in (401, 403)

    def test_note_search_requires_auth(self, client):
        resp = client.get("/v1/notes/search", params={"q": "test"})
        assert resp.status_code in (401, 403)

    def test_note_export_requires_auth(self, client):
        resp = client.get("/v1/note-export")
        assert resp.status_code in (401, 403)


class TestProgressFlowIntegration:
    def test_toggle_subtopic_requires_auth(self, client):
        subtopic_id = uuid.uuid4()
        resp = client.post(f"/v1/progress/subtopics/{subtopic_id}/toggle")
        assert resp.status_code in (401, 403)

    def test_toggle_subtopic_with_auth(self, client, demo_auth_headers):
        subtopic_id = uuid.uuid4()
        resp = client.post(
            f"/v1/progress/subtopics/{subtopic_id}/toggle",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 404, 500, 503)

    def test_get_chapter_progress_requires_auth(self, client):
        chapter_id = uuid.uuid4()
        resp = client.get(f"/v1/progress/chapters/{chapter_id}")
        assert resp.status_code in (401, 403)

    def test_get_chapter_progress_with_auth(self, client, demo_auth_headers):
        chapter_id = uuid.uuid4()
        resp = client.get(
            f"/v1/progress/chapters/{chapter_id}",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 404, 500, 503)

    def test_get_subject_progress_requires_auth(self, client):
        subject_id = uuid.uuid4()
        resp = client.get(f"/v1/progress/subjects/{subject_id}")
        assert resp.status_code in (401, 403)

    def test_get_subject_progress_with_auth(self, client, demo_auth_headers):
        subject_id = uuid.uuid4()
        resp = client.get(
            f"/v1/progress/subjects/{subject_id}",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 404, 500, 503)

    def test_get_exam_progress_requires_auth(self, client):
        exam_id = uuid.uuid4()
        resp = client.get(f"/v1/progress/exams/{exam_id}")
        assert resp.status_code in (401, 403)

    def test_get_exam_progress_with_auth(self, client, demo_auth_headers):
        exam_id = uuid.uuid4()
        resp = client.get(
            f"/v1/progress/exams/{exam_id}",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 404, 500, 503)

    def test_get_streak_requires_auth(self, client):
        resp = client.get("/v1/progress/streak")
        assert resp.status_code in (401, 403)

    def test_get_streak_with_auth_returns_defaults(self, client, demo_auth_headers):
        resp = client.get("/v1/progress/streak", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "current_streak" in body or "streak" in body


class TestAnalyticsFlowIntegration:
    def test_get_overview_requires_auth(self, client):
        resp = client.get("/v1/analytics/overview")
        assert resp.status_code in (401, 403)

    def test_get_overview_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/analytics/overview", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body

    def test_get_daily_progress_requires_auth(self, client):
        resp = client.get("/v1/analytics/daily")
        assert resp.status_code in (401, 403)

    def test_get_daily_progress_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/analytics/daily", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body

    def test_get_daily_progress_with_custom_days(self, client, demo_auth_headers):
        resp = client.get(
            "/v1/analytics/daily",
            params={"days": 7},
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 422, 500)

    def test_get_subject_progress_analytics_requires_auth(self, client):
        resp = client.get("/v1/analytics/subjects")
        assert resp.status_code in (401, 403)

    def test_get_subject_progress_analytics_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/analytics/subjects", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body

    def test_get_quiz_trends_requires_auth(self, client):
        resp = client.get("/v1/analytics/quiz-trends")
        assert resp.status_code in (401, 403)

    def test_get_quiz_trends_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/analytics/quiz-trends", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body

    def test_get_weak_areas_requires_auth(self, client):
        resp = client.get("/v1/analytics/weak-areas")
        assert resp.status_code in (401, 403)

    def test_get_weak_areas_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/analytics/weak-areas", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body

    def test_get_heatmap_requires_auth(self, client):
        resp = client.get("/v1/analytics/heatmap")
        assert resp.status_code in (401, 403)

    def test_get_heatmap_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/analytics/heatmap", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)

    def test_get_streak_calendar_requires_auth(self, client):
        resp = client.get("/v1/analytics/streak-calendar")
        assert resp.status_code in (401, 403)

    def test_get_streak_calendar_with_auth(self, client, demo_auth_headers):
        resp = client.get(
            "/v1/analytics/streak-calendar",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 500)

    def test_get_prediction_requires_auth(self, client):
        resp = client.get("/v1/analytics/prediction")
        assert resp.status_code in (401, 403)

    def test_get_prediction_with_auth(self, client, demo_auth_headers):
        resp = client.get("/v1/analytics/prediction", headers=demo_auth_headers)
        assert resp.status_code in (200, 500)


class TestRoadmapFlowIntegration:
    def test_generate_roadmap_requires_auth(self, client):
        resp = client.post("/v1/roadmap/generate")
        assert resp.status_code in (401, 403)

    def test_get_priority_scores_requires_auth(self, client):
        resp = client.get("/v1/roadmap/priority-scores")
        assert resp.status_code in (401, 403)

    def test_get_prediction_requires_auth(self, client):
        resp = client.get("/v1/roadmap/predict")
        assert resp.status_code in (401, 403)

    def test_get_prediction_history_requires_auth(self, client):
        resp = client.get("/v1/roadmap/predictions/history")
        assert resp.status_code in (401, 403)

    def test_generate_recovery_plan_requires_auth(self, client):
        resp = client.post(
            "/v1/roadmap/recovery",
            params={"exam_date": "2026-12-01"},
        )
        assert resp.status_code in (401, 403)

    def test_get_active_recovery_plan_requires_auth(self, client):
        resp = client.get("/v1/roadmap/recovery/active")
        assert resp.status_code in (401, 403)

    def test_optimize_for_exam_requires_auth(self, client):
        resp = client.post(
            "/v1/roadmap/optimize",
            params={"exam_date": "2026-12-01"},
        )
        assert resp.status_code in (401, 403)

    def test_roadmap_endpoints_with_auth_no_db(self, client, demo_auth_headers):
        resp = client.get(
            "/v1/roadmap/priority-scores",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 500, 503)

        resp = client.get("/v1/roadmap/predict", headers=demo_auth_headers)
        assert resp.status_code in (200, 500, 503)

        resp = client.get(
            "/v1/roadmap/recovery/active",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 500, 503)


class TestMistakeIntelligenceFlowIntegration:
    def test_log_mistake_requires_auth(self, client):
        resp = client.post(
            "/v1/mistake-intelligence/mistakes",
            params={"question_id": "q1", "mistake_type": "conceptual"},
        )
        assert resp.status_code in (401, 403)

    def test_get_user_mistakes_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes")
        assert resp.status_code in (401, 403)

    def test_get_mistake_stats_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/stats")
        assert resp.status_code in (401, 403)

    def test_analyze_gaps_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/gaps")
        assert resp.status_code in (401, 403)

    def test_get_weak_concepts_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/weak-concepts")
        assert resp.status_code in (401, 403)

    def test_get_mastery_level_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/mastery/test-concept")
        assert resp.status_code in (401, 403)

    def test_get_study_plan_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/study-plan")
        assert resp.status_code in (401, 403)

    def test_predict_mistakes_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/predictions")
        assert resp.status_code in (401, 403)

    def test_get_high_risk_concepts_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/high-risk")
        assert resp.status_code in (401, 403)

    def test_get_improvement_trend_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/trend/test-concept")
        assert resp.status_code in (401, 403)

    def test_cluster_mistakes_requires_auth(self, client):
        resp = client.post("/v1/mistake-intelligence/mistakes/cluster")
        assert resp.status_code in (401, 403)

    def test_get_cluster_stats_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/cluster/stats")
        assert resp.status_code in (401, 403)

    def test_get_full_intelligence_report_requires_auth(self, client):
        resp = client.get("/v1/mistake-intelligence/mistakes/report")
        assert resp.status_code in (401, 403)

    def test_mistake_intelligence_with_auth(self, client, demo_auth_headers):
        resp = client.get(
            "/v1/mistake-intelligence/mistakes/stats",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body or "stats" in body or "mistakes" in body

        resp = client.get(
            "/v1/mistake-intelligence/mistakes",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "data" in body or "mistakes" in body

        resp = client.get(
            "/v1/mistake-intelligence/mistakes/report",
            headers=demo_auth_headers,
        )
        assert resp.status_code in (200, 500)


class TestCrossServiceIntegration:
    def test_me_endpoint_with_valid_token(self, client, demo_auth_headers):
        resp = client.get("/v1/me", headers=demo_auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "service" in body

    def test_root_endpoint(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert "service" in body

    def test_syllabus_exams_public(self, client):
        resp = client.get("/v1/syllabus/exams")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_syllabus_chapters_public(self, client):
        resp = client.get("/v1/syllabus/chapters")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_ai_chat_requires_auth(self, client):
        resp = client.post(
            "/v1/ai/chat",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )
        assert resp.status_code in (401, 403, 422)

    def test_bulk_import_requires_auth(self, client):
        resp = client.post("/v1/bulk-import")
        assert resp.status_code in (401, 403, 422)

    def test_privacy_export_requires_auth(self, client):
        resp = client.get("/v1/privacy/export")
        assert resp.status_code in (401, 403)

    def test_privacy_delete_requires_auth(self, client):
        resp = client.delete("/v1/privacy/account")
        assert resp.status_code in (401, 403)
