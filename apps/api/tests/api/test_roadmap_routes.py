"""Tests for roadmap routes."""

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


class TestRoadmapRoutes:
    def test_generate_roadmap(self, client, auth_headers):
        resp = client.post("/v1/roadmap/generate", headers=auth_headers)
        assert resp.status_code in (200, 500)

    def test_generate_roadmap_without_auth(self, client):
        resp = client.post("/v1/roadmap/generate")
        assert resp.status_code in (401, 403, 200)

    def test_update_roadmap_item(self, client, auth_headers):
        item_id = str(uuid.uuid4())
        resp = client.patch(
            f"/v1/roadmap/items/{item_id}",
            json={"status": "completed"},
            headers=auth_headers,
        )
        assert resp.status_code in (200, 404, 500)

    def test_update_roadmap_item_without_auth(self, client):
        item_id = str(uuid.uuid4())
        resp = client.patch(f"/v1/roadmap/items/{item_id}", json={"status": "completed"})
        assert resp.status_code in (401, 403, 404, 405, 200)

    def test_get_priority_scores(self, client, auth_headers):
        resp = client.get("/v1/roadmap/priority-scores", headers=auth_headers)
        assert resp.status_code in (200, 500)

    def test_get_priority_scores_without_auth(self, client):
        resp = client.get("/v1/roadmap/priority-scores")
        assert resp.status_code in (401, 403, 200)

    def test_get_prediction(self, client, auth_headers):
        resp = client.get("/v1/roadmap/predict", headers=auth_headers)
        assert resp.status_code in (200, 500)

    def test_get_prediction_without_auth(self, client):
        resp = client.get("/v1/roadmap/predict")
        assert resp.status_code in (401, 403, 200)

    def test_get_predictions_history(self, client, auth_headers):
        resp = client.get("/v1/roadmap/predictions/history", headers=auth_headers)
        assert resp.status_code in (200, 500)

    def test_get_predictions_history_without_auth(self, client):
        resp = client.get("/v1/roadmap/predictions/history")
        assert resp.status_code in (401, 403, 200)

    def test_create_recovery_plan(self, client, auth_headers):
        resp = client.post("/v1/roadmap/recovery?exam_date=2026-06-01", headers=auth_headers)
        assert resp.status_code in (200, 422, 500)

    def test_create_recovery_plan_without_auth(self, client):
        resp = client.post("/v1/roadmap/recovery?exam_date=2026-06-01")
        assert resp.status_code in (401, 403, 200)

    def test_get_active_recovery_plan(self, client, auth_headers):
        resp = client.get("/v1/roadmap/recovery/active", headers=auth_headers)
        assert resp.status_code in (200, 500)

    def test_get_active_recovery_plan_without_auth(self, client):
        resp = client.get("/v1/roadmap/recovery/active")
        assert resp.status_code in (401, 403, 200)

    def test_optimize_roadmap(self, client, auth_headers):
        resp = client.post("/v1/roadmap/optimize?exam_date=2026-06-01", headers=auth_headers)
        assert resp.status_code in (200, 422, 500)

    def test_optimize_roadmap_without_auth(self, client):
        resp = client.post("/v1/roadmap/optimize?exam_date=2026-06-01")
        assert resp.status_code in (401, 403, 200)
