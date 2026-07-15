import { apiFetch } from "@/shared/api";

export interface ToggleProgressResponse {
  completed: boolean;
  chapter_progress: number;
  subject_progress: number;
  exam_progress: number;
}

export interface ChapterProgressResponse {
  chapter_id: string;
  progress_pct: number;
  completed_subtopics: string[];
  total_subtopics: number;
}

export interface StreakData {
  current_streak: number;
  longest_streak: number;
  last_study_date: string;
}

export async function toggleSubtopic(subtopicId: string): Promise<ToggleProgressResponse> {
  const response = await apiFetch<ToggleProgressResponse>(
    `/v1/progress/subtopics/${subtopicId}/toggle`,
    { method: "POST" },
  );
  return response;
}

export async function getChapterProgress(chapterId: string): Promise<ChapterProgressResponse> {
  const response = await apiFetch<ChapterProgressResponse>(
    `/v1/progress/chapters/${chapterId}`,
  );
  return response;
}

export async function getStreak(): Promise<StreakData> {
  const response = await apiFetch<StreakData>("/v1/progress/streak");
  return response;
}
