"use client";

import { ProgressRing } from "@/features/progress/components/progress-ring";
import { StreakBadge } from "@/features/progress/components/streak-badge";
import { useStreak } from "@/features/progress/hooks/use-progress";
import { Skeleton } from "@/shared/components/ui/skeleton";

export default function ProgressPage() {
  const { data: streak, isLoading } = useStreak();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Progress</h1>
        <p className="text-sm text-muted-foreground">
          Track your study progress and streaks.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border border-border bg-card p-6 flex flex-col items-center">
          <ProgressRing progress={0} size={120} strokeWidth={8} label="Overall" />
        </div>

        <div className="rounded-lg border border-border bg-card p-6 flex flex-col items-center justify-center">
          {isLoading ? (
            <Skeleton className="h-8 w-32 rounded-full" />
          ) : streak ? (
            <StreakBadge currentStreak={streak.current_streak} longestStreak={streak.longest_streak} size="lg" />
          ) : (
            <span className="text-sm text-muted-foreground">No streak yet</span>
          )}
        </div>
      </div>
    </div>
  );
}
