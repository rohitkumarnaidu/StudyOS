"use client";

import type { RecoveryPlan } from "@/features/roadmap/api";
import { cn } from "@/shared/lib";
import { AlertTriangle, BookOpen, Clock, SkipForward, Target } from "lucide-react";

interface RecoveryPlanViewerProps {
  plan: RecoveryPlan;
}

export function RecoveryPlanViewer({ plan }: RecoveryPlanViewerProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-500" />
          <h3 className="text-sm font-semibold">Recovery Plan</h3>
        </div>
        <span className="rounded-full bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-600">
          {plan.trigger_reason.replace("_", " ")}
        </span>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-md bg-muted/50 p-3">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            Days Left
          </div>
          <p className="mt-1 text-lg font-semibold">{plan.days_remaining}</p>
        </div>
        <div className="rounded-md bg-muted/50 p-3">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Target className="h-3 w-3" />
            Daily Hours
          </div>
          <p className="mt-1 text-lg font-semibold">{plan.daily_hours_target}h</p>
        </div>
        <div className="rounded-md bg-muted/50 p-3">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <BookOpen className="h-3 w-3" />
            Accelerate
          </div>
          <p className="mt-1 text-lg font-semibold">{plan.summary.total_accelerated}</p>
        </div>
        <div className="rounded-md bg-muted/50 p-3">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <SkipForward className="h-3 w-3" />
            Skip
          </div>
          <p className="mt-1 text-lg font-semibold">{plan.summary.total_skipped}</p>
        </div>
      </div>

      <div className="mb-4 rounded-md border border-amber-500/20 bg-amber-500/5 p-3">
        <p className="text-xs font-medium text-amber-700">
          Revised completion: {new Date(plan.revised_completion_date).toLocaleDateString()}
        </p>
        <p className="mt-1 text-xs text-amber-600">
          ~{plan.summary.days_per_chapter} days per chapter
        </p>
      </div>

      {plan.accelerated_chapters.length > 0 && (
        <div className="mb-4">
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Accelerated Chapters
          </h4>
          <div className="space-y-2">
            {plan.accelerated_chapters.map((ch) => (
              <div
                key={ch.chapter_id}
                className={cn(
                  "flex items-center justify-between rounded-md border p-2",
                  ch.priority === "high" ? "border-red-500/20 bg-red-500/5" : "border-amber-500/20 bg-amber-500/5",
                )}
              >
                <div>
                  <p className="text-sm font-medium">{ch.chapter_name}</p>
                  <p className="text-xs text-muted-foreground">{ch.subject_name}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-medium">
                    Weight: {ch.weightage}%
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {Math.round(ch.current_completion * 100)}% done
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {plan.skipped_chapters.length > 0 && (
        <div>
          <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Recommended to Skip
          </h4>
          <div className="space-y-1">
            {plan.skipped_chapters.map((ch) => (
              <div key={ch.chapter_id} className="flex items-center justify-between rounded-md border border-border/50 p-2 opacity-75">
                <div>
                  <p className="text-sm">{ch.chapter_name}</p>
                  <p className="text-xs text-muted-foreground">{ch.subject_name}</p>
                </div>
                <p className="text-xs text-muted-foreground">Weight: {ch.weightage}%</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
