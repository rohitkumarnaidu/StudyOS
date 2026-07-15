"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import {
  ZoomIn,
  ZoomOut,
  ChevronLeft,
  ChevronRight,
  Search,
  RotateCw,
} from "lucide-react";

interface PDFViewerProps {
  url: string;
  title: string;
  pageCount: number;
}

export function PDFViewer({ url, title, pageCount }: PDFViewerProps) {
  const [page, setPage] = useState(1);
  const [zoom, setZoom] = useState(100);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft" && page > 1) setPage((p) => p - 1);
      if (e.key === "ArrowRight" && page < pageCount) setPage((p) => p + 1);
      if ((e.ctrlKey || e.metaKey) && e.key === "f") {
        e.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [page, pageCount]);

  return (
    <div className="flex h-full flex-col bg-muted/30">
      <div className="flex items-center justify-between border-b border-border bg-background px-4 py-2">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            aria-label="Previous page"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>

          <span className="text-sm tabular-nums">
            {page} / {pageCount}
          </span>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setPage((p) => Math.min(pageCount, p + 1))}
            disabled={page >= pageCount}
            aria-label="Next page"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          {searchOpen ? (
            <Input
              placeholder="Search in PDF..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-7 w-48"
              autoFocus
              onBlur={() => setSearchOpen(false)}
            />
          ) : (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSearchOpen(true)}
              aria-label="Search"
            >
              <Search className="h-4 w-4" />
            </Button>
          )}

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setZoom((z) => Math.max(50, z - 25))}
            aria-label="Zoom out"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>

          <span className="text-xs tabular-nums w-10 text-center">{zoom}%</span>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setZoom((z) => Math.min(200, z + 25))}
            aria-label="Zoom in"
          >
            <ZoomIn className="h-4 w-4" />
          </Button>

          <Button variant="ghost" size="icon" aria-label="Rotate">
            <RotateCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div
        ref={containerRef}
        className="flex-1 overflow-auto p-4 flex items-start justify-center"
      >
        <div
          className="bg-white shadow-lg"
          style={{
            width: `${8.5 * zoom}px`,
            height: `${11 * zoom}px`,
            maxWidth: "100%",
          }}
        >
          <iframe
            src={`${url}#page=${page}`}
            className="h-full w-full border-0"
            title={title}
          />
        </div>
      </div>
    </div>
  );
}
