"use client";

import { useState, useEffect } from "react";
import type { HighlightData } from "@/features/notes/api";
import { listHighlights, deleteHighlight } from "@/features/notes/api";
import { Button } from "@/shared/components/ui/button";
import { Trash2, Highlighter } from "lucide-react";
import { notifySuccess, notifyError } from "@/shared/lib";

interface HighlightsManagerProps {
  noteId: string;
}

const colorMap: Record<string, string> = {
  yellow: "bg-yellow-200 dark:bg-yellow-500/30",
  green: "bg-green-200 dark:bg-green-500/30",
  blue: "bg-blue-200 dark:bg-blue-500/30",
  pink: "bg-pink-200 dark:bg-pink-500/30",
};

export function HighlightsManager({ noteId }: HighlightsManagerProps) {
  const [highlights, setHighlights] = useState<HighlightData[]>([]);

  useEffect(() => {
    void listHighlights(noteId).then(setHighlights);
  }, [noteId]);

  async function handleDelete(id: string) {
    try {
      await deleteHighlight(id);
      setHighlights((prev) => prev.filter((h) => h.id !== id));
      notifySuccess("Highlight removed");
    } catch {
      notifyError("Failed to delete highlight");
    }
  }

  if (highlights.length === 0) {
    return (
      <div className="rounded-lg border border-border p-4 text-center">
        <Highlighter className="mx-auto mb-2 h-6 w-6 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">No highlights yet</p>
        <p className="text-xs text-muted-foreground">Select text in the PDF to highlight</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold flex items-center gap-2">
        <Highlighter className="h-4 w-4" />
        Highlights ({highlights.length})
      </h3>
      <div className="space-y-2 max-h-64 overflow-auto">
        {highlights.map((h) => (
          <div
            key={h.id}
            className={`rounded-md p-3 ${colorMap[h.color] ?? colorMap.yellow}`}
          >
            <div className="flex items-start justify-between gap-2">
              <p className="text-sm">{h.text_content}</p>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 flex-shrink-0"
                onClick={() => handleDelete(h.id)}
                aria-label="Delete highlight"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
            {h.page_number && (
              <p className="mt-1 text-xs text-muted-foreground">
                Page {h.page_number}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
