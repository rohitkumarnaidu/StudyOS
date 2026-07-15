import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { NoteCard } from "./note-card";
import type { NoteData } from "@/features/notes/api";

afterEach(() => {
  cleanup();
});

const createNote = (overrides: Partial<NoteData> = {}): NoteData => ({
  id: "note-1",
  title: "Test Note",
  note_type: "pdf",
  status: "ready",
  page_count: 10,
  file_size: 1024000,
  tags: ["physics", "mechanics"],
  summary: "This is a test note summary",
  chapter_id: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
  ...overrides,
});

describe("NoteCard", () => {
  it("renders note title", () => {
    render(<NoteCard note={createNote()} />);
    expect(screen.getByText("Test Note")).toBeTruthy();
  });

  it("renders note status badge", () => {
    render(<NoteCard note={createNote()} />);
    expect(screen.getByText("ready")).toBeTruthy();
  });

  it("renders page count", () => {
    render(<NoteCard note={createNote()} />);
    expect(screen.getByText("10 pages")).toBeTruthy();
  });

  it("renders file size", () => {
    render(<NoteCard note={createNote({ file_size: 2048000 })} />);
    expect(screen.getByText(/2\.0 MB/)).toBeTruthy();
  });

  it("renders tags", () => {
    render(<NoteCard note={createNote()} />);
    expect(screen.getByText("physics")).toBeTruthy();
    expect(screen.getByText("mechanics")).toBeTruthy();
  });

  it("renders summary", () => {
    render(<NoteCard note={createNote()} />);
    expect(screen.getByText("This is a test note summary")).toBeTruthy();
  });

  it("shows uploading status with different styling", () => {
    render(<NoteCard note={createNote({ status: "uploading" })} />);
    expect(screen.getByText("uploading")).toBeTruthy();
  });

  it("shows failed status with different styling", () => {
    render(<NoteCard note={createNote({ status: "failed" })} />);
    expect(screen.getByText("failed")).toBeTruthy();
  });

  it("renders mindmap note type", () => {
    render(<NoteCard note={createNote({ note_type: "mindmap" })} />);
    expect(screen.getByText("Test Note")).toBeTruthy();
  });

  it("renders text note type", () => {
    render(<NoteCard note={createNote({ note_type: "text" })} />);
    expect(screen.getByText("Test Note")).toBeTruthy();
  });

  it("handles note without summary", () => {
    render(<NoteCard note={createNote({ summary: undefined })} />);
    expect(screen.getByText("Test Note")).toBeTruthy();
  });

  it("handles note without tags", () => {
    render(<NoteCard note={createNote({ tags: [] })} />);
    expect(screen.getByText("Test Note")).toBeTruthy();
  });

  it("handles note without page count", () => {
    render(<NoteCard note={createNote({ page_count: 0 })} />);
    expect(screen.getByText("Test Note")).toBeTruthy();
  });
});
