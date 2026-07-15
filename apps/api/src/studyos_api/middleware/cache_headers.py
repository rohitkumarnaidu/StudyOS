"""HTTP cache headers middleware for API responses."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Paths that should be cached by browsers/CDNs
CACHEABLE_PATHS = {
    "/v1/syllabus",
    "/v1/subjects",
    "/v1/exams",
}

# Cache TTL in seconds
CACHE_TTL = 300  # 5 minutes


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """Add HTTP cache headers to appropriate responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Only cache GET requests to cacheable paths
        if request.method == "GET" and any(
            request.url.path.startswith(path) for path in CACHEABLE_PATHS
        ):
            response.headers.setdefault(
                "Cache-Control",
                f"public, max-age={CACHE_TTL}, s-maxage={CACHE_TTL * 2}",
            )
            response.headers.setdefault("Vary", "Authorization")
        else:
            # Default: no caching for state-changing or authenticated endpoints
            response.headers.setdefault("Cache-Control", "no-store, no-cache, must-revalidate")
            response.headers.setdefault("Pragma", "no-cache")

        return response
