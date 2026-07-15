"""Audit logging middleware — records sensitive operations for compliance."""

import time
from uuid import uuid4

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger(__name__)

# Paths that require audit logging
AUDIT_PATHS = {
    "/v1/auth/login",
    "/v1/auth/register",
    "/v1/auth/logout",
    "/v1/privacy/export",
    "/v1/privacy/account",
    "/v1/admin",
}


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log sensitive operations for compliance (GDPR/DPDP/SOC2)."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check if this path requires audit logging
        requires_audit = any(
            request.url.path.startswith(path) for path in AUDIT_PATHS
        )

        if not requires_audit:
            return await call_next(request)

        # Generate audit ID
        audit_id = str(uuid4())
        start_time = time.time()

        # Extract user context
        auth_header = request.headers.get("Authorization", "")
        user_sub = "anonymous"
        if auth_header.startswith("Bearer "):
            # Token present — will be resolved by auth middleware
            user_sub = "authenticated"

        # Get request body hash (don't log sensitive data)
        body_preview = ""
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if len(body) > 100:
                    body_preview = f"{body[:100]}..."
                else:
                    body_preview = body.decode("utf-8", errors="replace")
            except Exception:
                body_preview = "<unreadable>"

        # Log audit event
        logger.info(
            "audit.request",
            audit_id=audit_id,
            method=request.method,
            path=request.url.path,
            user_sub=user_sub,
            ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "")[:100],
            body_preview=body_preview if request.method != "GET" else None,
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log audit response
        logger.info(
            "audit.response",
            audit_id=audit_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_sub=user_sub,
        )

        # Add audit ID to response headers for tracing
        response.headers["X-Audit-ID"] = audit_id

        return response
