"""Example request bodies for documentation and integration tests."""

from typing import Literal

from pydantic import BaseModel, Field

from studyos_api.schemas.common import ResponseMeta


class EchoRequest(BaseModel):
    message: str = Field(min_length=1, max_length=256, description="Short message to echo back")


class EchoPayload(BaseModel):
    echo: str


class EchoSuccessResponse(BaseModel):
    success: Literal[True] = True
    data: EchoPayload
    meta: ResponseMeta
