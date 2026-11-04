"""Bulk import service — queue-based PDF processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BulkImportJob:
    """A bulk import job tracking multiple PDFs."""

    id: str
    status: JobStatus = JobStatus.PENDING
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    file_results: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = ""
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status.value,
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "progress_pct": round(self.processed_files / max(self.total_files, 1) * 100, 1),
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


class BulkImportService:
    """Manage bulk PDF import jobs."""

    def __init__(self) -> None:
        self._jobs: dict[str, BulkImportJob] = {}

    def create_job(self, job_id: str, total_files: int) -> BulkImportJob:
        """Create a new bulk import job."""
        from datetime import datetime

        job = BulkImportJob(
            id=job_id,
            total_files=total_files,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._jobs[job_id] = job
        logger.info("bulk_import.created", job_id=job_id, files=total_files)
        return job

    def update_progress(
        self, job_id: str, success: bool, result: dict[str, Any] | None = None
    ) -> None:
        """Update job progress after processing a file."""
        job = self._jobs.get(job_id)
        if not job:
            return

        job.processed_files += 1
        if not success:
            job.failed_files += 1

        if result:
            job.file_results.append(result)

        if job.processed_files >= job.total_files:
            job.status = JobStatus.COMPLETED if job.failed_files == 0 else JobStatus.FAILED
            from datetime import datetime

            job.completed_at = datetime.now(UTC).isoformat()

    def get_job(self, job_id: str) -> BulkImportJob | None:
        """Get job by ID."""
        return self._jobs.get(job_id)

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or processing job."""
        job = self._jobs.get(job_id)
        if job and job.status in (JobStatus.PENDING, JobStatus.PROCESSING):
            job.status = JobStatus.CANCELLED
            return True
        return False

    def list_jobs(self) -> list[BulkImportJob]:
        """List all jobs."""
        return list(self._jobs.values())

    def reset(self) -> None:
        """Clear all jobs (for testing)."""
        self._jobs.clear()
