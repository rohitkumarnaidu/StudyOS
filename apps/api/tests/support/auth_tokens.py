"""JWT helpers for API tests — keep secrets aligned with `get_settings()` in tests."""

from studyos_api.core.config import get_settings
from studyos_api.security.tokens import mint_access_token


def bearer_token(*, roles: list[str], sub: str = "demo@studyos.app") -> str:
    return mint_access_token(get_settings(), sub=sub, roles=roles)
