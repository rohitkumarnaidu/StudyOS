"""Tests for AI routes."""

import os
import pytest
from fastapi.testclient import TestClient

from studyos_api.main import create_app


@pytest.fixture(autouse=True)
def configure_test_env() -> None:
    os.environ["STUDYOS_APP_ENV"] = "test"
    os.environ["STUDYOS_TRUSTED_HOSTS"] = ""
    os.environ["STUDYOS_DATABASE_URL"] = ""
    from studyos_api.core.config import get_settings
    get_settings.cache_clear()


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app, base_url="http://testserver") as c:
        yield c


class TestAIRoutes:
    def test_chat_requires_auth(self, client) -> None:
        resp = client.post("/v1/ai/chat", json={"messages": [{"role": "user", "content": "hi"}]})
        assert resp.status_code in (401, 403, 422)

    def test_chat_stream_requires_auth(self, client) -> None:
        resp = client.post("/v1/ai/chat/stream", json={"messages": [{"role": "user", "content": "hi"}]})
        assert resp.status_code in (401, 403, 422)

    def test_mcp_servers_requires_auth(self, client) -> None:
        resp = client.get("/v1/ai/mcp/servers")
        assert resp.status_code in (401, 403)

    def test_mcp_tools_requires_auth(self, client) -> None:
        resp = client.post("/v1/ai/mcp/tools", json={"server": "test", "tool": "test"})
        assert resp.status_code in (401, 403, 422)

    def test_mcp_call_requires_auth(self, client) -> None:
        resp = client.post("/v1/ai/mcp/call", json={"server": "test", "tool": "test", "arguments": {}})
        assert resp.status_code in (401, 403, 422)
