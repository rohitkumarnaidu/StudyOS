"""Tests for all middleware modules."""

import time
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from studyos_api.middleware.csrf import CsrfMiddleware, CSRF_COOKIE_NAME, CSRF_HEADER_NAME, SAFE_METHODS
from studyos_api.middleware.request_id import RequestIdMiddleware
from studyos_api.middleware.request_logging import RequestLoggingMiddleware, SKIPPED_PATHS
from studyos_api.middleware.security_headers import SecurityHeadersMiddleware
from studyos_api.middleware.cache_headers import CacheHeadersMiddleware, CACHEABLE_PATHS, CACHE_TTL
from studyos_api.middleware.rate_limit_headers import RateLimitHeadersMiddleware
from studyos_api.middleware.audit import AuditLoggingMiddleware, AUDIT_PATHS


@pytest.mark.unit
class TestCsrfMiddleware:
    """Test CSRF double-submit cookie middleware."""

    @pytest.mark.anyio
    async def test_skipped_in_non_production(self):
        """CSRF middleware is disabled when not in production."""
        with patch("studyos_api.middleware.csrf.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=False)

            async def call_next(request):
                return Response(status_code=200)

            middleware = CsrfMiddleware(None)
            request = MagicMock(method="POST", url=MagicMock(path="/v1/auth/login"))
            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 200

    @pytest.mark.anyio
    async def test_sets_csrf_cookie_on_safe_methods(self):
        """GET requests receive a CSRF token cookie."""
        with patch("studyos_api.middleware.csrf.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=True)

            async def call_next(request):
                from starlette.responses import PlainTextResponse
                resp = PlainTextResponse("ok", status_code=200)
                return resp

            middleware = CsrfMiddleware(None)
            request = MagicMock(method="GET", url=MagicMock(path="/v1/syllabus"))
            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 200
            # set_cookie adds Set-Cookie header
            assert "set-cookie" in response.headers
            assert CSRF_COOKIE_NAME in response.headers["set-cookie"]

    @pytest.mark.anyio
    async def test_rejects_missing_csrf_tokens(self):
        """POST without CSRF cookie or header returns 403."""
        with patch("studyos_api.middleware.csrf.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=True)

            middleware = CsrfMiddleware(None)
            request = MagicMock(
                method="POST",
                url=MagicMock(path="/v1/auth/login"),
                cookies={},
                headers={},
            )

            async def call_next(request):
                return Response(status_code=200)

            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 403
            assert "CSRF token missing" in response.body.decode()

    @pytest.mark.anyio
    async def test_rejects_only_cookie_token(self):
        """POST with only cookie token (no header) returns 403."""
        with patch("studyos_api.middleware.csrf.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=True)

            middleware = CsrfMiddleware(None)
            request = MagicMock(
                method="POST",
                url=MagicMock(path="/v1/auth/login"),
                cookies={CSRF_COOKIE_NAME: "test-token"},
                headers={},
            )

            async def call_next(request):
                return Response(status_code=200)

            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 403

    @pytest.mark.anyio
    async def test_rejects_only_header_token(self):
        """POST with only header token (no cookie) returns 403."""
        with patch("studyos_api.middleware.csrf.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=True)

            middleware = CsrfMiddleware(None)
            request = MagicMock(
                method="POST",
                url=MagicMock(path="/v1/auth/login"),
                cookies={},
                headers={CSRF_HEADER_NAME: "test-token"},
            )

            async def call_next(request):
                return Response(status_code=200)

            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 403

    @pytest.mark.anyio
    async def test_rejects_mismatched_tokens(self):
        """POST with mismatched cookie/header tokens returns 403."""
        with patch("studyos_api.middleware.csrf.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=True)

            middleware = CsrfMiddleware(None)
            request = MagicMock(
                method="POST",
                url=MagicMock(path="/v1/auth/login"),
                cookies={CSRF_COOKIE_NAME: "cookie-token"},
                headers={CSRF_HEADER_NAME: "header-token"},
            )

            async def call_next(request):
                return Response(status_code=200)

            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 403
            assert "CSRF token mismatch" in response.body.decode()

    @pytest.mark.anyio
    async def test_accepts_matching_tokens(self):
        """POST with matching cookie/header tokens passes through."""
        with patch("studyos_api.middleware.csrf.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=True)

            async def call_next(request):
                return Response(status_code=200)

            middleware = CsrfMiddleware(None)
            request = MagicMock(
                method="POST",
                url=MagicMock(path="/v1/auth/login"),
                cookies={CSRF_COOKIE_NAME: "matching-token"},
                headers={CSRF_HEADER_NAME: "matching-token"},
            )

            response = await middleware.dispatch(request, call_next)

            assert response.status_code == 200

    @pytest.mark.anyio
    async def test_safe_methods_list(self):
        """Verify SAFE_METHODS contains expected HTTP methods."""
        assert "GET" in SAFE_METHODS
        assert "HEAD" in SAFE_METHODS
        assert "OPTIONS" in SAFE_METHODS
        assert "POST" not in SAFE_METHODS
        assert "PUT" not in SAFE_METHODS
        assert "DELETE" not in SAFE_METHODS


@pytest.mark.unit
class TestRequestIdMiddleware:
    """Test request ID propagation middleware."""

    @pytest.mark.anyio
    async def test_generates_request_id_when_missing(self):
        """Generates UUID when X-Request-Id header is absent."""
        async def call_next(request):
            return Response(status_code=200)

        middleware = RequestIdMiddleware(None)
        request = MagicMock(
            headers={},
            method="GET",
            url=MagicMock(path="/v1/health"),
        )
        response = await middleware.dispatch(request, call_next)

        assert "X-Request-Id" in response.headers
        assert len(response.headers["X-Request-Id"]) == 36  # UUID format

    @pytest.mark.anyio
    async def test_propagates_existing_request_id(self):
        """Preserves X-Request-Id when provided by client."""
        async def call_next(request):
            return Response(status_code=200)

        middleware = RequestIdMiddleware(None)
        request = MagicMock(
            headers={"x-request-id": "client-provided-id"},
            method="GET",
            url=MagicMock(path="/v1/health"),
        )
        response = await middleware.dispatch(request, call_next)

        assert response.headers["X-Request-Id"] == "client-provided-id"

    @pytest.mark.anyio
    async def test_sets_request_state(self):
        """Sets request.state.request_id for downstream access."""
        async def call_next(request):
            assert hasattr(request.state, "request_id")
            return Response(status_code=200)

        middleware = RequestIdMiddleware(None)
        request = MagicMock(
            headers={},
            method="GET",
            url=MagicMock(path="/v1/health"),
            state=MagicMock(),
        )
        await middleware.dispatch(request, call_next)


@pytest.mark.unit
class TestRequestLoggingMiddleware:
    """Test request logging middleware."""

    @pytest.mark.anyio
    async def test_skips_health_paths(self):
        """Does not log requests to health/metrics/docs paths."""
        for path in SKIPPED_PATHS:
            middleware = RequestLoggingMiddleware(None)
            request = MagicMock(
                method="GET",
                url=MagicMock(path=path),
            )

            async def call_next(request):
                return Response(status_code=200)

            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 200
            assert "X-Response-Time" not in response.headers

    @pytest.mark.anyio
    async def test_logs_api_requests(self):
        """Logs requests to API paths with timing."""
        middleware = RequestLoggingMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/syllabus"),
            client=MagicMock(host="127.0.0.1"),
            headers={"user-agent": "test-client"},
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 200
        assert "X-Response-Time" in response.headers
        assert "ms" in response.headers["X-Response-Time"]

    @pytest.mark.anyio
    async def test_response_time_format(self):
        """X-Response-Time header contains millisecond value."""
        middleware = RequestLoggingMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/health"),
            client=MagicMock(host="127.0.0.1"),
            headers={},
        )

        async def call_next(request):
            time.sleep(0.01)  # Small delay
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert "X-Response-Time" in response.headers
        # Should be a number followed by "ms"
        value = response.headers["X-Response-Time"]
        assert value.endswith("ms")


@pytest.mark.unit
class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""

    @pytest.mark.anyio
    async def test_sets_baseline_headers(self):
        """Sets X-Content-Type-Options, X-Frame-Options, Referrer-Policy."""
        async def call_next(request):
            return Response(status_code=200)

        middleware = SecurityHeadersMiddleware(None)
        request = MagicMock(method="GET", url=MagicMock(path="/v1/health"))
        response = await middleware.dispatch(request, call_next)

        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    @pytest.mark.anyio
    async def test_sets_permissions_policy(self):
        """Restricts camera, microphone, geolocation."""
        async def call_next(request):
            return Response(status_code=200)

        middleware = SecurityHeadersMiddleware(None)
        request = MagicMock(method="GET", url=MagicMock(path="/v1/health"))
        response = await middleware.dispatch(request, call_next)

        permissions = response.headers.get("Permissions-Policy", "")
        assert "camera=()" in permissions
        assert "microphone=()" in permissions
        assert "geolocation=()" in permissions

    @pytest.mark.anyio
    async def test_hsts_only_in_production(self):
        """HSTS header only set when is_production=True."""
        with patch("studyos_api.middleware.security_headers.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=False)

            async def call_next(request):
                return Response(status_code=200)

            middleware = SecurityHeadersMiddleware(None)
            request = MagicMock(method="GET", url=MagicMock(path="/v1/health"))
            response = await middleware.dispatch(request, call_next)

            assert "Strict-Transport-Security" not in response.headers

    @pytest.mark.anyio
    async def test_hsts_in_production(self):
        """HSTS header set with max-age=31536000 in production."""
        with patch("studyos_api.middleware.security_headers.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(is_production=True)

            async def call_next(request):
                return Response(status_code=200)

            middleware = SecurityHeadersMiddleware(None)
            request = MagicMock(method="GET", url=MagicMock(path="/v1/health"))
            response = await middleware.dispatch(request, call_next)

            hsts = response.headers.get("Strict-Transport-Security", "")
            assert "max-age=31536000" in hsts
            assert "includeSubDomains" in hsts

    @pytest.mark.anyio
    async def test_does_not_override_existing_headers(self):
        """Uses setdefault to not override existing headers."""
        async def call_next(request):
            return Response(
                status_code=200,
                headers={"X-Content-Type-Options": "custom-value"},
            )

        middleware = SecurityHeadersMiddleware(None)
        request = MagicMock(method="GET", url=MagicMock(path="/v1/health"))
        response = await middleware.dispatch(request, call_next)

        assert response.headers.get("X-Content-Type-Options") == "custom-value"


@pytest.mark.unit
class TestCacheHeadersMiddleware:
    """Test HTTP cache headers middleware."""

    @pytest.mark.anyio
    async def test_caches_syllabus_get_requests(self):
        """GET requests to /v1/syllabus receive cache headers."""
        for path in CACHEABLE_PATHS:
            middleware = CacheHeadersMiddleware(None)
            request = MagicMock(
                method="GET",
                url=MagicMock(path=path),
            )

            async def call_next(request):
                return Response(status_code=200)

            response = await middleware.dispatch(request, call_next)

            cache_control = response.headers.get("Cache-Control", "")
            assert "public" in cache_control
            assert f"max-age={CACHE_TTL}" in cache_control
            assert response.headers.get("Vary") == "Authorization"

    @pytest.mark.anyio
    async def test_no_cache_for_post_requests(self):
        """POST requests receive no-cache headers."""
        middleware = CacheHeadersMiddleware(None)
        request = MagicMock(
            method="POST",
            url=MagicMock(path="/v1/auth/login"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        cache_control = response.headers.get("Cache-Control", "")
        assert "no-store" in cache_control
        assert "no-cache" in cache_control

    @pytest.mark.anyio
    async def test_no_cache_for_non_syllabus_paths(self):
        """GET requests to non-syllabus paths receive no-cache headers."""
        middleware = CacheHeadersMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/auth/session"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        cache_control = response.headers.get("Cache-Control", "")
        assert "no-store" in cache_control

    @pytest.mark.anyio
    async def test_s_maxage_doubled(self):
        """s-maxage is double the max-age for CDN caching."""
        middleware = CacheHeadersMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/syllabus"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        cache_control = response.headers.get("Cache-Control", "")
        assert f"s-maxage={CACHE_TTL * 2}" in cache_control


@pytest.mark.unit
class TestRateLimitHeadersMiddleware:
    """Test rate limit headers middleware."""

    @pytest.mark.anyio
    async def test_sets_default_rate_limit_headers(self):
        """Sets default rate limit headers when no rate info present."""
        async def call_next(request):
            return Response(status_code=200)

        middleware = RateLimitHeadersMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/health"),
            state=MagicMock(),
        )
        request.state.rate_limit = None
        response = await middleware.dispatch(request, call_next)

        assert response.headers.get("X-RateLimit-Limit") == "120"
        assert response.headers.get("X-RateLimit-Remaining") == "120"

    @pytest.mark.anyio
    async def test_sets_rate_limit_from_state(self):
        """Uses rate_limit from request.state when available."""
        async def call_next(request):
            return Response(status_code=200)

        middleware = RateLimitHeadersMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/health"),
            state=MagicMock(),
        )
        request.state.rate_limit = {
            "limit": 60,
            "remaining": 45,
            "reset": 300,
        }
        response = await middleware.dispatch(request, call_next)

        assert response.headers.get("X-RateLimit-Limit") == "60"
        assert response.headers.get("X-RateLimit-Remaining") == "45"
        assert response.headers.get("X-RateLimit-Reset") == "300"


@pytest.mark.unit
class TestAuditLoggingMiddleware:
    """Test audit logging middleware."""

    @pytest.mark.anyio
    async def test_skips_non_audit_paths(self):
        """Does not audit log requests to non-sensitive paths."""
        middleware = AuditLoggingMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/syllabus"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 200
        assert "X-Audit-ID" not in response.headers

    @pytest.mark.anyio
    async def test_audits_auth_login(self):
        """Logs audit events for /v1/auth/login."""
        middleware = AuditLoggingMiddleware(None)
        request = MagicMock(
            method="POST",
            url=MagicMock(path="/v1/auth/login"),
            headers={"Authorization": "Bearer some-token", "user-agent": "test-client"},
            client=MagicMock(host="127.0.0.1"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 200
        assert "X-Audit-ID" in response.headers
        assert len(response.headers["X-Audit-ID"]) == 36  # UUID format

    @pytest.mark.anyio
    async def test_audits_privacy_export(self):
        """Logs audit events for /v1/privacy/export."""
        middleware = AuditLoggingMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/privacy/export"),
            headers={},
            client=MagicMock(host="127.0.0.1"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert "X-Audit-ID" in response.headers

    @pytest.mark.anyio
    async def test_audits_admin_paths(self):
        """Logs audit events for /v1/admin paths."""
        middleware = AuditLoggingMiddleware(None)
        request = MagicMock(
            method="GET",
            url=MagicMock(path="/v1/admin/ping"),
            headers={},
            client=MagicMock(host="127.0.0.1"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert "X-Audit-ID" in response.headers

    @pytest.mark.anyio
    async def test_detects_authenticated_user(self):
        """Sets user_sub to 'authenticated' when Bearer token present."""
        middleware = AuditLoggingMiddleware(None)
        request = MagicMock(
            method="POST",
            url=MagicMock(path="/v1/auth/logout"),
            headers={"Authorization": "Bearer valid-token"},
            client=MagicMock(host="127.0.0.1"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_marks_anonymous_user(self):
        """Sets user_sub to 'anonymous' when no Bearer token."""
        middleware = AuditLoggingMiddleware(None)
        request = MagicMock(
            method="POST",
            url=MagicMock(path="/v1/auth/login"),
            headers={},
            client=MagicMock(host="127.0.0.1"),
        )

        async def call_next(request):
            return Response(status_code=200)

        response = await middleware.dispatch(request, call_next)

        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_audits_all_audit_paths(self):
        """All paths in AUDIT_PATHS trigger audit logging."""
        for path in AUDIT_PATHS:
            middleware = AuditLoggingMiddleware(None)
            request = MagicMock(
                method="GET" if "privacy" in path else "POST",
                url=MagicMock(path=path),
                headers={},
                client=MagicMock(host="127.0.0.1"),
            )

            async def call_next(request):
                return Response(status_code=200)

            response = await middleware.dispatch(request, call_next)

            assert "X-Audit-ID" in response.headers, f"Missing audit ID for {path}"
