"use client";

import { cn } from "@/shared/lib";
import type { WeakArea } from "@/features/analytics/api";
import { AlertTriangle, TrendingDown, CheckCircle } from "lucide-react";
import Link from "next/link";

interface WeakAreasProps {
  data: WeakArea[];
}

const priorityConfig = {
  high: { icon: AlertTriangle, color: "text-destructive", bg: "bg-destructive/10" },
  medium: { icon: TrendingDown, color: "text-amber-500", bg: "bg-amber-500/10" },
  low: { icon: CheckCircle, color: "text-emerald-500", bg: "bg-emerald-500/10" },
};

export function WeakAreas({ data }: WeakAreasProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="mb-4 text-sm font-semibold">Areas to Improve</h3>
        <p className="text-sm text-muted-foreground text-center py-8">
          No weak areas detected. Keep studying!
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold">Areas to Improve</h3>
      <div className="space-y-3">
        {data.slice(0, 8).map((area) => {
          const config = priorityConfig[area.priority];
          const Icon = config.icon;
          return (
            <Link
              key={area.chapter_id}
              href={`/syllabus/${area.chapter_id}`}
              className="flex items-center gap-3 rounded-md border border-border p-3 hover:bg-muted/50 transition-colors"
            >
              <div className={cn("flex h-8 w-8 items-center justify-center rounded-full", config.bg)}>
                <Icon className={cn("h-4 w-4", config.color)} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{area.chapter_name}</p>
                <p className="text-xs text-muted-foreground">{area.subject_name}</p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-sm font-medium">{area.progress_pct}%</p>
                {area.quiz_avg !== null && (
                  <p className="text-xs text-muted-foreground">Quiz: {area.quiz_avg}%</p>
                )}
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
