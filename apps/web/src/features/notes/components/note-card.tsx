"use client";

import type { NoteData } from "@/features/notes/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { FileText, Brain, FileType, Loader2, AlertCircle } from "lucide-react";
import Link from "next/link";
import { cn } from "@/shared/lib";

interface NoteCardProps {
  note: NoteData;
}

const typeIcons = {
  pdf: FileText,
  mindmap: Brain,
  text: FileType,
};

const statusColors = {
  uploading: "bg-blue-500/10 text-blue-600",
  processing: "bg-amber-500/10 text-amber-600",
  ready: "bg-emerald-500/10 text-emerald-600",
  failed: "bg-destructive/10 text-destructive",
};

const statusIcons = {
  uploading: Loader2,
  processing: Loader2,
  ready: null,
  failed: AlertCircle,
};

export function NoteCard({ note }: NoteCardProps) {
  const TypeIcon = typeIcons[note.note_type];
  const StatusIcon = statusIcons[note.status];
  const isReady = note.status === "ready";

  return (
    <Card className={cn("transition-colors hover:border-border/80", !isReady && "opacity-70")}>
      <Link href={isReady ? `/notes/${note.id}` : "#"}>
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2">
              <TypeIcon className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-sm truncate">{note.title}</CardTitle>
            </div>
            <Badge variant="secondary" className={cn("text-xs", statusColors[note.status])}>
              {StatusIcon && <StatusIcon className={cn("mr-1 h-3 w-3", note.status === "processing" && "animate-spin")} />}
              {note.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            {note.page_count > 0 && <span>{note.page_count} pages</span>}
            {note.file_size && <span>{formatFileSize(note.file_size)}</span>}
            {note.tags.length > 0 && (
              <div className="flex gap-1">
                {note.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="rounded bg-muted px-1.5 py-0.5">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
          {note.summary && (
            <p className="mt-2 line-clamp-2 text-xs text-muted-foreground">
              {note.summary}
            </p>
          )}
        </CardContent>
      </Link>
    </Card>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
