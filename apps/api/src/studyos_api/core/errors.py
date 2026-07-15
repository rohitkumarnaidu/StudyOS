"""RFC 7807 problem details, application errors, and centralized exception handlers."""

from typing import Any

import structlog
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from studyos_api.core.config import get_settings

logger = structlog.get_logger(__name__)


class AppError(Exception):
    """Raised for expected domain failures; mapped to a problem+json response."""

    def __init__(
        self,
        *,
        code: str,
        title: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str | None = None,
        type_uri: str | None = None,
        extensions: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(title)
        self.code = code
        self.title = title
        self.status_code = status_code
        self.detail = detail
        self.type_uri = type_uri or "https://studyos.app/problems/application-error"
        self.extensions = extensions or {}


def problem(
    *,
    type_uri: str,
    title: str,
    status_code: int,
    detail: str | None = None,
    instance: str | None = None,
    extensions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "type": type_uri,
        "title": title,
        "status": status_code,
    }
    if detail:
        body["detail"] = detail
    if instance:
        body["instance"] = instance
    if extensions:
        body.update(extensions)
    return body


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    _ = request
    payload = problem(
        type_uri=exc.type_uri,
        title=exc.title,
        status_code=exc.status_code,
        detail=exc.detail,
        extensions={"code": exc.code, **exc.extensions},
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    _ = request
    payload = problem(
        type_uri="https://studyos.app/problems/validation-error",
        title="Validation Error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        extensions={"errors": exc.errors()},
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    _ = request
    payload = problem(
        type_uri="https://studyos.app/problems/http-error",
        title="HTTP Error",
        status_code=exc.status_code,
        detail=str(exc.detail),
    )
    return JSONResponse(status_code=exc.status_code, content=payload)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.error("api.unhandled_exception", request_id=request_id, exc_info=True)
    settings = get_settings()
    detail: str | None = None
    if not settings.is_production or settings.expose_error_detail:
        detail = str(exc)
    payload = problem(
        type_uri="https://studyos.app/problems/internal-error",
        title="Internal Server Error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail,
        extensions={"code": "internal_error"},
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=payload)
