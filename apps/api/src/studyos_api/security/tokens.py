"""Short-lived access JWTs (HS256). Refresh material lives outside JWT."""

import time
from typing import Any

import jwt

from studyos_api.core.config import Settings


def mint_access_token(settings: Settings, *, sub: str, roles: list[str]) -> str:
    now = int(time.time())
    payload: dict[str, Any] = {
        "iss": settings.jwt_issuer,
        "sub": sub,
        "roles": roles,
        "typ": "access",
        "iat": now,
        "exp": now + settings.access_token_ttl_seconds,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict[str, Any] | None:
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            options={"require": ["exp", "iss", "sub"]},
        )
    except jwt.PyJWTError:
        return None
    if claims.get("typ") != "access":
        return None
    return claims
