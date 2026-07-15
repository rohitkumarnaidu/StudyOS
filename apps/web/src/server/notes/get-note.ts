"use server";

import { apiFetch } from "@/shared/api";
import type { NoteData } from "@/features/notes/api";

export async function getNote(noteId: string): Promise<NoteData | null> {
  try {
    const response = await apiFetch<NoteData>(`/v1/notes/${noteId}`);
    return response || null;
  } catch {
    return null;
  }
}

export async function listNotes(chapterId?: string): Promise<NoteData[]> {
  try {
    const params = chapterId ? `?chapter_id=${chapterId}` : "";
    const response = await apiFetch<NoteData[]>(`/v1/notes${params}`);
    return response || [];
  } catch {
    return [];
  }
}
