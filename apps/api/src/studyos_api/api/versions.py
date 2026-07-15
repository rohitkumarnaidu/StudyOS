"""Mount all supported API version routers under stable URL prefixes."""

from fastapi import FastAPI

from studyos_api.api.v1.router import router as v1_router
from studyos_api.api.v2.router import router as v2_router


def register_versioned_routes(app: FastAPI) -> None:
    """Register `/v1/*`, `/v2/*`, … Keep prefixes stable for clients and infra probes."""
    app.include_router(v1_router, prefix="/v1")
    app.include_router(v2_router, prefix="/v2")
