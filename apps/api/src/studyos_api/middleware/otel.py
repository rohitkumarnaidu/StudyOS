"""OpenTelemetry middleware for FastAPI — traces, metrics, and request logging."""

from __future__ import annotations

import time
from collections.abc import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)


class OTelMiddleware(BaseHTTPMiddleware):
    """Middleware that adds OTel-style request metrics and tracing metadata."""

    def __init__(
        self,
        app,
        service_name: str = "studyos-api",
        sample_rate: float = 0.1,
    ) -> None:
        super().__init__(app)
        self._service_name = service_name
        self._sample_rate = sample_rate
        self._request_count = 0
        self._error_count = 0
        self._latency_total = 0.0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = request.headers.get("x-request-id", "")

        response = await call_next(request)

        duration = time.time() - start_time
        self._request_count += 1
        self._latency_total += duration

        if response.status_code >= 500:
            self._error_count += 1

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "service": self._service_name,
        }
        if request_id:
            log_data["request_id"] = request_id

        if response.status_code >= 500:
            logger.error("http.request.failed", **log_data)
        elif duration > 1.0:
            logger.warning("http.request.slow", **log_data)
        else:
            logger.info("http.request.completed", **log_data)

        response.headers["x-service-name"] = self._service_name
        if request_id:
            response.headers["x-request-id"] = request_id
        response.headers["x-response-time-ms"] = str(round(duration * 1000, 2))

        return response

    @property
    def metrics(self) -> dict:
        """Get current middleware metrics."""
        avg_latency = (
            self._latency_total / self._request_count
            if self._request_count > 0
            else 0.0
        )
        return {
            "service_name": self._service_name,
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "avg_latency_ms": round(avg_latency * 1000, 2),
            "sample_rate": self._sample_rate,
        }

    def reset_metrics(self) -> None:
        """Reset all metrics counters."""
        self._request_count = 0
        self._error_count = 0
        self._latency_total = 0.0
