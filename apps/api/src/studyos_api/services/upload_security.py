"""File upload security helpers — magic-byte validation, size limits, MIME checks."""

from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)

# Max upload size: 50 MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
}

# Magic bytes for common file types
MAGIC_BYTES = {
    b"%PDF": "application/pdf",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"RIFF": "image/webp",  # WebP starts with RIFF
}


@dataclass
class UploadValidationResult:
    valid: bool
    mime_type: str | None = None
    error: str | None = None


def validate_upload(file_bytes: bytes, declared_mime: str | None = None) -> UploadValidationResult:
    """Validate uploaded file using magic bytes and size checks."""
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        return UploadValidationResult(
            valid=False,
            error=f"File too large. Max: {MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )

    if len(file_bytes) == 0:
        return UploadValidationResult(valid=False, error="Empty file")

    # Detect MIME type from magic bytes
    detected_mime = None
    for magic, mime in MAGIC_BYTES.items():
        if file_bytes[: len(magic)] == magic:
            detected_mime = mime
            break

    if detected_mime is None:
        # Fallback: try to detect from declared MIME
        if declared_mime and declared_mime in ALLOWED_MIME_TYPES:
            detected_mime = declared_mime
        else:
            return UploadValidationResult(
                valid=False,
                error="Unsupported file type. Allowed: PDF, PNG, JPEG, WebP",
            )

    if detected_mime not in ALLOWED_MIME_TYPES:
        return UploadValidationResult(
            valid=False,
            error=f"File type '{detected_mime}' not allowed",
        )

    # Cross-check declared vs detected
    if declared_mime and declared_mime != detected_mime:
        logger.warning(
            "upload.mime_mismatch",
            declared=declared_mime,
            detected=detected_mime,
        )

    return UploadValidationResult(valid=True, mime_type=detected_mime)
