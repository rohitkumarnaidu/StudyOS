"""Bulk import routes for notes."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request

from studyos_api.core.limiter import limiter
from studyos_api.core.responses import response_meta
from studyos_api.deps.auth import User, get_current_user
from studyos_api.services.bulk_import_service import BulkImportService, JobStatus

router = APIRouter()

_bulk_import_jobs: dict[str, JobStatus] = {}


def get_bulk_import_service() -> BulkImportService:
    return BulkImportService()


@router.post("")
@limiter.limit("5/minute")
async def create_bulk_import(
    request: Request,
    body: dict[str, Any],
    bulk_svc: Annotated[BulkImportService, Depends(get_bulk_import_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Create a bulk import job."""
    import uuid
    job = bulk_svc.create_job(str(uuid.uuid4()), total_files=body.get("total_files", 0))
    return {
        "data": job.to_dict(),
        "meta": response_meta(request, api_version="v1"),
    }


@router.get("/{job_id}")
@limiter.limit("30/minute")
async def get_bulk_import_job(
    request: Request,
    job_id: str,
    bulk_svc: Annotated[BulkImportService, Depends(get_bulk_import_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    """Get bulk import job status."""
    job = bulk_svc.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "data": job.to_dict(),
        "meta": response_meta(request, api_version="v1"),
    }
