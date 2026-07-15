"""Tests for note_export service."""

from studyos_api.services.note_export import NoteExport, ExportResult


class TestExportResult:
    def test_to_dict(self):
        result = ExportResult(
            format="json",
            file_name="test.json",
            content=b'{"test": true}',
            mime_type="application/json",
        )
        d = result.to_dict()
        assert d["format"] == "json"
        assert d["file_name"] == "test.json"
        assert d["size_bytes"] == len(b'{"test": true}')
        assert d["mime_type"] == "application/json"


class TestNoteExport:
    def test_export_json(self):
        exporter = NoteExport()
        notes = [
            {"id": "1", "title": "Test Note", "summary": "Hello world"},
            {"id": "2", "title": "Another Note", "summary": "Foo bar"},
        ]
        result = exporter.export_json(notes)
        assert result.format == "json"
        assert result.file_name == "studyos-notes.json"
        assert result.mime_type == "application/json"
        assert b"Test Note" in result.content

    def test_export_json_empty(self):
        exporter = NoteExport()
        result = exporter.export_json([])
        assert result.content == b"[]"

    def test_export_markdown(self):
        exporter = NoteExport()
        notes = [
            {"id": "1", "title": "Test Note", "summary": "Hello world"},
        ]
        result = exporter.export_markdown(notes)
        assert result.format == "markdown"
        assert result.file_name == "studyos-notes.md"
        assert b"# StudyOS Notes Export" in result.content
        assert b"Test Note" in result.content

    def test_export_markdown_empty(self):
        exporter = NoteExport()
        result = exporter.export_markdown([])
        assert result.format == "markdown"
        assert b"# StudyOS Notes Export" in result.content

    def test_export_markdown_with_concepts(self):
        exporter = NoteExport()
        notes = [
            {
                "id": "1",
                "title": "Physics Note",
                "summary": "Newton's laws",
                "concepts": [
                    {"title": "Inertia", "definition": "Resistance to change in motion"},
                ],
            },
        ]
        result = exporter.export_markdown(notes)
        assert b"Key Concepts" in result.content
        assert b"Inertia" in result.content

    def test_export_csv(self):
        exporter = NoteExport()
        notes = [
            {"id": "1", "title": "Test Note", "summary": "Hello", "tags": ["physics"], "created_at": "2024-01-01"},
        ]
        result = exporter.export_csv(notes)
        assert result.format == "csv"
        assert result.file_name == "studyos-notes.csv"
        assert b"id,title,summary,tags,created_at" in result.content

    def test_export_csv_empty(self):
        exporter = NoteExport()
        result = exporter.export_csv([])
        assert result.format == "csv"
        assert b"id,title,summary,tags,created_at" in result.content

    def test_export_csv_missing_fields(self):
        exporter = NoteExport()
        notes = [{"id": "1"}]
        result = exporter.export_csv(notes)
        assert result.format == "csv"

    def test_export_zip(self):
        exporter = NoteExport()
        notes = [
            {"id": "1", "title": "Note One", "summary": "First note"},
            {"id": "2", "title": "Note Two", "summary": "Second note"},
        ]
        result = exporter.export_zip(notes)
        assert result.format == "zip"
        assert result.file_name == "studyos-notes.zip"
        assert result.mime_type == "application/zip"
        assert len(result.content) > 0

    def test_export_zip_empty(self):
        exporter = NoteExport()
        result = exporter.export_zip([])
        assert result.format == "zip"
        assert len(result.content) > 0

    def test_export_zip_special_chars_in_title(self):
        exporter = NoteExport()
        notes = [{"id": "1", "title": "Note/With/Slashes", "summary": "test"}]
        result = exporter.export_zip(notes)
        assert result.format == "zip"
