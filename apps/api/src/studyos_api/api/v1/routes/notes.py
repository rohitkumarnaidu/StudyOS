"""Notes API endpoints — CRUD, highlights, bookmarks, personal notes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile

from studyos_api.core.limiter import limiter
from studyos_api.core.responses import response_meta
from studyos_api.deps.auth import User, get_current_user
from studyos_api.services.pdf_processor import PdfProcessor

router = APIRouter()

_notes_db: dict[str, dict[str, Any]] = {}
_highlights_db: dict[str, list[dict[str, Any]]] = {}
_bookmarks_db: dict[str, list[dict[str, Any]]] = {}
_personal_notes_db: dict[str, list[dict[str, Any]]] = {}


def get_pdf_processor() -> PdfProcessor:
    return PdfProcessor()


@router.post("/upload")
@limiter.limit("10/minute")
async def upload_note(
    request: Request,
    file: UploadFile,
    chapter_id: str | None = Query(None),
    processor: Annotated[PdfProcessor, Depends(get_pdf_processor)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Upload and process a PDF note."""
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    import uuid
    note_id = str(uuid.uuid4())

    result = processor.process(content, note_id, file.filename)

    note = {
        "id": note_id,
        "title": file.filename,
        "note_type": "pdf",
        "status": result.status,
        "file_size": len(content),
        "page_count": result.page_count,
        "summary": result.structured_note.summary if result.structured_note else None,
        "tags": result.structured_note.chapter_tags if result.structured_note else [],
        "chapter_id": chapter_id,
        "profile_id": current_user["sub"],
        "created_at": result.status,
    }
    _notes_db[note_id] = note

    return {
        "data": {**note, "processing_result": result.to_dict()},
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("")
@limiter.limit("60/minute")
async def list_notes(
    request: Request,
    chapter_id: str | None = Query(None),
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """List user's notes."""
    notes = [
        n for n in _notes_db.values()
        if n["profile_id"] == current_user["sub"]
        and (not chapter_id or n.get("chapter_id") == chapter_id)
    ]
    return {
        "data": notes,
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/{note_id}")
@limiter.limit("60/minute")
async def get_note(
    request: Request,
    note_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get a single note."""
    note = _notes_db.get(note_id)
    if not note or note["profile_id"] != current_user["sub"]:
        raise HTTPException(status_code=404, detail="Note not found")
    return {
        "data": note,
        "meta": response_meta(request, api_version="v1"),
    }


@router.delete("/{note_id}")
@limiter.limit("30/minute")
async def delete_note(
    request: Request,
    note_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Delete a note."""
    note = _notes_db.get(note_id)
    if not note or note["profile_id"] != current_user["sub"]:
        raise HTTPException(status_code=404, detail="Note not found")
    del _notes_db[note_id]
    return {
        "data": {"deleted": True},
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/{note_id}/highlights")
@limiter.limit("60/minute")
async def list_highlights(
    request: Request,
    note_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """List highlights for a note."""
    highlights = _highlights_db.get(note_id, [])
    return {
        "data": highlights,
        "meta": response_meta(request, api_version="v1"),
    }


@router.post("/{note_id}/highlights")
@limiter.limit("60/minute")
async def create_highlight(
    request: Request,
    note_id: str,
    body: dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Create a highlight."""
    import uuid
    highlight = {
        "id": str(uuid.uuid4()),
        "note_id": note_id,
        "page_number": body.get("page_number"),
        "color": body.get("color", "yellow"),
        "text_content": body.get("text_content", ""),
        "profile_id": current_user["sub"],
        "created_at": body.get("created_at", ""),
    }
    _highlights_db.setdefault(note_id, []).append(highlight)
    return {
        "data": highlight,
        "meta": response_meta(request, api_version="v1"),
    }


@router.delete("/highlights/{highlight_id}")
@limiter.limit("30/minute")
async def delete_highlight(
    request: Request,
    highlight_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Delete a highlight."""
    for note_id, highlights in _highlights_db.items():
        _highlights_db[note_id] = [h for h in highlights if h["id"] != highlight_id]
    return {
        "data": {"deleted": True},
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/{note_id}/bookmarks")
@limiter.limit("60/minute")
async def list_bookmarks(
    request: Request,
    note_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """List bookmarks for a note."""
    bookmarks = _bookmarks_db.get(note_id, [])
    return {
        "data": bookmarks,
        "meta": response_meta(request, api_version="v1"),
    }


@router.post("/{note_id}/bookmarks")
@limiter.limit("60/minute")
async def create_bookmark(
    request: Request,
    note_id: str,
    body: dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Create a bookmark."""
    import uuid
    bookmark = {
        "id": str(uuid.uuid4()),
        "note_id": note_id,
        "page_number": body.get("page_number", 1),
        "label": body.get("label"),
        "profile_id": current_user["sub"],
        "created_at": body.get("created_at", ""),
    }
    _bookmarks_db.setdefault(note_id, []).append(bookmark)
    return {
        "data": bookmark,
        "meta": response_meta(request, api_version="v1"),
    }


@router.delete("/bookmarks/{bookmark_id}")
@limiter.limit("30/minute")
async def delete_bookmark(
    request: Request,
    bookmark_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Delete a bookmark."""
    for note_id, bookmarks in _bookmarks_db.items():
        _bookmarks_db[note_id] = [b for b in bookmarks if b["id"] != bookmark_id]
    return {
        "data": {"deleted": True},
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/{note_id}/personal-notes")
@limiter.limit("60/minute")
async def list_personal_notes(
    request: Request,
    note_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """List personal notes for a note."""
    personal_notes = _personal_notes_db.get(note_id, [])
    return {
        "data": personal_notes,
        "meta": response_meta(request, api_version="v1"),
    }


@router.post("/{note_id}/personal-notes")
@limiter.limit("60/minute")
async def create_personal_note(
    request: Request,
    note_id: str,
    body: dict[str, Any],
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Create a personal note."""
    import uuid
    personal_note = {
        "id": str(uuid.uuid4()),
        "note_id": note_id,
        "page_number": body.get("page_number"),
        "content": body.get("content", ""),
        "profile_id": current_user["sub"],
        "created_at": body.get("created_at", ""),
    }
    _personal_notes_db.setdefault(note_id, []).append(personal_note)
    return {
        "data": personal_note,
        "meta": response_meta(request, api_version="v1"),
    }
