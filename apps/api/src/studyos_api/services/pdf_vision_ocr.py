"""Vision model OCR for scanned PDFs."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class OcrResult:
    """OCR extraction result for a page."""

    page_number: int
    text: str
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_number": self.page_number,
            "text": self.text,
            "confidence": round(self.confidence, 2),
        }


class PdfVisionOcr:
    """Extract text from scanned PDFs using vision models (OpenAI GPT-4o, etc.)."""

    def __init__(self, api_key: str = "", model: str = "gpt-4o") -> None:
        self._api_key = api_key
        self._model = model

    def ocr_page(self, image_bytes: bytes, page_number: int) -> OcrResult:
        """OCR a single page image."""
        if not self._api_key:
            return self._mock_ocr(image_bytes, page_number)

        b64 = base64.b64encode(image_bytes).decode()

        import httpx

        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this image. Preserve formatting where possible.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"},
                            },
                        ],
                    }
                ],
                "max_tokens": 4000,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        return OcrResult(page_number=page_number, text=text, confidence=0.95)

    def _mock_ocr(self, image_bytes: bytes, page_number: int) -> OcrResult:
        """Mock OCR for dev/testing."""
        return OcrResult(
            page_number=page_number,
            text=f"OCR extracted text for page {page_number}. This is mock data for testing.",
            confidence=0.85,
        )
