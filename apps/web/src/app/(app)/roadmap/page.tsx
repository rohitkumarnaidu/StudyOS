"use client";

import { useState, useEffect, useCallback } from "react";
import { getRoadmap, generateRoadmap } from "@/features/analytics/api";
import type { RoadmapItem } from "@/features/analytics/api";
import { RoadmapTimeline } from "@/features/roadmap/components/roadmap-timeline";
import { AchievementBadges } from "@/features/motivation/components/achievement-badges";
import { StreakFire } from "@/features/motivation/components/streak-fire";
import { getAchievements } from "@/features/analytics/api";
import type { Achievement } from "@/features/analytics/api";
import { Button } from "@/shared/components/ui/button";
import { Sparkles, Loader2 } from "lucide-react";
import { notifySuccess, notifyError } from "@/shared/lib";

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<RoadmapItem[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [currentStreak] = useState(0);

  const refreshData = useCallback(async () => {
    try {
      const [roadmapData, achievementData] = await Promise.all([
        getRoadmap().catch(() => []),
        getAchievements().catch(() => []),
      ]);
      setRoadmap(roadmapData);
      setAchievements(achievementData);
    } catch {
      notifyError("Failed to load data");
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [roadmapData, achievementData] = await Promise.all([
          getRoadmap().catch(() => []),
          getAchievements().catch(() => []),
        ]);
        if (!cancelled) {
          setRoadmap(roadmapData);
          setAchievements(achievementData);
        }
      } catch {
        if (!cancelled) notifyError("Failed to load data");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const data = await generateRoadmap();
      setRoadmap(data);
      notifySuccess("Roadmap generated!");
    } catch {
      notifyError("Failed to generate roadmap");
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return <div className="py-8 text-center text-sm text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Roadmap & Achievements</h1>
          <p className="text-sm text-muted-foreground">
            Your personalized study plan and milestones.
          </p>
        </div>
        <Button onClick={handleGenerate} disabled={generating}>
          {generating ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="mr-2 h-4 w-4" />
          )}
          {generating ? "Generating..." : "Generate Roadmap"}
        </Button>
      </div>

      <div className="flex items-center gap-6 rounded-lg border border-border bg-card p-4">
        <StreakFire streak={currentStreak} size="lg" />
        <div>
          <h2 className="text-lg font-semibold">Keep the momentum going!</h2>
          <p className="text-sm text-muted-foreground">
            {currentStreak === 0
              ? "Start studying today to begin your streak."
              : `You're on a ${currentStreak}-day streak. Don't break it!`}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RoadmapTimeline items={roadmap} onStatusChange={refreshData} />
        </div>
        <div>
          <AchievementBadges achievements={achievements} />
        </div>
      </div>
    </div>
  );
}
