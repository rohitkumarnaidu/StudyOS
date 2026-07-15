"""FastAPI dependencies for the AI service (scoped httpx client + usage sinks)."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request

from studyos_api.ai.http_client import http_client_scope
from studyos_api.ai.service import AIService
from studyos_api.ai.usage import CompositeUsageSink, InMemoryUsageStore, LoggingUsageSink
from studyos_api.core.config import Settings, get_settings

_usage_sink = CompositeUsageSink(InMemoryUsageStore(), LoggingUsageSink())


async def get_ai_service(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AIService, None]:
    async with http_client_scope(request.app) as client:
        memory = getattr(request.app.state, "ai_conversation_memory", None)
        mcp_registry = getattr(request.app.state, "mcp_registry", None)
        llm_chain = getattr(request.app.state, "llm_chain", None)
        yield AIService(
            settings=settings,
            http_client=client,
            usage_sink=_usage_sink,
            conversation_memory=memory,
            mcp_registry=mcp_registry,
            llm_chain=llm_chain,
        )
