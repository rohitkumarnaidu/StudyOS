"""Shared httpx client resolution (pooled in lifespan, ephemeral in tests)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI


@asynccontextmanager
async def http_client_scope(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    shared = getattr(app.state, "http_client", None)
    if isinstance(shared, httpx.AsyncClient):
        yield shared
        return
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=20.0),
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
    ) as ephemeral:
        yield ephemeral
