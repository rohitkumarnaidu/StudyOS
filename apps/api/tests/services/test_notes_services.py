"""Tests for Phase 4 notes services."""

from studyos_api.services.bulk_import_service import BulkImportService, JobStatus
from studyos_api.services.mindmap_parser import MindMapNode, MindMapParser
from studyos_api.services.note_embedder import NoteEmbedder, RecursiveChunker, cosine_similarity
from studyos_api.services.note_export import NoteExport
from studyos_api.services.note_search import NoteDocument, NoteSearch
from studyos_api.services.note_structurer import NoteStructurer
from studyos_api.services.pdf_processor import PdfProcessor, PdfType
from studyos_api.services.pdf_text_extractor import PdfTextExtractor
from studyos_api.services.pdf_vision_ocr import PdfVisionOcr


class TestPdfTextExtractor:
    def test_mock_extract(self) -> None:
        extractor = PdfTextExtractor()
        result = extractor.extract(b"fake pdf content")
        assert result.total_pages >= 1
        assert result.total_words > 0
        assert result.has_text is True

    def test_extract_page_text(self) -> None:
        extractor = PdfTextExtractor()
        result = extractor.extract(b"page one\npage two\npage three")
        assert len(result.pages) >= 1
        assert result.pages[0].page_number == 1
        assert len(result.pages[0].text) > 0


class TestPdfVisionOcr:
    def test_mock_ocr(self) -> None:
        ocr = PdfVisionOcr()
        result = ocr.ocr_page(b"fake image", page_number=1)
        assert result.page_number == 1
        assert len(result.text) > 0
        assert result.confidence > 0


class TestMindMapParser:
    def test_parse_flat_text(self) -> None:
        parser = MindMapParser()
        text = "Main Topic\n  Subtopic A\n    Detail 1\n    Detail 2\n  Subtopic B"
        tree = parser.parse(text)
        assert tree.root.label == "Main Topic"
        assert tree.total_nodes >= 4

    def test_parse_empty_text(self) -> None:
        parser = MindMapParser()
        tree = parser.parse("")
        assert tree.root.label == "Empty Mind Map"
        assert tree.total_nodes == 1

    def test_node_to_dict(self) -> None:
        node = MindMapNode(id="1", label="Test")
        d = node.to_dict()
        assert d["id"] == "1"
        assert d["label"] == "Test"
        assert d["children"] == []


class TestNoteStructurer:
    def test_structure_text(self) -> None:
        structurer = NoteStructurer()
        text = "This is a long paragraph about physics concepts. " * 10
        note = structurer.structure(text, "Physics Notes")
        assert note.title == "Physics Notes"
        assert len(note.summary) > 0
        assert "physics" in note.chapter_tags

    def test_extract_formulas(self) -> None:
        structurer = NoteStructurer()
        text = "E = mc²\n∫ f(x) dx\n∑ i=1 to n"
        formulas = structurer._extract_formulas(text)
        assert len(formulas) > 0

    def test_estimate_study_time(self) -> None:
        structurer = NoteStructurer()
        assert structurer._estimate_study_time("word " * 200) >= 5


class TestNoteEmbedder:
    def test_mock_embedding(self) -> None:
        embedder = NoteEmbedder()
        embedding = embedder._mock_embedding("test text")
        assert len(embedding) == 16
        assert all(0 <= v <= 1 for v in embedding)

    def test_chunk_text(self) -> None:
        chunker = RecursiveChunker(chunk_size=10, overlap=3)
        text = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12"
        chunks = chunker.chunk(text)
        assert len(chunks) > 1

    def test_cosine_similarity_identical(self) -> None:
        vec = [1.0, 0.0, 0.0]
        assert cosine_similarity(vec, vec) == 1.0

    def test_cosine_similarity_orthogonal(self) -> None:
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


class TestPdfProcessor:
    def test_process_text_pdf(self) -> None:
        processor = PdfProcessor()
        result = processor.process(b"fake pdf content", "note-1", "Test Note")
        assert result.note_id == "note-1"
        assert result.status == "ready"
        assert result.pdf_type == PdfType.TEXT

    def test_process_mindmap_pdf(self) -> None:
        processor = PdfProcessor()
        content = b"This is a mind map diagram\n  Main Topic\n    subtopic\n      detail"
        result = processor.process(content, "note-2")
        assert result.pdf_type == PdfType.MINDMAP
        assert result.mindmap_tree is not None

    def test_process_error(self) -> None:
        processor = PdfProcessor()
        result = processor.process(b"", "note-3")
        assert result.status in ("ready", "failed")


