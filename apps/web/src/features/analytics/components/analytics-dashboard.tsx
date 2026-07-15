"use client";

import { useState, useEffect } from "react";
import { cn } from "@/shared/lib";
import { getAnalyticsOverview, getDailyProgress, getSubjectProgress, getQuizTrends, getWeakAreas } from "@/features/analytics/api";
import type { AnalyticsOverview, DailyProgress, SubjectProgress, QuizTrend, WeakArea } from "@/features/analytics/api";
import { ProgressChart } from "@/features/analytics/components/progress-chart";
import { SubjectBreakdown } from "@/features/analytics/components/subject-breakdown";
import { StudyHeatmap } from "@/features/analytics/components/study-heatmap";
import { QuizAnalytics } from "@/features/analytics/components/quiz-analytics";
import { StreakCalendar } from "@/features/analytics/components/streak-calendar";
import { WeakAreas } from "@/features/analytics/components/weak-areas";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { BookOpen, Clock, Trophy, Target } from "lucide-react";

export function AnalyticsDashboard() {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [dailyData, setDailyData] = useState<DailyProgress[]>([]);
  const [subjectData, setSubjectData] = useState<SubjectProgress[]>([]);
  const [quizData, setQuizData] = useState<QuizTrend[]>([]);
  const [weakAreas, setWeakAreas] = useState<WeakArea[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getAnalyticsOverview().catch(() => null),
      getDailyProgress(30).catch(() => []),
      getSubjectProgress().catch(() => []),
      getQuizTrends(30).catch(() => []),
      getWeakAreas().catch(() => []),
    ]).then(([ov, daily, subjects, quizzes, weak]) => {
      setOverview(ov);
      setDailyData(daily);
      setSubjectData(subjects);
      setQuizData(quizzes);
      setWeakAreas(weak);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-64 rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  const heatmapData = dailyData.map((d) => ({ date: d.date, count: d.subtopics_completed }));
  const streakData = dailyData.map((d) => ({ date: d.date, active: d.subtopics_completed > 0 }));

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={BookOpen}
          label="Chapters Done"
          value={overview?.total_chapters_completed ?? 0}
          color="text-blue-500"
        />
        <StatCard
          icon={Target}
          label="Subtopics Done"
          value={overview?.total_subtopics_completed ?? 0}
          color="text-emerald-500"
        />
        <StatCard
          icon={Clock}
          label="Study Hours"
          value={overview?.total_study_hours ?? 0}
          color="text-amber-500"
        />
        <StatCard
          icon={Trophy}
          label="Avg Quiz Score"
          value={`${overview?.avg_quiz_score ?? 0}%`}
          color="text-purple-500"
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <ProgressChart
          data={dailyData.map((d) => ({ date: d.date.slice(5), value: d.subtopics_completed }))}
          title="Daily Subtopics Completed"
          color="#10b981"
        />
        {subjectData.length > 0 && (
          <SubjectBreakdown
            data={subjectData.map((s) => ({
              name: s.subject_name,
              completed: s.completed,
              total: s.total,
              percentage: s.percentage,
            }))}
          />
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <StudyHeatmap data={heatmapData} />
        <QuizAnalytics data={quizData} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <StreakCalendar
          data={streakData}
          currentStreak={overview?.current_streak ?? 0}
          longestStreak={overview?.longest_streak ?? 0}
        />
        <WeakAreas data={weakAreas} />
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-3">
        <Icon className={cn("h-5 w-5", color)} />
        <div>
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-xs text-muted-foreground">{label}</p>
        </div>
      </div>
    </div>
  );
}
