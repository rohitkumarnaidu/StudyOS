"""Note search routes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request

from studyos_api.core.limiter import limiter
from studyos_api.core.responses import response_meta
from studyos_api.deps.auth import User, get_current_user
from studyos_api.services.note_search import NoteSearch

router = APIRouter()


def get_note_search() -> NoteSearch:
    return NoteSearch()


@router.get("")
@limiter.limit("30/minute")
async def search_notes(
    request: Request,
    q: str = Query(..., min_length=1),
    chapter_id: str | None = Query(None),
    search_svc: Annotated[NoteSearch, Depends(get_note_search)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Search notes by keyword."""
    results = search_svc.search(q, chapter_id=chapter_id)
    return {
        "data": [r.to_dict() for r in results],
        "meta": response_meta(request, api_version="v1"),
    }
