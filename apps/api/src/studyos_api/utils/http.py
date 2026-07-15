"""HTTP-related helpers."""

from starlette.requests import Request


def client_ip(request: Request) -> str:
    """Best-effort client IP (honor X-Forwarded-For only behind a trusted proxy)."""
    if request.client:
        return request.client.host
    return "unknown"
