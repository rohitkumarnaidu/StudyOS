"use client";

import { useState, useEffect } from "react";
import type { PersonalNoteData } from "@/features/notes/api";
import { listPersonalNotes, createPersonalNote } from "@/features/notes/api";
import { Button } from "@/shared/components/ui/button";
import { Textarea } from "@/shared/components/ui/textarea";
import { StickyNote, Plus } from "lucide-react";
import { notifySuccess, notifyError } from "@/shared/lib";

interface PersonalNotesProps {
  noteId: string;
  pageNumber?: number;
}

export function PersonalNotes({ noteId, pageNumber }: PersonalNotesProps) {
  const [notes, setNotes] = useState<PersonalNoteData[]>([]);
  const [newNote, setNewNote] = useState("");

  useEffect(() => {
    void listPersonalNotes(noteId).then(setNotes);
  }, [noteId]);

  async function handleAdd() {
    if (!newNote.trim()) return;
    try {
      const created = await createPersonalNote(noteId, {
        page_number: pageNumber,
        content: newNote.trim(),
      });
      setNotes((prev) => [created, ...prev]);
      setNewNote("");
      notifySuccess("Note added");
    } catch {
      notifyError("Failed to add note");
    }
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold flex items-center gap-2">
        <StickyNote className="h-4 w-4" />
        Personal Notes
      </h3>

      <div className="flex gap-2">
        <Textarea
          placeholder="Add a personal note..."
          value={newNote}
          onChange={(e) => setNewNote(e.target.value)}
          className="min-h-[60px] text-sm"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
              e.preventDefault();
              void handleAdd();
            }
          }}
        />
        <Button size="sm" onClick={() => void handleAdd()}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>

      {notes.length > 0 && (
        <div className="space-y-2 max-h-48 overflow-auto">
          {notes.map((n) => (
            <div key={n.id} className="rounded-md border border-border p-3 bg-muted/20">
              <p className="text-sm whitespace-pre-wrap">{n.content}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {new Date(n.created_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
