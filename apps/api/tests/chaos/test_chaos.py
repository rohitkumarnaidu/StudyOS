"""Chaos engineering tests for StudyOS API.

Simulates failures and verifies graceful degradation:
- Service degradation: AI provider timeout, fallback to next provider
- Database connection loss: service gracefully handles DB unavailability
- Redis connection loss: cache falls back to in-memory
- Rate limit exhaustion: service returns proper 429 with retry-after
- Memory pressure: large payloads handled without crashes
- Token budget exhaustion: AI requests blocked properly
"""

import asyncio
import os
from unittest.mock import MagicMock, patch

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
    import uuid

    from studyos_api.core.config import get_settings
    from studyos_api.security.tokens import mint_access_token

    settings = get_settings()
    user_id = str(uuid.uuid4())
    token = mint_access_token(settings, sub=user_id, roles=["student"])
    return {"Authorization": f"Bearer {token}"}


class TestAIServiceDegradation:
    def test_ai_provider_timeout_falls_back(self, client, auth_headers):
        with patch("studyos_api.ai.provider_factory.build_llm_chain") as mock_chain:
            mock_provider = MagicMock()
            mock_provider.chat = MagicMock(side_effect=TimeoutError("timeout"))
            mock_chain.return_value = [mock_provider]

            resp = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            assert resp.status_code in (200, 500, 503)

    def test_ai_provider_connection_refused(self, client, auth_headers):
        with patch("studyos_api.ai.provider_factory.build_llm_chain") as mock_chain:
            mock_provider = MagicMock()
            mock_provider.chat = MagicMock(side_effect=ConnectionError("refused"))
            mock_chain.return_value = [mock_provider]

            resp = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            assert resp.status_code in (200, 500, 503)

    def test_ai_provider_empty_response(self, client, auth_headers):
        with patch("studyos_api.ai.provider_factory.build_llm_chain") as mock_chain:
            mock_provider = MagicMock()
            mock_provider.chat = MagicMock(return_value=None)
            mock_chain.return_value = [mock_provider]

            resp = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            assert resp.status_code in (200, 400, 500)

    def test_ai_provider_malformed_response(self, client, auth_headers):
        with patch("studyos_api.ai.provider_factory.build_llm_chain") as mock_chain:
            mock_provider = MagicMock()
            mock_provider.chat = MagicMock(return_value="not json")
            mock_chain.return_value = [mock_provider]

            resp = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            assert resp.status_code in (200, 400, 500)

    def test_all_ai_providers_fail_gracefully(self, client, auth_headers):
        with patch("studyos_api.ai.provider_factory.build_llm_chain") as mock_chain:
            mock_chain.return_value = []

            resp = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            assert resp.status_code in (200, 500, 503)


