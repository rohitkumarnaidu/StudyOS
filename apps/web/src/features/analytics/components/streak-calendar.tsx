"use client";

import { cn } from "@/shared/lib";
import { Flame } from "lucide-react";

interface StreakCalendarProps {
  data: Array<{ date: string; active: boolean }>;
  currentStreak: number;
  longestStreak: number;
}

export function StreakCalendar({ data, currentStreak, longestStreak }: StreakCalendarProps) {
  const days = data.slice(-30);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold">Last 30 Days</h3>
        {currentStreak > 0 && (
          <div className="flex items-center gap-1 text-orange-500">
            <Flame className="h-4 w-4" fill="currentColor" />
            <span className="text-sm font-bold">{currentStreak}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-7 gap-1">
        {["S", "M", "T", "W", "T", "F", "S"].map((d, i) => (
          <div key={i} className="text-center text-xs text-muted-foreground font-medium">
            {d}
          </div>
        ))}
        {days.map((day, i) => (
          <div
            key={i}
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-md text-xs transition-colors",
              day.active
                ? "bg-orange-500 text-white font-medium"
                : "bg-muted text-muted-foreground",
            )}
            title={`${day.date}: ${day.active ? "Studied" : "Missed"}`}
          >
            {new Date(day.date).getDate()}
          </div>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
        <span>Current: {currentStreak} days</span>
        <span>Best: {longestStreak} days</span>
      </div>
    </div>
  );
}
