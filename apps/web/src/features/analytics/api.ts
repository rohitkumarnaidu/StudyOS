import { apiFetch } from "@/shared/api";

export interface AnalyticsOverview {
  total_study_days: number;
  total_subtopics_completed: number;
  total_chapters_completed: number;
  current_streak: number;
  longest_streak: number;
  avg_quiz_score: number;
  total_quizzes_taken: number;
  total_study_hours: number;
}

export interface DailyProgress {
  date: string;
  subtopics_completed: number;
  study_minutes: number;
}

export interface SubjectProgress {
  subject_id: string;
  subject_name: string;
  completed: number;
  total: number;
  percentage: number;
}

export interface QuizTrend {
  date: string;
  score: number;
  question_count: number;
}

export interface WeakArea {
  chapter_id: string;
  chapter_name: string;
  subject_name: string;
  progress_pct: number;
  quiz_avg: number | null;
  last_studied: string | null;
  priority: "high" | "medium" | "low";
}

export interface RoadmapItem {
  id: string;
  title: string;
  description: string | null;
  target_date: string;
  priority: 1 | 2 | 3;
  status: "pending" | "in_progress" | "completed" | "skipped";
  chapter_name: string | null;
}

export interface Achievement {
  id: string;
  code: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  unlocked_at: string | null;
}

export async function getAnalyticsOverview(): Promise<AnalyticsOverview> {
  return apiFetch<AnalyticsOverview>("/v1/analytics/overview");
}

export async function getDailyProgress(days: number = 30): Promise<DailyProgress[]> {
  return apiFetch<DailyProgress[]>(`/v1/analytics/daily?days=${days}`);
}

export async function getSubjectProgress(): Promise<SubjectProgress[]> {
  return apiFetch<SubjectProgress[]>("/v1/analytics/subjects");
}

export async function getQuizTrends(days: number = 30): Promise<QuizTrend[]> {
  return apiFetch<QuizTrend[]>(`/v1/analytics/quiz-trends?days=${days}`);
}

export async function getWeakAreas(): Promise<WeakArea[]> {
  return apiFetch<WeakArea[]>("/v1/analytics/weak-areas");
}

export async function getRoadmap(): Promise<RoadmapItem[]> {
  return apiFetch<RoadmapItem[]>("/v1/roadmap");
}

export async function generateRoadmap(): Promise<RoadmapItem[]> {
  return apiFetch<RoadmapItem[]>("/v1/roadmap/generate", { method: "POST" });
}

export async function updateRoadmapItem(
  itemId: string,
  status: RoadmapItem["status"],
): Promise<void> {
  await apiFetch(`/v1/roadmap/items/${itemId}`, {
    method: "PATCH",
    body: { status },
  });
}

export async function getAchievements(): Promise<Achievement[]> {
  return apiFetch<Achievement[]>("/v1/achievements");
}