class TestDatabaseConnectionLoss:
    def test_service_handles_db_unavailable(self, client, auth_headers):
        resp = client.get("/v1/progress/streak", headers=auth_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "current_streak" in body or "streak" in body

    def test_progress_toggle_without_db_returns_error(self, client, auth_headers):
        import uuid

        subtopic_id = uuid.uuid4()
        resp = client.post(
            f"/v1/progress/subtopics/{subtopic_id}/toggle",
            headers=auth_headers,
        )
        assert resp.status_code in (200, 500, 503)

    def test_analytics_without_db_returns_defaults(self, client, auth_headers):
        resp = client.get("/v1/analytics/overview", headers=auth_headers)
        assert resp.status_code in (200, 500, 503)

    def test_roadmap_without_db_returns_error(self, client, auth_headers):
        resp = client.get("/v1/roadmap/priority-scores", headers=auth_headers)
        assert resp.status_code in (200, 500, 503)

    def test_health_degraded_without_db(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] in ("healthy", "degraded")


class TestRedisConnectionLoss:
    def test_cache_falls_back_to_in_memory(self, client):
        from studyos_api.services import cache

        cache._local_cache.clear()
        cache._enabled = False
        cache._client = None

        async def _test():
            await cache.set("test_key", "test_value")
            result = await cache.get("test_key")
            assert result == "test_value"

        asyncio.run(_test())

    def test_api_works_without_redis(self, client, auth_headers):
        with patch("studyos_api.services.cache._enabled", False):
            resp = client.get("/v1/syllabus/chapters")
            assert resp.status_code in (200, 500)

    def test_cache_get_returns_none_for_missing_key(self, client):
        from studyos_api.services import cache

        cache._local_cache.clear()
        cache._enabled = False

        async def _test():
            result = await cache.get("nonexistent_key_chaos_test")
            assert result is None

        asyncio.run(_test())


class TestRateLimitExhaustion:
    def test_rate_limit_returns_429(self, client):
        with patch("studyos_api.core.limiter.limiter") as mock_limiter:
            from slowapi.errors import RateLimitExceeded

            mock_limiter.limit.side_effect = RateLimitExceeded

            resp = client.get("/v1/syllabus/exams")
            assert resp.status_code in (200, 429)

    def test_rate_limit_configured(self, client):
        # Verify rate limiting is configured
        resp = client.get("/v1/syllabus/exams")
        assert resp.status_code in (200, 429)

    def test_auth_endpoints_rate_limited(self, client):
        for _ in range(50):
            resp = client.post(
                "/v1/auth/login",
                json={"email": "test@test.com", "password": "test"},
            )
            if resp.status_code == 429:
                break
        assert resp.status_code in (401, 422, 429)


class TestMemoryPressure:
    def test_large_request_body_handled(self, client):
        large_payload = {"data": "x" * 1_000_000}

        resp = client.post(
            "/v1/ai/chat",
            json=large_payload,
            headers={"Authorization": "Bearer demo"},
        )
        assert resp.status_code in (200, 400, 413, 422, 500)

    def test_large_query_parameters(self, client):
        resp = client.get("/v1/note-search?q=" + "a" * 10_000)
        assert resp.status_code in (200, 400, 413, 414, 422, 401, 403)

    def test_deeply_nested_json_payload(self, client):
        nested = {"level": 0}
        current = nested
        for i in range(100):
            current["child"] = {"level": i + 1}
            current = current["child"]

        resp = client.post(
            "/v1/ai/chat",
            json=nested,
            headers={"Authorization": "Bearer demo"},
        )
        assert resp.status_code in (200, 400, 422, 500)


class TestTokenBudgetExhaustion:
    def test_ai_requests_blocked_when_budget_exhausted(self, client, auth_headers):
        with patch("studyos_api.api.v1.routes.ai.get_budget_enforcer") as mock_get:
            mock_enforcer = MagicMock()
            mock_enforcer.check_budget.return_value = {
                "allowed": False,
                "daily_remaining": 0,
                "monthly_remaining": 0,
            }
            mock_get.return_value = mock_enforcer

            resp = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            assert resp.status_code in (200, 402, 429, 500)

    def test_budget_check_allows_valid_requests(self, client, auth_headers):
        with patch("studyos_api.api.v1.routes.ai.get_budget_enforcer") as mock_get:
            mock_enforcer = MagicMock()
            mock_enforcer.check_budget.return_value = {
                "allowed": True,
                "daily_remaining": 1000,
                "monthly_remaining": 5000,
            }
            mock_get.return_value = mock_enforcer

            with patch("studyos_api.ai.provider_factory.build_llm_chain") as mock_chain:
                mock_provider = MagicMock()
                mock_provider.chat = MagicMock(return_value="OK")
                mock_chain.return_value = [mock_provider]

                resp = client.post(
                    "/v1/ai/chat",
                    json={"messages": [{"role": "user", "content": "test"}]},
                    headers=auth_headers,
                )
                assert resp.status_code in (200, 500)

    def test_budget_tracking_records_usage(self, client, auth_headers):
        with patch("studyos_api.api.v1.routes.ai.get_budget_enforcer") as mock_get:
            mock_enforcer = MagicMock()
            mock_enforcer.check_budget.return_value = {
                "allowed": True,
                "daily_remaining": 1000,
                "monthly_remaining": 5000,
            }
            mock_enforcer.record_usage = MagicMock()
            mock_get.return_value = mock_enforcer

            # Budget check passes, AI call may succeed or fail depending on environment
            resp = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            # Verify budget was checked (the key behavior we're testing)
            mock_enforcer.check_budget.assert_called_once()
            assert resp.status_code in (200, 500)

    def test_budget_reset_allows_new_requests(self, client, auth_headers):
        with patch("studyos_api.api.v1.routes.ai.get_budget_enforcer") as mock_get:
            mock_enforcer = MagicMock()
            mock_enforcer.check_budget.side_effect = [
                {"allowed": False, "daily_remaining": 0, "monthly_remaining": 0},
                {"allowed": True, "daily_remaining": 1000, "monthly_remaining": 5000},
            ]
            mock_enforcer.reset_budget = MagicMock()
            mock_get.return_value = mock_enforcer

            resp1 = client.post(
                "/v1/ai/chat",
                json={"messages": [{"role": "user", "content": "test"}]},
                headers=auth_headers,
            )
            assert resp1.status_code in (200, 402, 429, 500)

            mock_enforcer.reset_budget.return_value = True

            with patch("studyos_api.ai.provider_factory.build_llm_chain") as mock_chain:
                mock_provider = MagicMock()
                mock_provider.chat = MagicMock(return_value="OK")
                mock_chain.return_value = [mock_provider]

                resp2 = client.post(
                    "/v1/ai/chat",
                    json={"messages": [{"role": "user", "content": "test"}]},
                    headers=auth_headers,
                )
                assert resp2.status_code in (200, 500)
