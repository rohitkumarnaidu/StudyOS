"use client";

import { StreakFire } from "@/features/motivation/components/streak-fire";

export default function AchievementsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Achievements</h1>
        <p className="text-sm text-muted-foreground">
          Track your milestones and unlock new achievements.
        </p>
      </div>

      <div className="flex items-center justify-center rounded-lg border border-border bg-card p-8">
        <StreakFire streak={0} size="lg" />
      </div>
    </div>
  );
}
