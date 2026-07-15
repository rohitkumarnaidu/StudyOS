from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from studyos_api.core.limiter import limiter

router = APIRouter()

_HEALTH_CACHE = "public, max-age=5, stale-while-revalidate=30"


@router.get("/healthz")
@limiter.limit("120/minute")
def healthz(request: Request) -> JSONResponse:
    _ = request
    return JSONResponse(
        content={"status": "ok"},
        headers={"Cache-Control": _HEALTH_CACHE},
    )


@router.get("/readyz")
@limiter.limit("120/minute")
def readyz(request: Request) -> JSONResponse:
    """Extend with DB/Redis checks when those clients exist."""
    _ = request
    return JSONResponse(
        content={"status": "ready"},
        headers={"Cache-Control": _HEALTH_CACHE},
    )
