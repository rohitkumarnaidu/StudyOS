# SKILL_BACKEND.md
# StudyOS — Backend Patterns & Conventions
# Read before generating ANY FastAPI endpoint, service, schema, or database code

---

## 1. PROJECT STRUCTURE (canonical — never deviate)

```
apps/api/
├── src/
│   └── studyos_api/
│       ├── __init__.py
│       ├── main.py                     ← FastAPI app factory (create_app)
│       │
│       ├── api/                        ← API routes
│       │   ├── versions.py             ← Versioned route registration
│       │   ├── v1/
│       │   │   ├── router.py           ← V1 router assembly
│       │   │   └── routes/
│       │   │       ├── auth.py         ← /v1/auth/* (login, register, refresh, logout)
│       │   │       ├── syllabus.py     ← /v1/syllabus/* (exams, subjects, chapters)
│       │   │       ├── progress.py     ← /v1/progress/* (subtopic completions)
│       │   │       ├── ai.py           ← /v1/ai/* (chat, roadmap)
│       │   │       ├── me.py           ← /v1/me (current user profile)
│       │   │       ├── privacy.py      ← /v1/privacy/* (data export, deletion)
│       │   │       ├── health.py       ← /v1/health
│       │   │       └── examples.py     ← Example endpoints
│       │   └── v2/                     ← Future API version
│       │
│       ├── core/                       ← Core configuration
│       │   ├── config.py               ← Settings (Zod-validated env vars)
│       │   ├── errors.py               ← AppError base class + handlers
│       │   └── limiter.py              ← SlowAPI rate limiter config
│       │
│       ├── deps/                       ← FastAPI dependencies
│       │   ├── auth.py                 ← get_current_user, require_auth
│       │   └── database.py             ← get_db_pool
│       │
│       ├── middleware/                 ← Custom middleware
│       │   ├── __init__.py
│       │   ├── audit.py                ← Audit logging for sensitive paths
│       │   ├── cache_headers.py        ← HTTP cache headers
│       │   ├── csrf.py                 ← CSRF double-submit cookie
│       │   ├── rate_limit_headers.py   ← Rate limit response headers
│       │   ├── request_id.py           ← X-Request-ID injection
│       │   ├── request_logging.py      ← Structured request logging
│       │   └── security_headers.py     ← CSP, HSTS, X-Frame-Options
│       │
│       ├── schemas/                    ← Pydantic v2 models
│       │   ├── auth.py                 ← LoginRequest, RegisterRequest, TokenResponse
│       │   ├── syllabus.py             ← ExamProfile, Subject, Chapter, Topic, Subtopic
│       │   ├── progress.py             ← SubtopicCompletion, ProgressResponse
│       │   ├── ai.py                   ← ChatMessage, ChatRequest, RoadmapResponse
│       │   └── user.py                 ← UserProfile, UserUpdate
│       │
│       ├── security/                   ← Security utilities
│       │   ├── password.py             ← Argon2id hashing
│       │   ├── jwt.py                  ← JWT encode/decode
│       │   └── tokens.py               ← Refresh token generation
│       │
│       ├── services/                   ← Business logic
│       │   ├── auth_login_service.py   ← Authentication service
│       │   ├── cache.py                ← Redis cache with in-memory fallback
│       │   ├── syllabus_service.py     ← Syllabus data access
│       │   ├── progress_service.py     ← Progress tracking
│       │   ├── ai_service.py           ← AI chat + roadmap generation
│       │   └── upload_security.py      ← File upload validation
│       │
│       ├── ai/                         ← AI integration layer
│       │   ├── provider_factory.py     ← LLM provider abstraction
│       │   ├── mcp/                    ← MCP connector registry
│       │   └── memory/                 ← Conversation memory
│       │
│       ├── types/                      ← Custom type definitions
│       │
│       └── utils/                      ← Utility functions
│
├── tests/                              ← Test suite
│   ├── test_auth.py
│   ├── test_syllabus.py
│   └── ...
│
├── pyproject.toml                      ← uv/pip dependencies
└── uv.lock
```

---

## 2. FASTAPI PATTERNS

### App factory pattern
```python
# main.py — create_app function
from fastapi import FastAPI
from studyos_api.core.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="StudyOS API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
    )
    # Middleware, routes, error handlers...
    return app

app = create_app()
```

### Route registration (versioned)
```python
# api/v1/router.py
from fastapi import APIRouter
from studyos_api.api.v1.routes import auth, syllabus, progress, ai, me, privacy, health

router = APIRouter(prefix="/v1")

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(syllabus.router, prefix="/syllabus", tags=["syllabus"])
router.include_router(progress.router, prefix="/progress", tags=["progress"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
router.include_router(me.router, tags=["me"])
router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
router.include_router(health.router, tags=["health"])
```

