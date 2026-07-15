"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Input } from "@/shared/components/ui/input";
import { searchNotes, type SearchResult } from "@/features/notes/api";
import { Search, FileText, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

interface GlobalSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GlobalSearch({ open, onOpenChange }: GlobalSearchProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      return;
    }
    setLoading(true);
    try {
      const data = await searchNotes(q);
      setResults(data.slice(0, 10));
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        onOpenChange(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onOpenChange]);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (open && query) void doSearch(query);
    }, 300);
    return () => clearTimeout(timer);
  }, [query, open, doSearch]);

  function selectResult(result: SearchResult) {
    onOpenChange(false);
    router.push(`/notes/${result.note_id}`);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Search className="h-4 w-4" />
            Search notes
          </DialogTitle>
        </DialogHeader>

        <Input
          placeholder="Type to search across all notes... (Ctrl+K)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
          className="mt-2"
        />

        <div className="mt-4 max-h-72 overflow-auto space-y-2">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          )}

          {!loading && results.length === 0 && query.length >= 2 && (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No results found
            </p>
          )}

          {results.map((result) => (
            <button
              key={result.note_id + result.score}
              className="flex w-full items-start gap-3 rounded-md p-3 text-left hover:bg-muted/50 transition-colors"
              onClick={() => selectResult(result)}
            >
              <FileText className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{result.note_title}</p>
                <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                  {result.chunk_content}
                </p>
              </div>
            </button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
