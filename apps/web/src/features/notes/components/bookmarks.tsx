"use client";

import { useState, useEffect } from "react";
import type { BookmarkData } from "@/features/notes/api";
import { listBookmarks, createBookmark, deleteBookmark } from "@/features/notes/api";
import { Button } from "@/shared/components/ui/button";
import { Bookmark as BookmarkIcon, Trash2, Plus } from "lucide-react";
import { notifySuccess, notifyError } from "@/shared/lib";

interface BookmarksProps {
  noteId: string;
  currentPage: number;
}

export function Bookmarks({ noteId, currentPage }: BookmarksProps) {
  const [bookmarks, setBookmarks] = useState<BookmarkData[]>([]);

  useEffect(() => {
    void listBookmarks(noteId).then(setBookmarks);
  }, [noteId]);

  async function handleAdd() {
    try {
      const created = await createBookmark(noteId, {
        page_number: currentPage,
        label: `Page ${currentPage}`,
      });
      setBookmarks((prev) => [...prev, created]);
      notifySuccess("Bookmark added");
    } catch {
      notifyError("Failed to add bookmark");
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteBookmark(id);
      setBookmarks((prev) => prev.filter((b) => b.id !== id));
      notifySuccess("Bookmark removed");
    } catch {
      notifyError("Failed to delete bookmark");
    }
  }

  const isBookmarked = bookmarks.some((b) => b.page_number === currentPage);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <BookmarkIcon className="h-4 w-4" />
          Bookmarks ({bookmarks.length})
        </h3>
        <Button
          size="sm"
          variant={isBookmarked ? "default" : "outline"}
          onClick={handleAdd}
          disabled={isBookmarked}
        >
          <Plus className="mr-1 h-3 w-3" />
          Add
        </Button>
      </div>

      {bookmarks.length === 0 ? (
        <p className="text-xs text-muted-foreground">No bookmarks yet</p>
      ) : (
        <div className="space-y-1 max-h-48 overflow-auto">
          {bookmarks.map((b) => (
            <div
              key={b.id}
              className="flex items-center justify-between rounded-md bg-muted/30 px-3 py-2"
            >
              <span className="text-sm">{b.label ?? `Page ${b.page_number}`}</span>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => handleDelete(b.id)}
                aria-label="Delete bookmark"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
