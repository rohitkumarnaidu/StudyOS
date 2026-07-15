"""Standard success envelope and metadata for versioned JSON APIs."""

from typing import Literal

from pydantic import BaseModel, Field


class ResponseMeta(BaseModel):
    """Correlation and versioning metadata included on successful responses."""

    request_id: str | None = None
    api_version: str = "v1"


class SuccessEnvelope[T](BaseModel):
    """Uniform success payload for business endpoints (health probes may omit this)."""

    success: Literal[True] = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    model_config = {"json_schema_extra": {"examples": [{"success": True, "data": {}, "meta": {}}]}}
