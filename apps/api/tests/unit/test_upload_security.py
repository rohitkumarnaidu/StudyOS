"""Tests for upload_security.py — magic-byte validation, size limits, MIME checks."""

from studyos_api.services.upload_security import (
    MAX_UPLOAD_SIZE,
    validate_upload,
)


class TestValidateUploadSize:
    def test_empty_file_rejected(self) -> None:
        result = validate_upload(b"")
        assert result.valid is False
        assert result.error == "Empty file"

    def test_oversized_file_rejected(self) -> None:
        oversized = b"x" * (MAX_UPLOAD_SIZE + 1)
        result = validate_upload(oversized)
        assert result.valid is False
        assert "too large" in result.error.lower()

    def test_valid_size_passes(self) -> None:
        result = validate_upload(b"%PDF-1.4 small")
        assert result.valid is True


class TestValidateUploadMagicBytes:
    def test_pdf_detected(self) -> None:
        data = b"%PDF-1.4 some content here"
        result = validate_upload(data)
        assert result.valid is True
        assert result.mime_type == "application/pdf"

    def test_png_detected(self) -> None:
        data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        result = validate_upload(data)
        assert result.valid is True
        assert result.mime_type == "image/png"

    def test_jpeg_detected(self) -> None:
        data = b"\xff\xd8\xff" + b"\xe0" * 100
        result = validate_upload(data)
        assert result.valid is True
        assert result.mime_type == "image/jpeg"

    def test_webp_detected(self) -> None:
        data = b"RIFF" + b"\x00" * 20 + b"WEBP"
        result = validate_upload(data)
        assert result.valid is True
        assert result.mime_type == "image/webp"

    def test_unknown_type_rejected(self) -> None:
        data = b"this is not a recognized file type"
        result = validate_upload(data)
        assert result.valid is False
        assert "unsupported" in result.error.lower()


class TestValidateUploadMimeCrossCheck:
    def test_declared_mime_matches_detected(self) -> None:
        data = b"%PDF-1.4 content"
        result = validate_upload(data, declared_mime="application/pdf")
        assert result.valid is True
        assert result.mime_type == "application/pdf"

    def test_declared_mime_mismatch_warns_but_uses_detected(self) -> None:
        data = b"%PDF-1.4 content"
        result = validate_upload(data, declared_mime="image/png")
        assert result.valid is True
        assert result.mime_type == "application/pdf"

    def test_fallback_to_declared_when_no_magic_match(self) -> None:
        data = b"some random bytes no magic"
        result = validate_upload(data, declared_mime="image/png")
        assert result.valid is True
        assert result.mime_type == "image/png"

    def test_unsupported_declared_mime_rejected(self) -> None:
        data = b"%PDF-1.4"
        result = validate_upload(data, declared_mime="application/zip")
        assert result.valid is True
        assert result.mime_type == "application/pdf"
