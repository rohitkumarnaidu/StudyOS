"""Feature flag middleware — injects flag context into requests."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from studyos_api.services.feature_flags import get_feature_flag_service

logger = structlog.get_logger(__name__)


class FeatureFlagMiddleware(BaseHTTPMiddleware):
    """Middleware that evaluates feature flags and injects them into request state."""

    async def dispatch(self, request: Request, call_next) -> Response:
        service = get_feature_flag_service()

        user_id = self._extract_user_id(request)
        context = self._build_context(request)

        flags = service.get_all_flags(user_id, context)

        request.state.feature_flags = flags
        request.state.user_id = user_id

        response = await call_next(request)
        response.headers["x-feature-flags"] = ",".join(k for k, v in flags.items() if v)

        return response

    def _extract_user_id(self, request: Request) -> str | None:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            import hashlib

            return hashlib.sha256(token.encode()).hexdigest()[:16]

        session_id = request.headers.get("x-session-id")
        if session_id:
            return session_id

        return None

    def _build_context(self, request: Request) -> dict[str, Any]:
        context: dict[str, Any] = {
            "path": request.url.path,
            "method": request.method,
        }

        locale = request.headers.get("accept-language", "")
        if locale:
            context["locale"] = locale.split(",")[0].strip()

        platform = request.headers.get("x-platform")
        if platform:
            context["platform"] = platform

        return context