### Endpoint pattern
```python
# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from studyos_api.schemas.auth import LoginRequest, TokenResponse
from studyos_api.deps.auth import get_auth_service
from studyos_api.services.auth_login_service import AuthLoginService

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    auth_service: AuthLoginService = Depends(get_auth_service),
):
    """Authenticate user with email/password."""
    result = await auth_service.login(payload.email, payload.password)
    return result
```

---

## 3. PYDANTIC SCHEMA PATTERNS

### Request/Response models
```python
# schemas/auth.py
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

class UserProfile(BaseModel):
    id: str
    name: str
    email: EmailStr
    exam_type: str | None = None
    exam_date: str | None = None
    created_at: datetime
```

### Error response model
```python
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    field_errors: dict[str, str] | None = None
```

---

## 4. DATABASE PATTERNS (asyncpg)

### Connection pool (lifespan)
```python
# main.py — lifespan context manager
import asyncpg
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=1,
        max_size=10,
        command_timeout=60,
        max_inactive_connection_lifetime=180.0,
        statement_cache_size=0,
    )
    app.state.db_pool = pool
    yield
    await pool.close()
```

### Dependency injection
```python
# deps/database.py
from fastapi import Depends, Request
import asyncpg

async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool
```

### Query patterns
```python
# services/syllabus_service.py
import asyncpg

class SyllabusService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_chapters(self, subject_id: str) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, number, name, class, tier, weightage_pct, is_deleted
                FROM chapters
                WHERE subject_id = $1 AND is_deleted = false
                ORDER BY number
                """,
                subject_id,
            )
            return [dict(r) for r in rows]

    async def get_chapter(self, chapter_id: str) -> dict | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, number, name, class, tier, weightage_pct
                FROM chapters
                WHERE id = $1 AND is_deleted = false
                """,
                chapter_id,
            )
            return dict(row) if row else None
```

---

## 5. AUTH PATTERNS

### Password hashing (Argon2id)
```python
# security/password.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False
```

### JWT tokens
```python
# security/jwt.py
import jwt
from datetime import datetime, timedelta, timezone

def create_access_token(
    user_id: str,
    email: str,
    secret: str,
    expires_delta: timedelta = timedelta(minutes=15),
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

### Auth dependency
```python
# deps/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
```

---

## 6. SERVICE LAYER PATTERNS

### Service class pattern
```python
# services/progress_service.py
import asyncpg
from datetime import datetime, timezone

class ProgressService:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def complete_subtopic(
        self,
        user_id: str,
        subtopic_id: str,
    ) -> dict:
        async with self.pool.acquire() as conn:
            # Insert completion (idempotent)
            await conn.execute(
                """
                INSERT INTO subtopic_completions (user_id, subtopic_id, completed_at, source)
                VALUES ($1, $2, $3, 'manual')
                ON CONFLICT (user_id, subtopic_id) DO NOTHING
                """,
                user_id,
                subtopic_id,
                datetime.now(timezone.utc),
            )
            # Recalculate chapter progress
            row = await conn.fetchrow(
                """
                SELECT chapter_id,
                    COUNT(*) FILTER (WHERE sc.completed_at IS NOT NULL) as completed,
                    COUNT(*) as total
                FROM subtopics st
                JOIN chapters c ON c.id = st.chapter_id
                LEFT JOIN subtopic_completions sc
                    ON sc.subtopic_id = st.id AND sc.user_id = $1
                WHERE c.id = (SELECT chapter_id FROM subtopics WHERE id = $2)
                GROUP BY chapter_id
                """,
                user_id,
                subtopic_id,
            )
            if row:
                pct = round((row["completed"] / row["total"]) * 100)
                await conn.execute(
                    """
                    INSERT INTO user_chapter_progress (user_id, chapter_id, pct_complete, last_studied_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, chapter_id)
                    DO UPDATE SET pct_complete = $3, last_studied_at = $4
                    """,
                    user_id,
                    row["chapter_id"],
                    pct,
                    datetime.now(timezone.utc),
                )
            return {"subtopic_id": subtopic_id, "completed": True}
```

---

## 7. MIDDLEWARE PATTERNS

### Request ID middleware
```python
# middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

### Security headers middleware
```python
# middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response
```

### Audit logging middleware
```python
# middleware/audit.py
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

SENSITIVE_PATHS = ["/v1/auth/", "/v1/privacy/"]

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        is_sensitive = any(
            request.url.path.startswith(p) for p in SENSITIVE_PATHS
        )
        if is_sensitive and request.method in ("POST", "DELETE"):
            structlog.contextvars.bind_contextvars(
                audit=True,
                audit_path=request.url.path,
                audit_method=request.method,
            )
        return await call_next(request)
```

---

## 8. ERROR HANDLING

### Custom error base class
```python
# core/errors.py
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, detail: str, code: str | None = None, status_code: int = 400):
        self.detail = detail
        self.code = code
        self.status_code = status_code

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "field_errors": {
                str(e["loc"][-1]): e["msg"]
                for e in exc.errors()
            },
        },
    )
```

---

## 9. RATE LIMITING

