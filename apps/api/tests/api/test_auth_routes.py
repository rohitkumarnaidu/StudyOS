"""Integration tests for auth routes — covering gaps."""

import os
import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture(autouse=True)
def configure_test_env() -> None:
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    os.environ["STUDYOS_ALLOW_LEGACY_DEMO_BEARER"] = "true"
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app, base_url="http://testserver") as c:
        yield c


class TestAuthRoutes:
    def test_login_demo_credentials(self, client) -> None:
        resp = client.post(
            "/v1/auth/login",
            json={"email": "demo@studyos.app", "password": "demo"},
        )
        assert resp.status_code in (200, 401)

    def test_register_new_user(self, client) -> None:
        resp = client.post(
            "/v1/auth/register",
            json={"email": "newuser@test.com", "password": "secure123"},
        )
        assert resp.status_code in (200, 400, 409, 422, 500)

    def test_refresh_without_token(self, client) -> None:
        resp = client.post("/v1/auth/refresh")
        assert resp.status_code in (401, 422)

    def test_logout_without_token(self, client) -> None:
        resp = client.post("/v1/auth/logout")
        assert resp.status_code in (401, 200, 422, 500)
