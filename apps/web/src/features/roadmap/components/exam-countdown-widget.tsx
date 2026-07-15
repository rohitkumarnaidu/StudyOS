"use client";

import { cn } from "@/shared/lib";
import { Calendar, Clock, Target, TrendingDown, TrendingUp } from "lucide-react";

interface ExamCountdownWidgetProps {
  examDate: string;
  predictedScore?: number;
  targetScore?: number;
  phase?: string;
  dailyHours?: number;
}

const phaseColors: Record<string, string> = {
  crash: "bg-red-500/10 text-red-600 border-red-500/20",
  intensive: "bg-amber-500/10 text-amber-600 border-amber-500/20",
  focused: "bg-blue-500/10 text-blue-600 border-blue-500/20",
  foundational: "bg-emerald-500/10 text-emerald-600 border-emerald-500/20",
};

const urgencyColors = (days: number) => {
  if (days <= 30) return "text-red-600";
  if (days <= 60) return "text-amber-600";
  if (days <= 90) return "text-blue-600";
  return "text-emerald-600";
};

export function ExamCountdownWidget({
  examDate,
  predictedScore,
  targetScore,
  phase = "foundational",
  dailyHours,
}: ExamCountdownWidgetProps) {
  const today = new Date();
  const exam = new Date(examDate);
  const daysRemaining = Math.max(0, Math.ceil((exam.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)));

  const weeks = Math.floor(daysRemaining / 7);
  const days = daysRemaining % 7;

  const scoreDiff = predictedScore && targetScore ? targetScore - predictedScore : null;

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-muted-foreground" />
          <h3 className="text-sm font-semibold">Exam Countdown</h3>
        </div>
        <span className={cn("rounded-full border px-2 py-0.5 text-xs font-medium", phaseColors[phase] || phaseColors.foundational)}>
          {phase} phase
        </span>
      </div>

      <div className="mb-4 text-center">
        <p className={cn("text-4xl font-bold", urgencyColors(daysRemaining))}>
          {daysRemaining}
        </p>
        <p className="text-sm text-muted-foreground">days remaining</p>
        {weeks > 0 && (
          <p className="mt-1 text-xs text-muted-foreground">
            {weeks} week{weeks !== 1 ? "s" : ""}, {days} day{days !== 1 ? "s" : ""}
          </p>
        )}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3">
        <div className="rounded-md bg-muted/50 p-3">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            Daily Target
          </div>
          <p className="mt-1 text-lg font-semibold">{dailyHours ?? 6}h</p>
        </div>
        <div className="rounded-md bg-muted/50 p-3">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Target className="h-3 w-3" />
            Exam Date
          </div>
          <p className="mt-1 text-sm font-semibold">{exam.toLocaleDateString()}</p>
        </div>
      </div>

      {predictedScore !== undefined && (
        <div className={cn(
          "rounded-md border p-3",
          scoreDiff !== null && scoreDiff > 0
            ? "border-amber-500/20 bg-amber-500/5"
            : "border-emerald-500/20 bg-emerald-500/5",
        )}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-muted-foreground">Predicted Score</p>
              <p className="text-xl font-bold">{predictedScore}/720</p>
            </div>
            {scoreDiff !== null && (
              <div className="text-right">
                <p className="text-xs text-muted-foreground">Gap to Target</p>
                <div className="flex items-center gap-1">
                  {scoreDiff > 0 ? (
                    <TrendingDown className="h-4 w-4 text-amber-500" />
                  ) : (
                    <TrendingUp className="h-4 w-4 text-emerald-500" />
                  )}
                  <p className={cn(
                    "text-sm font-semibold",
                    scoreDiff > 0 ? "text-amber-600" : "text-emerald-600",
                  )}>
                    {scoreDiff > 0 ? `+${scoreDiff}` : scoreDiff} pts
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
