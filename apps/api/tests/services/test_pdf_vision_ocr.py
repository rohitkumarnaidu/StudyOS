"""Tests for pdf_vision_ocr service."""

from studyos_api.services.pdf_vision_ocr import OcrResult, PdfVisionOcr


class TestOcrResult:
    def test_to_dict(self):
        result = OcrResult(page_number=1, text="Hello world", confidence=0.95)
        d = result.to_dict()
        assert d["page_number"] == 1
        assert d["text"] == "Hello world"
        assert d["confidence"] == 0.95

    def test_to_dict_rounds_confidence(self):
        result = OcrResult(page_number=1, text="Test", confidence=0.95678)
        d = result.to_dict()
        assert d["confidence"] == 0.96

    def test_default_confidence(self):
        result = OcrResult(page_number=1, text="Test")
        assert result.confidence == 0.0


class TestPdfVisionOcr:
    def test_init_default(self):
        ocr = PdfVisionOcr()
        assert ocr._api_key == ""
        assert ocr._model == "gpt-4o"

    def test_init_custom(self):
        ocr = PdfVisionOcr(api_key="sk-test", model="gpt-4o-mini")
        assert ocr._api_key == "sk-test"
        assert ocr._model == "gpt-4o-mini"

    def test_mock_ocr(self):
        ocr = PdfVisionOcr(api_key="")
        result = ocr.ocr_page(b"fake image data", page_number=1)
        assert result.page_number == 1
        assert "page 1" in result.text
        assert result.confidence == 0.85

    def test_mock_ocr_multiple_pages(self):
        ocr = PdfVisionOcr(api_key="")
        result1 = ocr.ocr_page(b"page1", page_number=1)
        result2 = ocr.ocr_page(b"page2", page_number=2)
        assert result1.page_number == 1
        assert result2.page_number == 2
        assert result1.confidence == 0.85
        assert result2.confidence == 0.85

    def test_mock_ocr_with_none_api_key(self):
        ocr = PdfVisionOcr(api_key=None)
        result = ocr.ocr_page(b"test", page_number=5)
        assert result.page_number == 5
        assert result.confidence == 0.85
