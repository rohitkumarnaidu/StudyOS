"use client";

import { NotesLibrary } from "@/features/notes/components/notes-library";

export default function NotesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Notes</h1>
        <p className="text-sm text-muted-foreground">
          Upload, organize, and study from your PDF notes and mind maps.
        </p>
      </div>

      <NotesLibrary />
    </div>
  );
}
