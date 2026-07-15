"""Credential verification — JWT access tokens and optional legacy demo bearers."""

from studyos_api.core.config import get_settings
from studyos_api.security.tokens import decode_access_token
from studyos_api.types.principal import User


class AuthService:
    """Validates bearer tokens and returns a principal."""

    def resolve_optional_user(self, bearer_token: str | None) -> User | None:
        if not bearer_token:
            return None
        settings = get_settings()
        claims = decode_access_token(bearer_token, settings)
        if claims is not None:
            roles_raw = claims.get("roles", [])
            roles = [str(r) for r in roles_raw] if isinstance(roles_raw, list) else []
            sub = str(claims.get("sub", ""))
            return User(sub=sub, roles=roles)
        if settings.allow_legacy_demo_bearer:
            if bearer_token == "demo":
                u: User = {"sub": "demo-user", "roles": ["student"]}
                return u
            if bearer_token == "admin":
                u2: User = {"sub": "admin-user", "roles": ["admin"]}
                return u2
        return None
