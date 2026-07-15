"use client";

import { FileText, CheckCircle2, XCircle, Loader2, X } from "lucide-react";
import { cn } from "@/shared/lib";

export interface UploadQueueItem {
  id: string;
  filename: string;
  progress: number;
  status: "pending" | "uploading" | "done" | "error";
}

interface UploadQueueProps {
  items: UploadQueueItem[];
  onRemove?: (id: string) => void;
  compact?: boolean;
  className?: string;
}

export function UploadQueue({ items, onRemove, compact = false, className }: UploadQueueProps) {
  const completedCount = items.filter((i) => i.status === "done").length;
  const totalCount = items.length;
  const hasCompleted = completedCount > 0;

  function handleClearCompleted() {
    items.filter((i) => i.status === "done" || i.status === "error").forEach((i) => onRemove?.(i.id));
  }

  if (items.length === 0) return null;

  return (
    <div className={cn("space-y-3", compact ? "text-xs" : "text-sm", className)}>
      {totalCount > 1 && (
        <div className={cn("flex items-center justify-between", compact ? "text-xs" : "text-sm")}>
          <span className="text-muted-foreground">
            {completedCount} of {totalCount} completed
          </span>
          {hasCompleted && (
            <button
              onClick={handleClearCompleted}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Clear completed
            </button>
          )}
        </div>
      )}

      <div className={cn("space-y-2", compact && "max-h-40 overflow-auto")}>
        {items.map((item) => (
          <UploadQueueRow key={item.id} item={item} onRemove={onRemove} compact={compact} />
        ))}
      </div>
    </div>
  );
}

function UploadQueueRow({
  item,
  onRemove,
  compact = false,
}: {
  item: UploadQueueItem;
  onRemove?: (id: string) => void;
  compact?: boolean;
}) {
  const canRemove = item.status === "done" || item.status === "error";

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-md border border-border px-3 transition-colors",
        compact ? "py-1.5" : "py-2",
        item.status === "error" && "border-destructive/50 bg-destructive/5",
      )}
    >
      <StatusIcon status={item.status} compact={compact} />

      <div className="flex-1 min-w-0">
        <p className={cn("truncate font-medium", compact && "text-xs")}>{item.filename}</p>
        <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-muted">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-300",
              item.status === "done"
                ? "bg-emerald-500"
                : item.status === "error"
                  ? "bg-destructive"
                  : item.status === "pending"
                    ? "bg-muted-foreground/40"
                    : "bg-primary",
            )}
            style={{ width: `${item.progress}%` }}
          />
        </div>
      </div>

      {canRemove && onRemove && (
        <button
          onClick={() => onRemove(item.id)}
          className="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
          aria-label={`Remove ${item.filename}`}
        >
          <X className={cn("h-4 w-4", compact && "h-3 w-3")} />
        </button>
      )}
    </div>
  );
}

function StatusIcon({ status, compact }: { status: UploadQueueItem["status"]; compact: boolean }) {
  const size = cn("flex-shrink-0", compact ? "h-3 w-3" : "h-4 w-4");

  switch (status) {
    case "done":
      return <CheckCircle2 className={cn(size, "text-emerald-500")} />;
    case "error":
      return <XCircle className={cn(size, "text-destructive")} />;
    case "uploading":
      return <Loader2 className={cn(size, "text-primary animate-spin")} />;
    case "pending":
    default:
      return <FileText className={cn(size, "text-muted-foreground")} />;
  }
}
