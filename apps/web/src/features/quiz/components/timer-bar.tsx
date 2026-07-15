"use client";

import { useEffect, useState } from "react";
import { cn } from "@/shared/lib";
import { AlertTriangle } from "lucide-react";

interface TimerBarProps {
  totalSeconds: number;
  onTimeUp: () => void;
  paused?: boolean;
}

export function TimerBar({ totalSeconds, onTimeUp, paused = false }: TimerBarProps) {
  const [remaining, setRemaining] = useState(totalSeconds);

  useEffect(() => {
    if (paused) return;
    if (remaining <= 0) {
      onTimeUp();
      return;
    }
    const interval = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          onTimeUp();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [remaining, paused, onTimeUp]);

  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  const percent = totalSeconds > 0 ? (remaining / totalSeconds) * 100 : 0;
  const isLow = remaining < 300;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className={cn("font-mono tabular-nums", isLow && "text-destructive animate-pulse")}>
          {isLow && <AlertTriangle className="mr-1 inline h-4 w-4" />}
          {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
        </span>
        <span className="text-xs text-muted-foreground">
          {Math.round(percent)}% remaining
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-1000 ease-linear",
            isLow ? "bg-destructive" : "bg-primary",
          )}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
