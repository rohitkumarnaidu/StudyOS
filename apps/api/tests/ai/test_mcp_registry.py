"""Tests for AI MCP registry."""

from unittest.mock import AsyncMock

import pytest

from studyos_api.ai.mcp.registry import MCPConnectorRegistry


class TestMCPConnectorRegistry:
    @pytest.fixture
    def mock_settings(self):
        from studyos_api.core.config import Settings

        return Settings(
            ai_mcp_servers_json="[]",
        )

    def test_init_empty(self, mock_settings) -> None:
        registry = MCPConnectorRegistry(settings=mock_settings, http_client=AsyncMock())
        assert registry.list_connector_ids() == []

    def test_list_connector_ids(self, mock_settings) -> None:
        registry = MCPConnectorRegistry(settings=mock_settings, http_client=AsyncMock())
        ids = registry.list_connector_ids()
        assert isinstance(ids, list)
