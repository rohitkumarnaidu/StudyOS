"""Note export — export notes in various formats."""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ExportResult:
    """Result of an export operation."""

    format: str
    file_name: str
    content: bytes
    mime_type: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": self.format,
            "file_name": self.file_name,
            "size_bytes": len(self.content),
            "mime_type": self.mime_type,
        }


class NoteExport:
    """Export notes in various formats."""

    def __init__(self) -> None:
        pass

    def export_json(self, notes: list[dict[str, Any]]) -> ExportResult:
        """Export notes as JSON."""
        content = json.dumps(notes, indent=2, ensure_ascii=False).encode("utf-8")
        return ExportResult(
            format="json",
            file_name="studyos-notes.json",
            content=content,
            mime_type="application/json",
        )

    def export_markdown(self, notes: list[dict[str, Any]]) -> ExportResult:
        """Export notes as Markdown."""
        lines = ["# StudyOS Notes Export\n"]
        for note in notes:
            lines.append(f"\n## {note.get('title', 'Untitled')}\n")
            if note.get("summary"):
                lines.append(f"\n{note['summary']}\n")
            if note.get("concepts"):
                lines.append("\n### Key Concepts\n")
                for concept in note["concepts"]:
                    lines.append(f"- **{concept.get('title', '')}**: {concept.get('definition', '')}")
            lines.append("\n---\n")

        content = "\n".join(lines).encode("utf-8")
        return ExportResult(
            format="markdown",
            file_name="studyos-notes.md",
            content=content,
            mime_type="text/markdown",
        )

    def export_zip(self, notes: list[dict[str, Any]]) -> ExportResult:
        """Export notes as ZIP with individual files."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for note in notes:
                title = note.get("title", "untitled").replace("/", "_")
                zf.writestr(f"{title}.json", json.dumps(note, indent=2, ensure_ascii=False))

            summary = json.dumps({"total_notes": len(notes), "notes": [n.get("title") for n in notes]}, indent=2)
            zf.writestr("manifest.json", summary)

        buffer.seek(0)
        return ExportResult(
            format="zip",
            file_name="studyos-notes.zip",
            content=buffer.getvalue(),
            mime_type="application/zip",
        )

    def export_csv(self, notes: list[dict[str, Any]]) -> ExportResult:
        """Export notes as CSV."""
        import csv
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "title", "summary", "tags", "created_at"])

        for note in notes:
            writer.writerow([
                note.get("id", ""),
                note.get("title", ""),
                (note.get("summary", "") or "")[:500],
                ", ".join(note.get("tags", [])),
                note.get("created_at", ""),
            ])

        content = buffer.getvalue().encode("utf-8")
        return ExportResult(
            format="csv",
            file_name="studyos-notes.csv",
            content=content,
            mime_type="text/csv",
        )
