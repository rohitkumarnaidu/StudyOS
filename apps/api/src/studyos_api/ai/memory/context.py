"""Server-side conversation buffers (single-process; swap for Redis + vector memory later)."""

from __future__ import annotations

import time

from studyos_api.ai.types import ChatMessage


class SessionConversationMemory:
    """Keyed transcript store with TTL + max message count."""

    def __init__(self, *, max_messages: int, ttl_seconds: int) -> None:
        self._max_messages = max_messages
        self._ttl = ttl_seconds
        self._buffers: dict[str, tuple[list[ChatMessage], float]] = {}

    def _purge(self, now: float) -> None:
        dead = [k for k, (_, t) in self._buffers.items() if now - t > self._ttl]
        for k in dead:
            del self._buffers[k]

    def get_messages(self, key: str) -> list[ChatMessage]:
        self._purge(time.time())
        row = self._buffers.get(key)
        if row is None:
            return []
        return list(row[0])

    def set_messages(self, key: str, messages: list[ChatMessage]) -> None:
        now = time.time()
        self._purge(now)
        trimmed = messages[-self._max_messages :]
        self._buffers[key] = (trimmed, now)
