"use client";

import { cn } from "@/shared/lib";

interface PriorityScoreBadgeProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

const scoreColors = (score: number) => {
  if (score >= 80) return "bg-red-500/10 text-red-600 border-red-500/20";
  if (score >= 60) return "bg-amber-500/10 text-amber-600 border-amber-500/20";
  if (score >= 40) return "bg-blue-500/10 text-blue-600 border-blue-500/20";
  return "bg-emerald-500/10 text-emerald-600 border-emerald-500/20";
};

const scoreLabels = (score: number) => {
  if (score >= 80) return "Critical";
  if (score >= 60) return "High";
  if (score >= 40) return "Medium";
  return "Low";
};

const sizeClasses = {
  sm: "text-xs px-1.5 py-0.5",
  md: "text-sm px-2 py-1",
  lg: "text-base px-3 py-1.5",
};

export function PriorityScoreBadge({ score, size = "md", showLabel = true }: PriorityScoreBadgeProps) {
  const clampedScore = Math.min(Math.max(score, 0), 100);

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border font-medium",
        scoreColors(clampedScore),
        sizeClasses[size],
      )}
    >
      <span>{Math.round(clampedScore)}</span>
      {showLabel && <span className="opacity-75">/100</span>}
      {showLabel && size !== "sm" && (
        <span className="ml-1 text-xs opacity-60">{scoreLabels(clampedScore)}</span>
      )}
    </span>
  );
}
