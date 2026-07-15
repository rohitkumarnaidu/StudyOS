"""Note export routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request

from studyos_api.core.limiter import limiter
from studyos_api.core.responses import response_meta
from studyos_api.deps.auth import User, get_current_user
from studyos_api.services.note_export import NoteExport

router = APIRouter()

_notes_db: dict[str, dict[str, Any]] = {}


def get_note_export() -> NoteExport:
    return NoteExport()


@router.get("")
@limiter.limit("10/minute")
async def export_notes(
    request: Request,
    fmt: str = Query("json", regex="^(json|markdown|csv|zip)$"),
    export_svc: Annotated[NoteExport, Depends(get_note_export)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Export notes in specified format."""
    notes = [n for n in _notes_db.values() if n["profile_id"] == current_user["sub"]]

    if fmt == "json":
        result = export_svc.export_json(notes)
    elif fmt == "markdown":
        result = export_svc.export_markdown(notes)
    elif fmt == "csv":
        result = export_svc.export_csv(notes)
    else:
        result = export_svc.export_zip(notes)

    return {
        "data": result.to_dict(),
        "meta": response_meta(request, api_version="v1"),
    }
