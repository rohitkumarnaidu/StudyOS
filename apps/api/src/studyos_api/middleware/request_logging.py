import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)

SKIPPED_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with method, path, status code, and duration in milliseconds."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if str(request.url.path) in SKIPPED_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "http.request",
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )

        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        return response
