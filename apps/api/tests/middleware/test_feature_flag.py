"""Tests for feature flag middleware."""

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from studyos_api.middleware.feature_flag import FeatureFlagMiddleware
from studyos_api.services.feature_flags import get_feature_flag_service, reset_feature_flag_service


@pytest.fixture(autouse=True)
def reset_flags():
    reset_feature_flag_service()
    yield
    reset_feature_flag_service()


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()

    @app.get("/flags")
    async def get_flags(request: Request) -> dict:
        return {"flags": getattr(request.state, "feature_flags", {})}

    @app.get("/user")
    async def get_user(request: Request) -> dict:
        return {"user_id": getattr(request.state, "user_id", None)}

    app.add_middleware(FeatureFlagMiddleware)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestFeatureFlagMiddleware:
    def test_injects_flags(self, client: TestClient) -> None:
        service = get_feature_flag_service()
        service.set_flag("test_flag", enabled=True)
        response = client.get("/flags")
        assert response.status_code == 200
        assert response.json()["flags"].get("test_flag") is True

    def test_injects_disabled_flag(self, client: TestClient) -> None:
        service = get_feature_flag_service()
        service.set_flag("disabled_flag", enabled=False)
        response = client.get("/flags")
        assert response.json()["flags"].get("disabled_flag") is False

    def test_sets_response_header(self, client: TestClient) -> None:
        service = get_feature_flag_service()
        service.set_flag("flag1", enabled=True)
        service.set_flag("flag2", enabled=True)
        service.set_flag("flag3", enabled=False)
        response = client.get("/flags")
        header = response.headers.get("x-feature-flags", "")
        assert "flag1" in header
        assert "flag2" in header
        assert "flag3" not in header

    def test_extracts_user_from_bearer_token(self, client: TestClient) -> None:
        response = client.get("/user", headers={"authorization": "Bearer test-token-123"})
        assert response.json()["user_id"] is not None

    def test_extracts_user_from_session_header(self, client: TestClient) -> None:
        response = client.get("/user", headers={"x-session-id": "session-abc"})
        assert response.json()["user_id"] == "session-abc"

    def test_no_user_id(self, client: TestClient) -> None:
        response = client.get("/user")
        assert response.json()["user_id"] is None

    def test_builds_context_from_headers(self, client: TestClient) -> None:
        service = get_feature_flag_service()
        service.set_flag(
            "mobile_only",
            enabled=True,
            conditions={"platform": "mobile"},
        )
        response = client.get(
            "/flags",
            headers={"x-platform": "mobile", "accept-language": "en-US"},
        )
        assert response.json()["flags"].get("mobile_only") is True

    def test_context_condition_fails(self, client: TestClient) -> None:
        service = get_feature_flag_service()
        service.set_flag(
            "mobile_only",
            enabled=True,
            conditions={"platform": "mobile"},
        )
        response = client.get(
            "/flags",
            headers={"x-platform": "web"},
        )
        assert response.json()["flags"].get("mobile_only") is False

    def test_empty_flags_header(self, client: TestClient) -> None:
        response = client.get("/flags")
        header = response.headers.get("x-feature-flags", "")
        assert header == ""
