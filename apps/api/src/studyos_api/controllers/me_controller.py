"""HTTP orchestration: map requests to services and standard response models."""

from starlette.requests import Request

from studyos_api.core.responses import response_meta
from studyos_api.schemas.me import AdminPingPayload, AdminPingSuccessResponse, MeSuccessResponse
from studyos_api.services.me_service import MeService
from studyos_api.types.principal import User


class MeController:
    def __init__(self, service: MeService | None = None) -> None:
        self._me = service or MeService()

    def get_me(self, request: Request, user: User | None) -> MeSuccessResponse:
        payload = self._me.build_me_payload(user)
        return MeSuccessResponse(data=payload, meta=response_meta(request, api_version="v1"))

    def admin_ping(self, request: Request, _user: User) -> AdminPingSuccessResponse:
        _ = _user
        return AdminPingSuccessResponse(
            data=AdminPingPayload(status="admin-ok"),
            meta=response_meta(request, api_version="v1"),
        )
