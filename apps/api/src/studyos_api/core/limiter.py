"""Endpoint-specific rate limit decorators and helpers."""

from collections.abc import Callable

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    strategy="fixed-window",
)

AUTH_RATE_LIMIT = "5/minute"
AI_RATE_LIMIT = "30/minute"
SYLLABUS_RATE_LIMIT = "200/minute"


def rate_limit_auth(func: Callable) -> Callable:
    """Rate limit for auth endpoints (login, register, password reset)."""
    return limiter.limit(AUTH_RATE_LIMIT)(func)


def rate_limit_ai(func: Callable) -> Callable:
    """Rate limit for AI/chat endpoints."""
    return limiter.limit(AI_RATE_LIMIT)(func)


def rate_limit_syllabus(func: Callable) -> Callable:
    """Higher rate limit for syllabus read endpoints."""
    return limiter.limit(SYLLABUS_RATE_LIMIT)(func)
