"""Authenticated principal (subject + roles)."""

from typing import TypedDict


class User(TypedDict):
    """Authenticated subject resolved from credentials (JWT, session, API key, …)."""

    sub: str
    roles: list[str]
