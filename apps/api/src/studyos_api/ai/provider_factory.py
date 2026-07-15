"""Construct provider chain from settings (swap order without code changes)."""

from __future__ import annotations

from typing import cast

import httpx

from studyos_api.ai.protocols import LLMProvider
from studyos_api.ai.providers.anthropic_provider import AnthropicProvider
from studyos_api.ai.providers.base import AbstractLLMProvider
from studyos_api.ai.providers.ollama import OllamaProvider
from studyos_api.ai.providers.openai_provider import OpenAIProvider
from studyos_api.core.config import Settings


def build_llm_chain(settings: Settings, client: httpx.AsyncClient) -> list[LLMProvider]:
    pmap: dict[str, AbstractLLMProvider] = {
        "ollama": OllamaProvider(
            client,
            base_url=settings.ai_ollama_base_url,
            default_model=settings.ai_default_model_ollama,
        ),
    }
    if settings.ai_openai_api_key:
        pmap["openai"] = OpenAIProvider(
            client,
            api_key=settings.ai_openai_api_key,
            base_url=settings.ai_openai_base_url,
            default_model=settings.ai_default_model_openai,
        )
    if settings.ai_anthropic_api_key:
        pmap["anthropic"] = AnthropicProvider(
            client,
            api_key=settings.ai_anthropic_api_key,
            base_url=settings.ai_anthropic_base_url,
            default_model=settings.ai_default_model_anthropic,
        )

    primary = settings.ai_primary_provider.lower().strip()
    ordered: list[AbstractLLMProvider] = []
    if primary in pmap:
        ordered.append(pmap[primary])
    for pid in settings.ai_fallback_provider_ids:
        prov = pmap.get(pid)
        if prov is not None and prov not in ordered:
            ordered.append(prov)
    if not ordered:
        ordered.append(pmap["ollama"])
    return cast(list[LLMProvider], ordered)
