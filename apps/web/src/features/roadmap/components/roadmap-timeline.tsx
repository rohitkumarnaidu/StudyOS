"use client";

import type { RoadmapItem } from "@/features/analytics/api";
import { updateRoadmapItem } from "@/features/analytics/api";
import { cn } from "@/shared/lib";
import { Calendar, CheckCircle2, Clock, SkipForward, AlertCircle } from "lucide-react";
import { notifySuccess, notifyError } from "@/shared/lib";

interface RoadmapTimelineProps {
  items: RoadmapItem[];
  onStatusChange?: () => void;
}

const statusIcons = {
  pending: Clock,
  in_progress: AlertCircle,
  completed: CheckCircle2,
  skipped: SkipForward,
};

const priorityColors = {
  1: "border-l-emerald-500",
  2: "border-l-amber-500",
  3: "border-l-destructive",
};

export function RoadmapTimeline({ items, onStatusChange }: RoadmapTimelineProps) {
  if (items.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="mb-4 text-sm font-semibold">Study Roadmap</h3>
        <p className="text-sm text-muted-foreground text-center py-8">
          No roadmap generated yet.
        </p>
      </div>
    );
  }

  async function handleStatusChange(item: RoadmapItem, newStatus: RoadmapItem["status"]) {
    try {
      await updateRoadmapItem(item.id, newStatus);
      notifySuccess(`Marked as ${newStatus.replace("_", " ")}`);
      onStatusChange?.();
    } catch {
      notifyError("Failed to update roadmap item");
    }
  }

  const sorted = [...items].sort((a, b) => new Date(a.target_date).getTime() - new Date(b.target_date).getTime());

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold">Study Roadmap</h3>
      <div className="space-y-3">
        {sorted.map((item) => {
          const Icon = statusIcons[item.status];
          return (
            <div
              key={item.id}
              className={cn(
                "rounded-md border border-border border-l-4 p-3 transition-colors",
                priorityColors[item.priority],
                item.status === "completed" && "opacity-60",
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2 flex-1">
                  <Icon className={cn("mt-0.5 h-4 w-4 flex-shrink-0", item.status === "completed" ? "text-emerald-500" : "text-muted-foreground")} />
                  <div>
                    <p className={cn("text-sm font-medium", item.status === "completed" && "line-through")}>
                      {item.title}
                    </p>
                    {item.description && (
                      <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(item.target_date).toLocaleDateString()}
                      </span>
                      {item.chapter_name && <span>{item.chapter_name}</span>}
                    </div>
                  </div>
                </div>

                {item.status !== "completed" && (
                  <button
                    className="flex-shrink-0 rounded-md border border-border px-2 py-1 text-xs hover:bg-muted transition-colors"
                    onClick={() => void handleStatusChange(item, "completed")}
                  >
                    Done
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
