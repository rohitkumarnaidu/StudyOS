"""Bulk import script — processes all PDFs from data/neet-notes/ directory."""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

# Add the API source to path so we can import services
SCRIPT_DIR = Path(__file__).resolve().parent
API_SRC = SCRIPT_DIR / "src"
if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))

from studyos_api.services.pdf_processor import PdfProcessor, ProcessingResult


# In-memory stores (mirrors notes.py API)
_notes_db: dict[str, dict[str, Any]] = {}
_bulk_results: dict[str, Any] = {}


def scan_pdfs(root_dir: str) -> dict[str, list[Path]]:
    """Scan directory for PDFs, grouped by category folder (recursive)."""
    root = Path(root_dir)
    if not root.exists():
        print(f"ERROR: Directory not found: {root_dir}")
        sys.exit(1)

    categories: dict[str, list[Path]] = {}
    for item in sorted(root.iterdir()):
        if item.is_dir():
            pdfs = sorted(item.rglob("*.pdf"))  # recursive
            if pdfs:
                categories[item.name] = pdfs

    # Also check for PDFs directly in root
    root_pdfs = sorted(root.glob("*.pdf"))
    if root_pdfs:
        categories["(root)"] = root_pdfs

    return categories


def process_pdf(
    processor: PdfProcessor,
    pdf_path: Path,
    category: str,
    profile_id: str = "demo-user",
) -> dict[str, Any]:
    """Process a single PDF and store in notes DB."""
    note_id = str(uuid.uuid4())

    try:
        with open(pdf_path, "rb") as f:
            content = f.read()

        result = processor.process(content, note_id, pdf_path.name)

        note = {
            "id": note_id,
            "title": pdf_path.name,
            "category": category,
            "note_type": result.pdf_type.value if result.pdf_type else "pdf",
            "status": result.status,
            "file_size": len(content),
            "page_count": result.page_count,
            "summary": result.structured_note.summary if result.structured_note else None,
            "tags": result.structured_note.chapter_tags if result.structured_note else [],
            "concepts_count": len(result.structured_note.concepts) if result.structured_note else 0,
            "mindmap_nodes": result.mindmap_tree.total_nodes if result.mindmap_tree else 0,
            "profile_id": profile_id,
            "file_path": str(pdf_path),
            "error": result.error,
        }
        _notes_db[note_id] = note
        return note

    except Exception as e:
        error_note = {
            "id": note_id,
            "title": pdf_path.name,
            "category": category,
            "status": "failed",
            "error": str(e),
            "profile_id": profile_id,
            "file_path": str(pdf_path),
        }
        _notes_db[note_id] = error_note
        return error_note


def run_bulk_import(root_dir: str, output_dir: str | None = None) -> dict[str, Any]:
    """Run bulk import on all PDFs in the directory."""
    print("=" * 60)
    print("STUDYOS — Bulk PDF Import")
    print("=" * 60)

    categories = scan_pdfs(root_dir)
    total_pdfs = sum(len(pdfs) for pdfs in categories.values())

    print(f"\nFound {total_pdfs} PDFs in {len(categories)} categories:")
    for cat, pdfs in categories.items():
        print(f"  {cat}: {len(pdfs)} PDFs")

    print(f"\nStarting processing...\n")

    processor = PdfProcessor()
    start_time = time.time()
    total_processed = 0
    total_success = 0
    total_failed = 0
    category_stats: dict[str, dict[str, int]] = {}

    for category, pdfs in categories.items():
        cat_success = 0
        cat_failed = 0
        print(f"\n{'-' * 40}")
        print(f"Category: {category} ({len(pdfs)} files)")
        print(f"{'-' * 40}")

        for i, pdf_path in enumerate(pdfs, 1):
            total_processed += 1
            note = process_pdf(processor, pdf_path, category)

            if note["status"] == "ready":
                total_success += 1
                cat_success += 1
                status_icon = "✓"
            else:
                total_failed += 1
                cat_failed += 1
                status_icon = "✗"

            # Progress indicator
            if i % 10 == 0 or i == len(pdfs):
                elapsed = time.time() - start_time
                rate = total_processed / elapsed if elapsed > 0 else 0
                print(f"  [{total_processed}/{total_pdfs}] {pdf_path.name[:50]}... {status_icon} ({rate:.1f} files/sec)")

        category_stats[category] = {"success": cat_success, "failed": cat_failed, "total": len(pdfs)}
        print(f"  → {category}: {cat_success} succeeded, {cat_failed} failed")

    elapsed = time.time() - start_time
    overall_rate = total_processed / elapsed if elapsed > 0 else 0

    # Summary
    print(f"\n{'=' * 60}")
    print("IMPORT SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total PDFs:    {total_processed}")
    print(f"Succeeded:     {total_success}")
    print(f"Failed:        {total_failed}")
    print(f"Success rate:  {total_success / max(total_processed, 1) * 100:.1f}%")
    print(f"Total time:    {elapsed:.1f}s")
    print(f"Avg rate:      {overall_rate:.1f} files/sec")

    print(f"\nCategory breakdown:")
    for cat, stats in category_stats.items():
        print(f"  {cat}: {stats['success']}/{stats['total']} succeeded")

    # Save results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save notes DB
        notes_file = output_path / "imported_notes.json"
        with open(notes_file, "w") as f:
            json.dump(_notes_db, f, indent=2, default=str)
        print(f"\nNotes saved to: {notes_file}")

        # Save summary
        summary = {
            "total_processed": total_processed,
            "total_success": total_success,
            "total_failed": total_failed,
            "elapsed_seconds": round(elapsed, 1),
            "avg_rate": round(overall_rate, 1),
            "category_stats": category_stats,
        }
        summary_file = output_path / "import_summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary saved to: {summary_file}")

    return {
        "total_processed": total_processed,
        "total_success": total_success,
        "total_failed": total_failed,
        "elapsed_seconds": round(elapsed, 1),
        "category_stats": category_stats,
        "notes_count": len(_notes_db),
    }


if __name__ == "__main__":
    # Default paths
    repo_root = Path(__file__).resolve().parent.parent.parent.parent  # apps/api/scripts -> repo root
    notes_dir = repo_root / "data" / "neet-notes"
    output_dir = repo_root / "data" / "import-results"

    # Allow override via CLI args
    if len(sys.argv) > 1:
        notes_dir = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_dir = Path(sys.argv[2])

    run_bulk_import(str(notes_dir), str(output_dir))