### SlowAPI configuration
```python
# core/limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Usage in routes
from studyos_api.core.limiter import limiter

@router.post("/login")
@limiter.limit("5/15minutes")
async def login(request: Request, payload: LoginRequest):
    ...
```

---

## 10. CACHING

### Redis service with in-memory fallback
```python
# services/cache.py
import json
from typing import Any

_cache: dict[str, Any] = {}
_redis_client: Any | None = None

def init_cache(redis_url: str | None) -> None:
    global _redis_client
    if redis_url:
        import redis.asyncio as redis
        _redis_client = redis.from_url(redis_url, decode_responses=True)

async def cache_get(key: str) -> Any | None:
    if _redis_client:
        val = await _redis_client.get(key)
        return json.loads(val) if val else None
    return _cache.get(key)

async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    if _redis_client:
        await _redis_client.setex(key, ttl, json.dumps(value))
    else:
        _cache[key] = value
```

---

## 11. LOGGING (structlog)

### Configuration
```python
# core/logging.py
import structlog

def configure_logging(log_level: str = "info") -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(__import__("logging"), log_level.upper())
        ),
        cache_logger_on_first_use=True,
    )
```

### Usage
```python
import structlog

logger = structlog.get_logger(__name__)

logger.info("auth.login.success", user_id=user_id, ip=request.client.host)
logger.warning("auth.login.failed", email=email, ip=request.client.host)
logger.error("db.query.failed", error=str(e), query="SELECT ...")
```

---

## 12. AI INTEGRATION

### LLM provider factory
```python
# ai/provider_factory.py
import httpx

def build_llm_chain(settings, http_client: httpx.AsyncClient):
    """Build fallback chain: primary → secondary → tertiary."""
    chain = []
    if settings.openai_api_key:
        chain.append({
            "provider": "openai",
            "model": settings.openai_model,
            "api_key": settings.openai_api_key,
        })
    if settings.anthropic_api_key:
        chain.append({
            "provider": "anthropic",
            "model": settings.anthropic_model,
            "api_key": settings.anthropic_api_key,
        })
    return chain
```

### SSE streaming for chat
```python
# routes/ai.py
from fastapi.responses import StreamingResponse

@router.post("/chat")
async def chat(request: ChatRequest):
    async def generate():
        async for chunk in ai_service.stream_chat(request.messages):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
```

---

## 13. TESTING PATTERNS

### Test client setup
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from studyos_api.main import create_app

@pytest.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

### Endpoint test
```python
# tests/test_auth.py
import pytest

@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    response = await client.post(
        "/v1/auth/login",
        json={"email": "test@example.com", "password": "Test1234!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.anyio
async def test_login_invalid(client: AsyncClient):
    response = await client.post(
        "/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong"},
    )
    assert response.status_code == 401
```

---

## 14. ENVIRONMENT VARIABLES

### Config (Zod-validated via Pydantic)
```python
# core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_env: str = "development"
    is_production: bool = False

    # Database
    database_url: str | None = None

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_access_token_expiry_minutes: int = 15
    jwt_refresh_token_expiry_days: int = 30

    # Redis
    redis_url: str | None = None

    # AI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5-20250414"
    ai_warm_on_start: bool = True
    ai_memory_max_messages: int = 50
    ai_memory_session_ttl_seconds: int = 3600

    # CORS
    cors_origin_list: list[str] = ["http://localhost:3000"]

    # Logging
    log_level: str = "info"

    # Rate limiting
    trusted_host_list: list[str] = []

    # Telemetry
    otel_service_name: str = "studyos-api"
    otel_exporter_otlp_endpoint: str | None = None
    otel_traces_sample_rate: float = 0.0

    class Config:
        env_prefix = "STUDYOS_"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 15. DO / DON'T QUICK REFERENCE

```
✅ DO:
  Use Pydantic v2 for all request/response schemas
  Use asyncpg for database queries (not SQLAlchemy)
  Use structlog for JSON logging
  Use SlowAPI for rate limiting
  Use app.state for shared resources (pool, cache, services)
  Use lifespan context manager for startup/shutdown
  Use Depends() for dependency injection
  Use @limiter.limit() for endpoint rate limits
  Return StreamingResponse for AI chat (SSE)
  Validate all inputs with Pydantic
  Use ON CONFLICT for idempotent operations
  Use RLS policies for row-level security

❌ DON'T:
  Use Supabase Edge Functions (use FastAPI)
  Use Supabase JS client (use asyncpg directly)
  Use Supabase Realtime subscriptions
  Use Dexie.js or IndexedDB patterns
  Use synchronous database drivers
  Store secrets in code (use env vars)
  Skip error handlers
  Use print() for logging (use structlog)
  Skip rate limiting on auth endpoints
  Return raw database rows (convert to dict)
  Use bare except: clauses
  Commit .env files
```

---

*SKILL_BACKEND.md — StudyOS | FastAPI Python 3.12 | May 2026*
