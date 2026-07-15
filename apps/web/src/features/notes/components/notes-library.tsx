"use client";

import { useState, useEffect, startTransition, useCallback } from "react";
import type { NoteData } from "@/features/notes/api";
import { NoteCard } from "@/features/notes/components/note-card";
import { UploadDialog } from "@/features/notes/components/upload-dialog";
import { listNotes } from "@/features/notes/api";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import { Search, Grid, List, Filter } from "lucide-react";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { notifyError } from "@/shared/lib";

interface NotesLibraryProps {
  chapterId?: string;
}

export function NotesLibrary({ chapterId }: NotesLibraryProps) {
  const [notes, setNotes] = useState<NoteData[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");

  const loadNotes = useCallback(() => {
    let cancelled = false;
    startTransition(() => setLoading(true));
    listNotes(chapterId)
      .then((data) => {
        if (!cancelled) startTransition(() => setNotes(data));
      })
      .catch(() => {
        if (!cancelled) notifyError("Failed to load notes");
      })
      .finally(() => {
        if (!cancelled) startTransition(() => setLoading(false));
      });
    return () => {
      cancelled = true;
    };
  }, [chapterId]);

  useEffect(() => {
    const cleanup = loadNotes();
    return cleanup;
  }, [loadNotes]);

  const filtered = notes.filter((n) =>
    n.title.toLowerCase().includes(search.toLowerCase()) ||
    n.tags.some((t) => t.toLowerCase().includes(search.toLowerCase())),
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search notes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <Button variant="outline" size="icon" aria-label="Filter">
          <Filter className="h-4 w-4" />
        </Button>

        <div className="flex rounded-md border border-border">
          <button
            className={`px-2 py-1.5 text-sm ${view === "grid" ? "bg-muted" : ""}`}
            onClick={() => setView("grid")}
            aria-label="Grid view"
          >
            <Grid className="h-4 w-4" />
          </button>
          <button
            className={`px-2 py-1.5 text-sm ${view === "list" ? "bg-muted" : ""}`}
            onClick={() => setView("list")}
            aria-label="List view"
          >
            <List className="h-4 w-4" />
          </button>
        </div>

        <UploadDialog onUploadComplete={loadNotes} />
      </div>

      {loading ? (
        <div className={view === "grid" ? "grid gap-4 sm:grid-cols-2 lg:grid-cols-3" : "space-y-2"}>
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-32 rounded-lg" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border bg-card/50 px-4 py-12 text-center">
          <p className="text-sm text-muted-foreground">
            {search ? "No notes match your search" : "No notes yet. Upload your first PDF!"}
          </p>
        </div>
      ) : (
        <div
          className={
            view === "grid"
              ? "grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
              : "space-y-2"
          }
        >
          {filtered.map((note) => (
            <NoteCard key={note.id} note={note} />
          ))}
        </div>
      )}
    </div>
  );
}
