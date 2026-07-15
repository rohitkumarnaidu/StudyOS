"""Middleware to add X-RateLimit-* headers to all responses."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard rate limit headers to all responses.

    Headers added:
    - X-RateLimit-Limit: Maximum requests allowed per window
    - X-RateLimit-Remaining: Requests remaining in current window
    - X-RateLimit-Reset: Seconds until the rate limit window resets
    """

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        response: Response = await call_next(request)

        limit = getattr(request.state, "rate_limit", None)
        if limit:
            response.headers["X-RateLimit-Limit"] = str(limit.get("limit", 120))
            response.headers["X-RateLimit-Remaining"] = str(limit.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(limit.get("reset", 0))
        else:
            response.headers["X-RateLimit-Limit"] = "120"
            response.headers["X-RateLimit-Remaining"] = "120"

        return response
