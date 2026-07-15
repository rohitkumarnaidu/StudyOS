"use client";

import { ProgressRing } from "@/features/progress/components/progress-ring";
import { StreakBadge } from "@/features/progress/components/streak-badge";
import { useStreak } from "@/features/progress/hooks/use-progress";
import { Skeleton } from "@/shared/components/ui/skeleton";

interface StudyStatsProps {
  examProgress: number;
  chaptersCompleted: number;
  totalChapters: number;
  subtopicsCompleted: number;
  totalSubtopics: number;
}

export function StudyStats({
  examProgress,
  chaptersCompleted,
  totalChapters,
  subtopicsCompleted,
  totalSubtopics,
}: StudyStatsProps) {
  const { data: streak, isLoading: streakLoading } = useStreak();

  return (
    <div className="flex flex-wrap items-center gap-6 rounded-lg border border-border bg-card p-4">
      <ProgressRing
        progress={examProgress}
        size={72}
        strokeWidth={5}
        label="Overall"
      />

      <div className="flex flex-col gap-1">
        <span className="text-sm font-medium text-foreground">Chapters</span>
        <span className="text-xs text-muted-foreground">
          {chaptersCompleted} / {totalChapters}
        </span>
      </div>

      <div className="flex flex-col gap-1">
        <span className="text-sm font-medium text-foreground">Subtopics</span>
        <span className="text-xs text-muted-foreground">
          {subtopicsCompleted} / {totalSubtopics}
        </span>
      </div>

      <div className="ml-auto">
        {streakLoading ? (
          <Skeleton className="h-8 w-24 rounded-full" />
        ) : streak ? (
          <StreakBadge
            currentStreak={streak.current_streak}
            longestStreak={streak.longest_streak}
          />
        ) : (
          <span className="text-xs text-muted-foreground">Start studying to build a streak!</span>
        )}
      </div>
    </div>
  );
}
