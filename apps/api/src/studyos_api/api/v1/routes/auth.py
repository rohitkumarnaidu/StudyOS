"""Auth endpoints — login, refresh, logout, register (JWT access + rotating refresh)."""

import uuid
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from studyos_api.core.config import Settings, get_settings
from studyos_api.core.limiter import limiter
from studyos_api.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from studyos_api.security.passwords import hash_password
from studyos_api.security.tokens import mint_access_token
from studyos_api.services.auth_login_service import AuthLoginService
from studyos_api.services.refresh_sessions import RefreshSessionStore

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_refresh_store(request: Request) -> RefreshSessionStore:
    return request.app.state.refresh_store  # type: ignore[no-any-return]


def get_auth_login_service(request: Request) -> AuthLoginService:
    return request.app.state.auth_login_service  # type: ignore[no-any-return]


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    login_service: Annotated[AuthLoginService, Depends(get_auth_login_service)],
    store: Annotated[RefreshSessionStore, Depends(get_refresh_store)],
) -> TokenResponse:
    """Register a new user account."""
    # Attempt to authenticate with email (will fail if user doesn't exist)
    existing = await login_service.authenticate(
        email=body.email,
        password="",  # dummy password, just checking if email exists
        user_agent=None,
        ip=None,
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Get database pool from request
    pool = request.app.state.db_pool
    if pool is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )

    # Create new profile
    profile_id = uuid.uuid4()
    password_hash = hash_password(body.password)

    try:
        async with pool.acquire() as conn:
            # Insert profile
            await conn.execute(
                """INSERT INTO public.profiles (id, email, display_name, app_role)
                   VALUES ($1, $2, $3, 'student')""",
                profile_id,
                body.email,
                body.display_name,
            )

            # Insert auth credentials
            await conn.execute(
                """INSERT INTO public.auth_credentials (profile_id, password_hash)
                   VALUES ($1, $2)""",
                profile_id,
                password_hash,
            )
    except Exception as e:
        logger.exception("auth.register_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account",
        ) from e

    # Generate tokens
    ua = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    sub = str(profile_id)
    roles = ["student"]

    access = mint_access_token(settings, sub=sub, roles=roles)
    refresh, _exp = await store.create_session(
        profile_id=profile_id,
        sub=sub,
        roles=roles,
        family_id=None,
        user_agent=ua,
        ip=ip,
        ttl_seconds=settings.refresh_token_ttl_seconds,
    )

    logger.info("auth.register_ok", profile_id=str(profile_id), email=body.email)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.access_token_ttl_seconds,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
async def login(
    request: Request,
    body: LoginRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    login_service: Annotated[AuthLoginService, Depends(get_auth_login_service)],
    store: Annotated[RefreshSessionStore, Depends(get_refresh_store)],
) -> TokenResponse:
    ua = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    row = await login_service.authenticate(
        email=body.email,
        password=body.password,
        user_agent=ua,
        ip=ip,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    profile_id, sub, roles = row
    access = mint_access_token(settings, sub=sub, roles=roles)
    refresh, _exp = await store.create_session(
        profile_id=profile_id,
        sub=sub,
        roles=roles,
        family_id=None,
        user_agent=ua,
        ip=ip,
        ttl_seconds=settings.refresh_token_ttl_seconds,
    )
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.access_token_ttl_seconds,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("60/minute")
async def refresh(
    request: Request,
    body: RefreshRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    store: Annotated[RefreshSessionStore, Depends(get_refresh_store)],
) -> TokenResponse:
    ua = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    rotated = await store.validate_and_rotate(
        body.refresh_token,
        user_agent=ua,
        ip=ip,
        ttl_seconds=settings.refresh_token_ttl_seconds,
    )
    if rotated is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    ctx, new_refresh, _exp = rotated
    access = mint_access_token(settings, sub=ctx.sub, roles=ctx.roles)
    logger.info("auth.refresh_ok", profile_id=str(ctx.profile_id))
    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        expires_in=settings.access_token_ttl_seconds,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("60/minute")
async def logout(
    request: Request,
    body: LogoutRequest,
    store: Annotated[RefreshSessionStore, Depends(get_refresh_store)],
) -> Response:
    if body.refresh_token:
        await store.revoke_refresh(body.refresh_token)
        logger.info("auth.logout")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
