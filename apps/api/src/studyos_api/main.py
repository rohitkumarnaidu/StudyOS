from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
import httpx
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from studyos_api.ai.mcp.registry import MCPConnectorRegistry
from studyos_api.ai.memory.context import SessionConversationMemory
from studyos_api.ai.provider_factory import build_llm_chain
from studyos_api.api.versions import register_versioned_routes
from studyos_api.core.config import Settings, get_settings
from studyos_api.core.errors import (
    AppError,
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from studyos_api.core.limiter import limiter
from studyos_api.core.logging import configure_logging
from studyos_api.core.telemetry import init_telemetry
from studyos_api.middleware import (
    CsrfMiddleware,
    RequestIdMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from studyos_api.middleware.audit import AuditLoggingMiddleware
from studyos_api.middleware.cache_headers import CacheHeadersMiddleware
from studyos_api.middleware.rate_limit_headers import RateLimitHeadersMiddleware
from studyos_api.services.auth_login_service import AuthLoginService
from studyos_api.services.cache import init_cache
from studyos_api.services.refresh_sessions import MemoryRefreshStore, PostgresRefreshStore

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("api.startup", app_env=settings.app_env)

    # Initialize Redis cache
    init_cache(settings.redis_url)

    pool: asyncpg.Pool | None = None
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=20.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=25),
    ) as http_client:
        app.state.http_client = http_client
        app.state.ai_conversation_memory = SessionConversationMemory(
            max_messages=settings.ai_memory_max_messages,
            ttl_seconds=settings.ai_memory_session_ttl_seconds,
        )
        app.state.mcp_registry = MCPConnectorRegistry(settings=settings, http_client=http_client)
        if settings.ai_warm_on_start:
            app.state.llm_chain = build_llm_chain(settings, http_client)
            logger.info("ai.warm_chain_ready", providers=len(app.state.llm_chain))
        else:
            app.state.llm_chain = None
        if settings.database_url:
            pool = await asyncpg.create_pool(
                dsn=settings.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                max_inactive_connection_lifetime=180.0,
                statement_cache_size=0,
            )
            store = PostgresRefreshStore(pool)
            app.state.db_pool = pool
            app.state.refresh_store = store
            app.state.auth_login_service = AuthLoginService(
                pool=pool,
                refresh_store=store,
                settings=settings,
            )
        yield
        if pool is not None:
            await pool.close()
    logger.info("api.shutdown")


def _init_memory_auth_state(app: FastAPI, settings: Settings) -> None:
    """Init in-process auth when DATABASE_URL is unset (tests skip ASGI lifespan)."""
    if settings.database_url:
        return
    store = MemoryRefreshStore()
    app.state.db_pool = None
    app.state.refresh_store = store
    app.state.auth_login_service = AuthLoginService(
        pool=None,
        refresh_store=store,
        settings=settings,
    )


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="StudyOS API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(AuditLoggingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(CacheHeadersMiddleware)
    app.add_middleware(RateLimitHeadersMiddleware)
    app.add_middleware(CsrfMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if settings.trusted_host_list:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)

    init_telemetry(
        app,
        service_name=settings.otel_service_name,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        sample_rate=settings.otel_traces_sample_rate,
    )

    register_versioned_routes(app)

    @app.get("/", tags=["meta"])
    def service_root() -> dict[str, object]:
        payload: dict[str, object] = {
            "service": "studyos-api",
            "versions": [{"name": "v1", "base_path": "/v1"}, {"name": "v2", "base_path": "/v2"}],
        }
        if not settings.is_production:
            payload["documentation"] = "/docs"
        return payload

    @app.get("/health", tags=["meta"])
    async def health_check() -> dict[str, object]:
        """Health check endpoint for container orchestration and load balancers."""
        health: dict[str, object] = {"status": "healthy", "service": "studyos-api"}
        pool = getattr(app.state, "db_pool", None)
        if pool is not None:
            try:
                async with pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                health["database"] = "connected"
            except Exception:
                health["database"] = "disconnected"
                health["status"] = "degraded"
        return health

    @app.get("/metrics", tags=["meta"])
    async def metrics() -> dict[str, object]:
        """Basic metrics endpoint for monitoring."""
        return {
            "service": "studyos-api",
            "version": "0.1.0",
            "env": settings.app_env,
        }

    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)

    _init_memory_auth_state(app, settings)

    return app


app = create_app()
