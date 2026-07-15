"""PDF text extraction using pdfplumber."""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ExtractedPage:
    """Text extracted from a single PDF page."""

    page_number: int
    text: str
    word_count: int = 0
    has_images: bool = False

    def __post_init__(self) -> None:
        if self.word_count == 0 and self.text:
            self.word_count = len(self.text.split())


@dataclass
class ExtractedDocument:
    """Full extracted PDF document."""

    pages: list[ExtractedPage] = field(default_factory=list)
    total_pages: int = 0
    total_words: int = 0
    has_text: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_pages": self.total_pages,
            "total_words": self.total_words,
            "has_text": self.has_text,
            "pages": [
                {
                    "page_number": p.page_number,
                    "text": p.text[:500],
                    "word_count": p.word_count,
                }
                for p in self.pages
            ],
        }


class PdfTextExtractor:
    """Extract text from PDFs using pdfplumber."""

    def __init__(self) -> None:
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        try:
            import pdfplumber
            return True
        except ImportError:
            return False

    def extract(self, pdf_bytes: bytes) -> ExtractedDocument:
        """Extract text from PDF bytes."""
        if not self._available:
            return self._mock_extract(pdf_bytes)

        import pdfplumber

        doc = ExtractedDocument()
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            doc.total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                has_images = len(page.images) > 0
                doc.pages.append(ExtractedPage(
                    page_number=i + 1,
                    text=text,
                    has_images=has_images,
                ))
            doc.total_words = sum(p.word_count for p in doc.pages)
            doc.has_text = doc.total_words > 0

        logger.info(
            "pdf.extracted",
            pages=doc.total_pages,
            words=doc.total_words,
            has_text=doc.has_text,
        )
        return doc

    def _mock_extract(self, pdf_bytes: bytes) -> ExtractedDocument:
        """Fallback mock extraction for dev/testing."""
        text = pdf_bytes.decode("utf-8", errors="ignore")
        lines = text.split("\n")
        doc = ExtractedDocument()
        doc.total_pages = max(1, len(lines) // 3)
        doc.pages = [
            ExtractedPage(page_number=i + 1, text=line, word_count=len(line.split()))
            for i, line in enumerate(lines)
        ]
        doc.total_words = sum(p.word_count for p in doc.pages)
        doc.has_text = doc.total_words > 0
        return doc
