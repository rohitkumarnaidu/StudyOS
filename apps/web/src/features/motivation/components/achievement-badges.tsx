"use client";

import type { Achievement } from "@/features/analytics/api";
import { Trophy, Flame, Compass, BookOpen, Target, Star, CheckCircle, GraduationCap, Crown, Sparkles } from "lucide-react";

interface AchievementBadgesProps {
  achievements: Achievement[];
}

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  trophy: Trophy,
  flame: Flame,
  compass: Compass,
  "book-open": BookOpen,
  target: Target,
  star: Star,
  "check-circle": CheckCircle,
  "graduation-cap": GraduationCap,
  crown: Crown,
  sparkles: Sparkles,
};

export function AchievementBadges({ achievements }: AchievementBadgesProps) {
  const unlocked = achievements.filter((a) => a.unlocked_at);
  const locked = achievements.filter((a) => !a.unlocked_at);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold">
        Achievements ({unlocked.length}/{achievements.length})
      </h3>

      <div className="mb-4">
        <h4 className="text-xs font-medium text-muted-foreground mb-2">Unlocked</h4>
        <div className="flex flex-wrap gap-3">
          {unlocked.map((a) => {
            const Icon = iconMap[a.icon] ?? Trophy;
            return (
              <div
                key={a.id}
                className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card p-3 w-24 text-center"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/10">
                  <Icon className="h-5 w-5 text-amber-500" />
                </div>
                <span className="text-xs font-medium leading-tight">{a.title}</span>
              </div>
            );
          })}
        </div>
      </div>

      {locked.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-muted-foreground mb-2">Locked</h4>
          <div className="flex flex-wrap gap-3">
            {locked.map((a) => {
              const Icon = iconMap[a.icon] ?? Trophy;
              return (
                <div
                  key={a.id}
                  className="flex flex-col items-center gap-1 rounded-lg border border-border p-3 w-24 text-center opacity-40"
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <span className="text-xs font-medium leading-tight">{a.title}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
