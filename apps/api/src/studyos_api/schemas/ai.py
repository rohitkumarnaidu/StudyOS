"""AI chat + MCP request/response models."""

from typing import Literal

from pydantic import BaseModel, Field

from studyos_api.schemas.common import ResponseMeta, SuccessEnvelope


class AIChatMessageIn(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=200_000)


class AIChatRequest(BaseModel):
    messages: list[AIChatMessageIn] = Field(min_length=1, max_length=200)
    model: str | None = Field(default=None, max_length=256)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=2048, ge=1, le=32000)
    prompt_id: str | None = Field(default=None, max_length=128)
    prompt_variables: dict[str, str] = Field(default_factory=dict)
    conversation_key: str | None = Field(default=None, max_length=128)


class AIUsagePayload(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class AIChatPayload(BaseModel):
    text: str
    provider_id: str
    model: str
    usage: AIUsagePayload


class AIChatSuccessResponse(SuccessEnvelope[AIChatPayload]):
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class MCPToolsRequest(BaseModel):
    server_id: str = Field(min_length=1, max_length=64)


class MCPToolCallRequest(BaseModel):
    server_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    arguments: dict[str, object] = Field(default_factory=dict)


class MCPServersPayload(BaseModel):
    server_ids: list[str]


class MCPServersSuccessResponse(SuccessEnvelope[MCPServersPayload]):
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class MCPToolsSuccessResponse(SuccessEnvelope[object]):
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
