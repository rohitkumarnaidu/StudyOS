"""Tests for pdf_text_extractor service."""

from studyos_api.services.pdf_text_extractor import (
    ExtractedDocument,
    ExtractedPage,
    PdfTextExtractor,
)


class TestExtractedPage:
    def test_word_count_auto_computed(self):
        page = ExtractedPage(page_number=1, text="hello world test")
        assert page.word_count == 3

    def test_word_count_zero_for_empty_text(self):
        page = ExtractedPage(page_number=1, text="")
        assert page.word_count == 0

    def test_word_count_preserved_if_set(self):
        page = ExtractedPage(page_number=1, text="hello world", word_count=10)
        assert page.word_count == 10

    def test_has_images_default_false(self):
        page = ExtractedPage(page_number=1, text="test")
        assert page.has_images is False


class TestExtractedDocument:
    def test_to_dict_empty(self):
        doc = ExtractedDocument()
        result = doc.to_dict()
        assert result["total_pages"] == 0
        assert result["total_words"] == 0
        assert result["has_text"] is True
        assert result["pages"] == []

    def test_to_dict_with_pages(self):
        doc = ExtractedDocument(
            pages=[
                ExtractedPage(page_number=1, text="hello world"),
                ExtractedPage(page_number=2, text="foo bar baz"),
            ],
            total_pages=2,
            total_words=5,
        )
        result = doc.to_dict()
        assert result["total_pages"] == 2
        assert result["total_words"] == 5
        assert len(result["pages"]) == 2
        assert result["pages"][0]["page_number"] == 1

    def test_to_dict_truncates_long_text(self):
        long_text = "x" * 1000
        doc = ExtractedDocument(
            pages=[ExtractedPage(page_number=1, text=long_text)],
            total_pages=1,
            total_words=1,
        )
        result = doc.to_dict()
        assert len(result["pages"][0]["text"]) <= 500


class TestPdfTextExtractor:
    def test_check_availability(self):
        extractor = PdfTextExtractor()
        # Should not crash regardless of pdfplumber availability
        assert isinstance(extractor._available, bool)

    def test_extract_mock_fallback(self):
        extractor = PdfTextExtractor()
        extractor._available = False
        pdf_bytes = b"Line 1\nLine 2\nLine 3\nLine 4"
        result = extractor.extract(pdf_bytes)
        assert result.total_pages >= 1
        assert len(result.pages) >= 1
        assert result.total_words > 0

    def test_extract_empty_bytes(self):
        extractor = PdfTextExtractor()
        extractor._available = False
        result = extractor.extract(b"")
        assert result.total_pages == 1
        assert result.total_words == 0

    def test_extract_binary_garbage(self):
        extractor = PdfTextExtractor()
        extractor._available = False
        result = extractor.extract(b"\x00\x01\x02\x03\x04\x05")
        assert result.total_pages >= 1