class TestNoteSearch:
    def test_index_and_search(self) -> None:
        search = NoteSearch()
        doc = NoteDocument(
            note_id="n1",
            title="Physics Notes",
            content="Newton's laws of motion are fundamental principles in physics.",
            tags=["physics"],
        )
        search.index_note(doc)
        results = search.search("Newton physics")
        assert len(results) > 0
        assert results[0].note_id == "n1"

    def test_search_no_match(self) -> None:
        search = NoteSearch()
        doc = NoteDocument(note_id="n1", title="Math", content="Calculus and derivatives")
        search.index_note(doc)
        results = search.search("biology")
        assert len(results) == 0

    def test_remove_note(self) -> None:
        search = NoteSearch()
        doc = NoteDocument(note_id="n1", title="Test", content="content")
        search.index_note(doc)
        search.remove_note("n1")
        results = search.search("Test")
        assert len(results) == 0

    def test_extract_snippet(self) -> None:
        search = NoteSearch()
        text = "This is a long text about physics and Newton's laws."
        snippet = search._extract_snippet(text, {"Newton"})
        assert "Newton" in snippet


class TestNoteExport:
    def test_export_json(self) -> None:
        exporter = NoteExport()
        notes = [{"id": "1", "title": "Test"}]
        result = exporter.export_json(notes)
        assert result.format == "json"
        assert b"Test" in result.content

    def test_export_markdown(self) -> None:
        exporter = NoteExport()
        notes = [{"id": "1", "title": "Test", "summary": "Summary text"}]
        result = exporter.export_markdown(notes)
        assert result.format == "markdown"
        assert b"# StudyOS Notes Export" in result.content

    def test_export_csv(self) -> None:
        exporter = NoteExport()
        notes = [
            {
                "id": "1",
                "title": "Test",
                "summary": "Summary",
                "tags": [],
                "created_at": "2026-01-01",
            }
        ]
        result = exporter.export_csv(notes)
        assert result.format == "csv"
        assert b"id,title" in result.content

    def test_export_zip(self) -> None:
        exporter = NoteExport()
        notes = [{"id": "1", "title": "Test"}]
        result = exporter.export_zip(notes)
        assert result.format == "zip"
        assert len(result.content) > 0


class TestBulkImportService:
    def setup_method(self) -> None:
        self.service = BulkImportService()

    def test_create_job(self) -> None:
        job = self.service.create_job("job-1", total_files=5)
        assert job.id == "job-1"
        assert job.total_files == 5
        assert job.status == JobStatus.PENDING

    def test_update_progress(self) -> None:
        job = self.service.create_job("job-2", total_files=2)
        self.service.update_progress("job-2", success=True)
        self.service.update_progress("job-2", success=True)
        assert job.status == JobStatus.COMPLETED
        assert job.processed_files == 2

    def test_update_progress_with_failure(self) -> None:
        job = self.service.create_job("job-3", total_files=2)
        self.service.update_progress("job-3", success=True)
        self.service.update_progress("job-3", success=False)
        assert job.status == JobStatus.FAILED
        assert job.failed_files == 1

    def test_get_job(self) -> None:
        self.service.create_job("job-4", total_files=1)
        job = self.service.get_job("job-4")
        assert job is not None
        assert job.id == "job-4"

    def test_get_nonexistent_job(self) -> None:
        assert self.service.get_job("nonexistent") is None

    def test_cancel_job(self) -> None:
        self.service.create_job("job-5", total_files=1)
        assert self.service.cancel_job("job-5") is True
        job = self.service.get_job("job-5")
        assert job.status == JobStatus.CANCELLED

    def test_cancel_completed_job(self) -> None:
        job = self.service.create_job("job-6", total_files=1)
        self.service.update_progress("job-6", success=True)
        assert self.service.cancel_job("job-6") is False

    def test_list_jobs(self) -> None:
        self.service.create_job("job-7", total_files=1)
        self.service.create_job("job-8", total_files=2)
        assert len(self.service.list_jobs()) == 2

    def test_reset(self) -> None:
        self.service.create_job("job-9", total_files=1)
        self.service.reset()
        assert len(self.service.list_jobs()) == 0
