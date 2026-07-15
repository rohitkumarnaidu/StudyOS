"""AI chat (multi-provider) + MCP connector endpoints."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from studyos_api.ai.service import AIService
from studyos_api.ai.types import ChatMessage
from studyos_api.core.limiter import limiter
from studyos_api.core.responses import response_meta
from studyos_api.deps.ai import get_ai_service
from studyos_api.deps.rbac import Permission, require_permissions
from studyos_api.schemas.ai import (
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
from studyos_api.services.token_budget import get_budget_enforcer
from studyos_api.types.principal import User

router = APIRouter()


def _messages(body: AIChatRequest) -> list[ChatMessage]:
    return [ChatMessage(role=m.role, content=m.content) for m in body.messages]


@router.post("/chat", response_model=AIChatSuccessResponse)
@limiter.limit("30/minute")
async def ai_chat(
    request: Request,
    body: AIChatRequest,
    user: Annotated[User, Depends(require_permissions(Permission.AI_USE))],
    svc: Annotated[AIService, Depends(get_ai_service)],
) -> AIChatSuccessResponse:
    rid = getattr(request.state, "request_id", None)

    budget = get_budget_enforcer().check_budget(user["sub"])
    if not budget["allowed"]:
        raise HTTPException(
            status_code=429,
            detail=f"Token budget exceeded. Daily remaining: {budget['daily_remaining']}, Monthly remaining: {budget['monthly_remaining']}",
        )

    result = await svc.complete_chat(
        messages=_messages(body),
        model=body.model,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        prompt_id=body.prompt_id,
        prompt_variables=body.prompt_variables,
        conversation_key=body.conversation_key,
        user_sub=user["sub"],
        request_id=str(rid) if rid else None,
    )
    payload = AIChatPayload(
        text=result.text,
        provider_id=result.provider_id,
        model=result.model,
        usage=AIUsagePayload(
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            total_tokens=result.usage.total_tokens,
        ),
    )
    return AIChatSuccessResponse(data=payload, meta=response_meta(request, api_version="v1"))


@router.post("/chat/stream")
@limiter.limit("20/minute")
async def ai_chat_stream(
    request: Request,
    body: AIChatRequest,
    user: Annotated[User, Depends(require_permissions(Permission.AI_USE))],
    svc: Annotated[AIService, Depends(get_ai_service)],
) -> StreamingResponse:
    rid = getattr(request.state, "request_id", None)

    budget = get_budget_enforcer().check_budget(user["sub"])
    if not budget["allowed"]:
        raise HTTPException(
            status_code=429,
            detail=f"Token budget exceeded. Daily remaining: {budget['daily_remaining']}, Monthly remaining: {budget['monthly_remaining']}",
        )

    async def event_gen() -> AsyncIterator[str]:
        async for line in svc.stream_chat(
            messages=_messages(body),
            model=body.model,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            prompt_id=body.prompt_id,
            prompt_variables=body.prompt_variables,
            conversation_key=body.conversation_key,
            user_sub=user["sub"],
            request_id=str(rid) if rid else None,
        ):
            yield line

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Connection": "keep-alive",
        },
    )


@router.get("/mcp/servers", response_model=MCPServersSuccessResponse)
@limiter.limit("60/minute")
async def list_mcp_servers(
    request: Request,
    user: Annotated[User, Depends(require_permissions(Permission.AI_USE))],
    svc: Annotated[AIService, Depends(get_ai_service)],
) -> MCPServersSuccessResponse:
    _ = user
    ids = svc.mcp.list_connector_ids()
    return MCPServersSuccessResponse(
        data=MCPServersPayload(server_ids=ids),
        meta=response_meta(request, api_version="v1"),
    )


@router.post("/mcp/tools", response_model=MCPToolsSuccessResponse)
@limiter.limit("30/minute")
async def mcp_list_tools(
    request: Request,
    body: MCPToolsRequest,
    user: Annotated[User, Depends(require_permissions(Permission.AI_USE))],
    svc: Annotated[AIService, Depends(get_ai_service)],
) -> MCPToolsSuccessResponse:
    _ = user
    tools = await svc.mcp.list_tools(body.server_id)
    return MCPToolsSuccessResponse(data=tools, meta=response_meta(request, api_version="v1"))


@router.post("/mcp/call", response_model=MCPToolsSuccessResponse)
@limiter.limit("30/minute")
async def mcp_call_tool(
    request: Request,
    body: MCPToolCallRequest,
    user: Annotated[User, Depends(require_permissions(Permission.AI_USE))],
    svc: Annotated[AIService, Depends(get_ai_service)],
) -> MCPToolsSuccessResponse:
    _ = user
    out = await svc.mcp.call_tool(body.server_id, body.name, body.arguments)
    return MCPToolsSuccessResponse(data=out, meta=response_meta(request, api_version="v1"))
