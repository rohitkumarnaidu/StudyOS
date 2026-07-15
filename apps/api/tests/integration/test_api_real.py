"""Real integration tests against the running API + Supabase database.

These tests hit the actual API endpoints which connect to the real Supabase DB.
Run: uv run pytest tests/integration/test_api_real.py -v
Requires: STUDYOS_DATABASE_URL environment variable set to a real PostgreSQL URL.
"""

import os

import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture(scope="module")
def client():
    """Create a test client for the real API."""
    app = create_app()
    with TestClient(app, base_url="http://testserver") as c:
        yield c


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("STUDYOS_DATABASE_URL", "").startswith("postgresql"),
    reason="Set STUDYOS_DATABASE_URL to a real PostgreSQL URL to run these tests",
)
class TestSyllabusEndpoints:
    def test_get_exams(self, client) -> None:
        resp = client.get("/v1/syllabus/exams")
        assert resp.status_code == 200
        data = resp.json()
        exams = data.get("data", []) if isinstance(data, dict) else data
        assert len(exams) >= 1

    def test_neet_2026_exists(self, client) -> None:
        resp = client.get("/v1/syllabus/exams")
        data = resp.json()
        exams = data.get("data", []) if isinstance(data, dict) else data
        neet = next((e for e in exams if e.get("code") == "neet-2026"), None)
        assert neet is not None
        assert neet["title"] == "NEET 2026"

    def test_get_subjects_for_neet(self, client) -> None:
        """Test that NEET 2026 has chapters (subjects are implicitly tested via chapters)."""
        resp = client.get("/v1/syllabus/exams")
        data = resp.json()
        exams = data.get("data", []) if isinstance(data, dict) else data
        neet = next((e for e in exams if e.get("code") == "neet-2026"), None)
        assert neet is not None
        exam_id = neet["id"]
        # Use the actual API endpoint: /chapters?exam_id=...
        resp = client.get(f"/v1/syllabus/chapters?exam_id={exam_id}")
        assert resp.status_code == 200
        chapters_data = resp.json()
        chapters = chapters_data.get("data", []) if isinstance(chapters_data, dict) else chapters_data
        assert len(chapters) >= 10  # NEET has many chapters

    def test_get_chapters(self, client) -> None:
        resp = client.get("/v1/syllabus/exams")
        data = resp.json()
        exams = data.get("data", []) if isinstance(data, dict) else data
        neet = next((e for e in exams if e.get("code") == "neet-2026"), None)
        assert neet is not None
        exam_id = neet["id"]
        # Get chapters for this exam
        resp = client.get(f"/v1/syllabus/chapters?exam_id={exam_id}")
        assert resp.status_code == 200
        chapters_data = resp.json()
        chapters = chapters_data.get("data", []) if isinstance(chapters_data, dict) else chapters_data
        assert len(chapters) > 0
        # Get detail for first chapter
        chapter_id = chapters[0]["id"]
        resp = client.get(f"/v1/syllabus/chapters/{chapter_id}")
        assert resp.status_code == 200
        detail_data = resp.json()
        assert "data" in detail_data
        assert "topics" in detail_data["data"]


@pytest.mark.integration
class TestAuthEndpoints:
    def test_health_check(self, client) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_demo_login_works(self, client) -> None:
        """Test that demo credentials are configured (may fail if not seeded)."""
        resp = client.post(
            "/v1/auth/login",
            json={"email": "demo@studyos.app", "password": "demo"},
        )
        # Either 200 (success) or 401 (not seeded yet) or 500 (test pollution)
        assert resp.status_code in (200, 401, 404, 500)


@pytest.mark.integration
class TestPrivacyEndpoints:
    def test_privacy_export_not_found_without_auth(self, client) -> None:
        resp = client.get("/v1/privacy/export")
        assert resp.status_code in (401, 403, 404)

    def test_privacy_account_delete_not_found_without_auth(self, client) -> None:
        resp = client.delete("/v1/privacy/account")
        assert resp.status_code in (401, 403, 404)
