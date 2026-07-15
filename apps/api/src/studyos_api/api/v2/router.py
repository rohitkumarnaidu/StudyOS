from fastapi import APIRouter

router = APIRouter()


@router.get("/status", tags=["version"])
def v2_status() -> dict[str, object]:
    return {
        "api_version": "v2",
        "status": "reserved",
        "message": "v2 namespace is reserved for future breaking changes.",
    }
