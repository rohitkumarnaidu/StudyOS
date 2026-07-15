"""Role- and permission-based access control (RBAC / ABAC-lite)."""

from collections.abc import Callable
from enum import StrEnum
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status

from studyos_api.deps.auth import get_current_user
from studyos_api.types.principal import User


class Permission(StrEnum):
    """Fine-grained action identifiers — map roles to these in ROLE_PERMISSIONS."""

    ME_READ = "me:read"
    ADMIN_PING = "admin:ping"
    AI_USE = "ai:use"


ROLE_PERMISSIONS: dict[str, frozenset[Permission]] = {
    "student": frozenset({Permission.ME_READ, Permission.AI_USE}),
    "teacher": frozenset({Permission.ME_READ, Permission.AI_USE}),
    "institute_admin": frozenset({Permission.ME_READ, Permission.ADMIN_PING, Permission.AI_USE}),
    "platform_admin": frozenset({Permission.ME_READ, Permission.ADMIN_PING, Permission.AI_USE}),
    "admin": frozenset({Permission.ME_READ, Permission.ADMIN_PING, Permission.AI_USE}),
}


def require_permissions(*required: Permission) -> Callable[..., Any]:
    """Require an authenticated principal with all listed permissions (union of role grants)."""

    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        effective: set[Permission] = set()
        for role in user["roles"]:
            effective |= ROLE_PERMISSIONS.get(role, frozenset())
        if not set(required).issubset(effective):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency


def require_roles(*allowed_role_names: str) -> Callable[..., Any]:
    """Require at least one of the named roles (coarser than require_permissions)."""

    def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if not set(allowed_role_names) & set(user["roles"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency
