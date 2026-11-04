"""PDF processor — main orchestrator for PDF → structured notes pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

from studyos_api.services.mindmap_parser import MindMapParser, MindMapTree
from studyos_api.services.note_embedder import NoteEmbedder
from studyos_api.services.note_structurer import NoteStructurer, StructuredNote
from studyos_api.services.pdf_text_extractor import ExtractedDocument, PdfTextExtractor
from studyos_api.services.pdf_vision_ocr import OcrResult, PdfVisionOcr

logger = structlog.get_logger(__name__)


class PdfType(str, Enum):
    TEXT = "text"
    SCANNED = "scanned"
    MINDMAP = "mindmap"


@dataclass
class ProcessingResult:
    """Result of processing a PDF."""

    note_id: str
    pdf_type: PdfType
    extracted_text: str = ""
    structured_note: StructuredNote | None = None
    mindmap_tree: MindMapTree | None = None
    ocr_results: list[OcrResult] = field(default_factory=list)
    page_count: int = 0
    status: str = "ready"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "note_id": self.note_id,
            "pdf_type": self.pdf_type.value,
            "page_count": self.page_count,
            "status": self.status,
            "summary": self.structured_note.summary if self.structured_note else None,
            "concepts_count": len(self.structured_note.concepts) if self.structured_note else 0,
            "mindmap_nodes": self.mindmap_tree.total_nodes if self.mindmap_tree else 0,
            "error": self.error,
        }


class PdfProcessor:
    """Main orchestrator: detect type → extract → structure → embed."""

    def __init__(
        self,
        text_extractor: PdfTextExtractor | None = None,
        vision_ocr: PdfVisionOcr | None = None,
        structurer: NoteStructurer | None = None,
        embedder: NoteEmbedder | None = None,
        mindmap_parser: MindMapParser | None = None,
    ) -> None:
        self._text_extractor = text_extractor or PdfTextExtractor()
        self._vision_ocr = vision_ocr or PdfVisionOcr()
        self._structurer = structurer or NoteStructurer()
        self._embedder = embedder or NoteEmbedder()
        self._mindmap_parser = mindmap_parser or MindMapParser()

    def process(self, pdf_bytes: bytes, note_id: str, title: str = "") -> ProcessingResult:
        """Process a PDF through the full pipeline."""
        try:
            extracted = self._text_extractor.extract(pdf_bytes)
            pdf_type = self._detect_type(extracted)

            result = ProcessingResult(
                note_id=note_id,
                pdf_type=pdf_type,
                page_count=extracted.total_pages,
            )

            full_text = "\n".join(p.text for p in extracted.pages)
            result.extracted_text = full_text

            if pdf_type == PdfType.MINDMAP:
                result.mindmap_tree = self._mindmap_parser.parse(full_text)
            else:
                result.structured_note = self._structurer.structure(full_text, title or note_id)
                self._embedder.embed_note(full_text, note_id)

            result.status = "ready"
            logger.info(
                "pdf.processed", note_id=note_id, type=pdf_type.value, pages=result.page_count
            )
            return result

        except Exception as e:
            logger.exception("pdf.processing_failed", note_id=note_id)
            return ProcessingResult(
                note_id=note_id,
                pdf_type=PdfType.TEXT,
                status="failed",
                error=str(e),
            )

    def _detect_type(self, extracted: ExtractedDocument) -> PdfType:
        """Detect PDF type from extraction results."""
        if extracted.total_words == 0:
            return PdfType.SCANNED

        lower_text = "\n".join(p.text for p in extracted.pages).lower()
        if any(kw in lower_text for kw in ["mind map", "mindmap", "concept map"]):
            return PdfType.MINDMAP

        pages_with_images = sum(1 for p in extracted.pages if p.has_images)
        if pages_with_images > extracted.total_pages * 0.5:
            return PdfType.SCANNED

        return PdfType.TEXT
