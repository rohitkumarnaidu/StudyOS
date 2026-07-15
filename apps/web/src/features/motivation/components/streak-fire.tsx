"use client";

import { cn } from "@/shared/lib";
import { Flame } from "lucide-react";

interface StreakFireProps {
  streak: number;
  size?: "sm" | "md" | "lg";
  animated?: boolean;
}

export function StreakFire({ streak, size = "md", animated = true }: StreakFireProps) {
  if (streak === 0) return null;

  const sizes = {
    sm: { container: "h-8 w-8", icon: "h-4 w-4", text: "text-xs" },
    md: { container: "h-12 w-12", icon: "h-6 w-6", text: "text-sm" },
    lg: { container: "h-16 w-16", icon: "h-8 w-8", text: "text-lg" },
  };

  const s = sizes[size];
  const isMilestone = streak >= 7 && streak % 7 === 0;

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className={cn(
          "flex items-center justify-center rounded-full bg-orange-500/10",
          s.container,
          animated && isMilestone && "animate-pulse",
        )}
      >
        <Flame
          className={cn(s.icon, isMilestone ? "text-orange-500" : "text-orange-400")}
          fill={isMilestone ? "currentColor" : "none"}
        />
      </div>
      <span className={cn("font-bold text-orange-500", s.text)}>
        {streak}
      </span>
      <span className="text-xs text-muted-foreground">
        {streak === 1 ? "day" : "days"}
      </span>
    </div>
  );
}
