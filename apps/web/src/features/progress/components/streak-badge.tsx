"use client";

import { cn } from "@/shared/lib";
import { Flame } from "lucide-react";

interface StreakBadgeProps {
  currentStreak: number;
  longestStreak: number;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function StreakBadge({
  currentStreak,
  longestStreak,
  className,
  size = "md",
}: StreakBadgeProps) {
  const sizes = {
    sm: { icon: "h-3 w-3", text: "text-xs", container: "px-2 py-1" },
    md: { icon: "h-4 w-4", text: "text-sm", container: "px-3 py-1.5" },
    lg: { icon: "h-5 w-5", text: "text-base", container: "px-4 py-2" },
  };

  const s = sizes[size];

  if (currentStreak === 0) {
    return null;
  }

  const isMilestone = currentStreak >= 7 && currentStreak % 7 === 0;

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full bg-orange-500/10 text-orange-600 dark:text-orange-400",
        s.container,
        isMilestone && "animate-pulse bg-orange-500/20",
        className,
      )}
    >
      <Flame
        className={cn(s.icon, isMilestone && "text-orange-500")}
        fill={isMilestone ? "currentColor" : "none"}
      />
      <span className={cn("font-semibold", s.text)}>
        {currentStreak} day{currentStreak !== 1 ? "s" : ""}
      </span>
      {longestStreak > currentStreak && (
        <span className={cn("text-muted-foreground", s.text)}>
          (best: {longestStreak})
        </span>
      )}
    </div>
  );
}
