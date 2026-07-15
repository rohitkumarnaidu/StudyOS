"""Shared AI request/response types — stable across providers."""

from dataclasses import dataclass
from typing import Literal

ChatRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    role: ChatRole
    content: str


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class CompletionRequest:
    messages: list[ChatMessage]
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = 2048
    stream: bool = False


@dataclass
class CompletionResult:
    text: str
    usage: TokenUsage
    provider_id: str
    model: str
    finish_reason: str | None = None


@dataclass
class StreamChunk:
    delta: str
    done: bool = False
    usage: TokenUsage | None = None
    provider_id: str | None = None
    model: str | None = None
