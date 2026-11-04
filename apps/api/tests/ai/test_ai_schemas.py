"""Tests for AI schemas."""

from studyos_api.schemas.ai import (
    AIChatMessageIn,
    AIChatPayload,
    AIChatRequest,
    AIChatSuccessResponse,
    AIUsagePayload,
    MCPServersPayload,
    MCPServersSuccessResponse,
    MCPToolCallRequest,
    MCPToolsRequest,
    MCPToolsSuccessResponse,
)


class TestAISchemas:
    def test_ai_chat_message_in(self) -> None:
        msg = AIChatMessageIn(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_ai_chat_request(self) -> None:
        req = AIChatRequest(messages=[AIChatMessageIn(role="user", content="Hi")])
        assert len(req.messages) == 1

    def test_ai_usage_payload(self) -> None:
        payload = AIUsagePayload(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        assert payload.prompt_tokens == 10

    def test_ai_chat_payload(self) -> None:
        usage = AIUsagePayload(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        payload = AIChatPayload(
            text="Hello!", provider_id="openai", model="gpt-4o-mini", usage=usage
        )
        assert payload.text == "Hello!"

    def test_ai_chat_success_response(self) -> None:
        usage = AIUsagePayload(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        payload = AIChatPayload(
            text="Hello!", provider_id="openai", model="gpt-4o-mini", usage=usage
        )
        resp = AIChatSuccessResponse(data=payload, meta={"api_version": "v1"})
        assert resp.data.text == "Hello!"

    def test_mcp_servers_payload(self) -> None:
        payload = MCPServersPayload(server_ids=[])
        assert len(payload.server_ids) == 0

    def test_mcp_servers_success_response(self) -> None:
        payload = MCPServersPayload(server_ids=[])
        resp = MCPServersSuccessResponse(data=payload, meta={"api_version": "v1"})
        assert resp.data is not None

    def test_mcp_tools_request(self) -> None:
        req = MCPToolsRequest(server_id="test-server")
        assert req.server_id == "test-server"

    def test_mcp_tools_success_response(self) -> None:
        resp = MCPToolsSuccessResponse(data={}, meta={"api_version": "v1"})
        assert resp.data is not None

    def test_mcp_tool_call_request(self) -> None:
        req = MCPToolCallRequest(
            server_id="test-server", name="search", arguments={"query": "test"}
        )
        assert req.server_id == "test-server"
        assert req.name == "search"
