"""Helpers for consistent success responses."""

from starlette.requests import Request

from studyos_api.schemas.common import ResponseMeta


def response_meta(request: Request, *, api_version: str) -> ResponseMeta:
    request_id = getattr(request.state, "request_id", None)
    return ResponseMeta(request_id=str(request_id) if request_id else None, api_version=api_version)
