import hmac
import secrets

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from studyos_api.core.config import get_settings

logger = structlog.get_logger(__name__)

CSRF_HEADER_NAME = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CsrfMiddleware(BaseHTTPMiddleware):
    """
    Double-submit cookie CSRF protection.

    - On GET/HEAD, set a csrf_token cookie with a random value.
    - On state-changing requests, require the same token in the X-CSRF-Token header.
    - The cookie is HttpOnly=False so JS can read it for the header.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        settings = get_settings()
        if not settings.is_production:
            return await call_next(request)

        if request.method in SAFE_METHODS:
            response = await call_next(request)
            token = secrets.token_hex(32)
            response.set_cookie(
                key=CSRF_COOKIE_NAME,
                value=token,
                httponly=False,
                secure=True,
                samesite="strict",
                path="/",
            )
            return response

        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)

        if not cookie_token or not header_token:
            logger.warning("csrf.missing_tokens", method=request.method, path=str(request.url.path))
            return Response(
                content='{"detail": "CSRF token missing"}',
                status_code=403,
                media_type="application/json",
                headers={"X-Content-Type-Options": "nosniff"},
            )

        if not hmac.compare_digest(cookie_token, header_token):
            logger.warning("csrf.mismatch", method=request.method, path=str(request.url.path))
            return Response(
                content='{"detail": "CSRF token mismatch"}',
                status_code=403,
                media_type="application/json",
                headers={"X-Content-Type-Options": "nosniff"},
            )

        return await call_next(request)
