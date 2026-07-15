from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from studyos_api.services.auth_service import AuthService
from studyos_api.types.principal import User

__all__ = ["User", "get_auth_service", "get_current_user_optional", "get_current_user"]


def get_auth_service() -> AuthService:
    return AuthService()


def _parse_bearer(authorization: str | None) -> str | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    return authorization.split(" ", 1)[1].strip() or None


def get_current_user_optional(
    auth: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> User | None:
    token = _parse_bearer(authorization)
    return auth.resolve_optional_user(token)


def get_current_user(user: Annotated[User | None, Depends(get_current_user_optional)]) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid credentials",
        )
    return user
