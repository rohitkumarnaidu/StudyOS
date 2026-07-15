"""Tests for progress routes — more comprehensive coverage."""

import os
import uuid

import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture
def client():
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    os.environ["STUDYOS_EXPOSE_ERROR_DETAIL"] = "true"
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()
    app = create_app()
    with TestClient(app, base_url="http://testserver", raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def auth_headers():
    from studyos_api.core.config import get_settings
    from studyos_api.security.tokens import mint_access_token
    import uuid

    settings = get_settings()
    token = mint_access_token(settings, sub=str(uuid.uuid4()), roles=["student"])
    return {"Authorization": f"Bearer {token}"}


class TestToggleSubtopicRoute:
    def test_toggle_requires_auth(self, client):
        subtopic_id = uuid.uuid4()
        resp = client.post(f"/v1/progress/subtopics/{subtopic_id}/toggle")
        assert resp.status_code in (401, 403)

    def test_toggle_invalid_uuid(self, client, auth_headers):
        resp = client.post(
            "/v1/progress/subtopics/not-a-uuid/toggle",
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestChapterProgressRoute:
    def test_get_requires_auth(self, client):
        chapter_id = uuid.uuid4()
        resp = client.get(f"/v1/progress/chapters/{chapter_id}")
        assert resp.status_code in (401, 403)

    def test_get_invalid_uuid(self, client, auth_headers):
        resp = client.get(
            "/v1/progress/chapters/not-a-uuid",
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestSubjectProgressRoute:
    def test_get_requires_auth(self, client):
        subject_id = uuid.uuid4()
        resp = client.get(f"/v1/progress/subjects/{subject_id}")
        assert resp.status_code in (401, 403)

    def test_get_invalid_uuid(self, client, auth_headers):
        resp = client.get(
            "/v1/progress/subjects/not-a-uuid",
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestExamProgressRoute:
    def test_get_requires_auth(self, client):
        exam_id = uuid.uuid4()
        resp = client.get(f"/v1/progress/exams/{exam_id}")
        assert resp.status_code in (401, 403)

    def test_get_invalid_uuid(self, client, auth_headers):
        resp = client.get(
            "/v1/progress/exams/not-a-uuid",
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestStreakRoute:
    def test_get_requires_auth(self, client):
        resp = client.get("/v1/progress/streak")
        assert resp.status_code in (401, 403)

    def test_get_no_pool_returns_defaults(self, client, auth_headers):
        resp = client.get("/v1/progress/streak", headers=auth_headers)
        assert resp.status_code == 200
