from fastapi import APIRouter, Request

from studyos_api.core.responses import response_meta
from studyos_api.schemas.examples import EchoPayload, EchoRequest, EchoSuccessResponse

router = APIRouter()


@router.post("/examples/echo", response_model=EchoSuccessResponse, tags=["examples"])
def validated_echo(request: Request, body: EchoRequest) -> EchoSuccessResponse:
    """Demonstrates Pydantic body validation + standard success envelope."""
    return EchoSuccessResponse(
        data=EchoPayload(echo=body.message),
        meta=response_meta(request, api_version="v1"),
    )
