"""Identity / session DTOs."""

from typing import Literal

from pydantic import BaseModel, Field

from studyos_api.schemas.common import ResponseMeta


class PublicUser(BaseModel):
    sub: str
    roles: list[str] = Field(default_factory=list)


class MePayload(BaseModel):
    authenticated: bool
    user: PublicUser | None = None


class AdminPingPayload(BaseModel):
    status: str


class MeSuccessResponse(BaseModel):
    success: Literal[True] = True
    data: MePayload
    meta: ResponseMeta


class AdminPingSuccessResponse(BaseModel):
    success: Literal[True] = True
    data: AdminPingPayload
    meta: ResponseMeta
