import { apiFetch } from "@/shared/api";

export interface NoteData {
  id: string;
  title: string;
  note_type: "pdf" | "mindmap" | "text";
  status: "uploading" | "processing" | "ready" | "failed";
  file_size: number | null;
  page_count: number;
  summary: string | null;
  tags: string[];
  chapter_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface HighlightData {
  id: string;
  note_id: string;
  page_number: number | null;
  color: string;
  text_content: string;
  created_at: string;
}

export interface BookmarkData {
  id: string;
  note_id: string;
  page_number: number;
  label: string | null;
  created_at: string;
}

export interface PersonalNoteData {
  id: string;
  note_id: string;
  page_number: number | null;
  content: string;
  created_at: string;
}

export interface BulkImportJob {
  id: string;
  status: "pending" | "processing" | "completed" | "failed" | "cancelled";
  total_files: number;
  processed_files: number;
  failed_files: number;
  created_at: string;
}

export interface SearchResult {
  note_id: string;
  note_title: string;
  chunk_content: string;
  score: number;
  page_number: number | null;
}

export async function listNotes(chapterId?: string): Promise<NoteData[]> {
  const params = chapterId ? `?chapter_id=${chapterId}` : "";
  return apiFetch<NoteData[]>(`/v1/notes${params}`);
}

export async function getNote(noteId: string): Promise<NoteData> {
  return apiFetch<NoteData>(`/v1/notes/${noteId}`);
}

export async function deleteNote(noteId: string): Promise<void> {
  await apiFetch(`/v1/notes/${noteId}`, { method: "DELETE" });
}

export async function listHighlights(noteId: string): Promise<HighlightData[]> {
  return apiFetch<HighlightData[]>(`/v1/notes/${noteId}/highlights`);
}

export async function createHighlight(
  noteId: string,
  data: { page_number?: number; color: string; text_content: string },
): Promise<HighlightData> {
  return apiFetch<HighlightData>(`/v1/notes/${noteId}/highlights`, {
    method: "POST",
    body: data,
  });
}

export async function deleteHighlight(highlightId: string): Promise<void> {
  await apiFetch(`/v1/notes/highlights/${highlightId}`, { method: "DELETE" });
}

export async function listBookmarks(noteId: string): Promise<BookmarkData[]> {
  return apiFetch<BookmarkData[]>(`/v1/notes/${noteId}/bookmarks`);
}

export async function createBookmark(
  noteId: string,
  data: { page_number: number; label?: string },
): Promise<BookmarkData> {
  return apiFetch<BookmarkData>(`/v1/notes/${noteId}/bookmarks`, {
    method: "POST",
    body: data,
  });
}

export async function deleteBookmark(bookmarkId: string): Promise<void> {
  await apiFetch(`/v1/notes/bookmarks/${bookmarkId}`, { method: "DELETE" });
}

export async function listPersonalNotes(noteId: string): Promise<PersonalNoteData[]> {
  return apiFetch<PersonalNoteData[]>(`/v1/notes/${noteId}/personal-notes`);
}

export async function createPersonalNote(
  noteId: string,
  data: { page_number?: number; content: string },
): Promise<PersonalNoteData> {
  return apiFetch<PersonalNoteData>(`/v1/notes/${noteId}/personal-notes`, {
    method: "POST",
    body: data,
  });
}

export async function searchNotes(query: string, chapterId?: string): Promise<SearchResult[]> {
  const params = new URLSearchParams({ q: query });
  if (chapterId) params.set("chapter_id", chapterId);
  return apiFetch<SearchResult[]>(`/v1/notes/search?${params.toString()}`);
}

export async function createBulkImportJob(
  chapterId?: string,
): Promise<BulkImportJob> {
  return apiFetch<BulkImportJob>("/v1/notes/bulk-import", {
    method: "POST",
    body: chapterId ? { chapter_id: chapterId } : {},
  });
}

export async function getBulkImportJob(jobId: string): Promise<BulkImportJob> {
  return apiFetch<BulkImportJob>(`/v1/notes/bulk-import/${jobId}`);
}
