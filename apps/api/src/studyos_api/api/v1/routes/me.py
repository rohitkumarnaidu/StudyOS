from typing import Annotated

from fastapi import APIRouter, Depends, Request

from studyos_api.controllers.me_controller import MeController
from studyos_api.deps.auth import get_current_user_optional
from studyos_api.deps.rbac import Permission, require_permissions
from studyos_api.schemas.me import AdminPingSuccessResponse, MeSuccessResponse
from studyos_api.types.principal import User

router = APIRouter()
_controller = MeController()


@router.get("/me", response_model=MeSuccessResponse)
def read_me(
    request: Request,
    user: Annotated[User | None, Depends(get_current_user_optional)],
) -> MeSuccessResponse:
    return _controller.get_me(request, user)


@router.get("/admin/ping", response_model=AdminPingSuccessResponse)
def admin_ping(
    request: Request,
    user: Annotated[User, Depends(require_permissions(Permission.ADMIN_PING))],
) -> AdminPingSuccessResponse:
    return _controller.admin_ping(request, user)
