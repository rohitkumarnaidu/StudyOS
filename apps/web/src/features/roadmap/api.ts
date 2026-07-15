import { apiFetch } from "@/shared/api";

export interface PriorityScore {
  chapter_id: string;
  chapter_name: string;
  subject_name: string;
  score: number;
  weightage_factor: number;
  weak_area_factor: number;
  time_remaining_factor: number;
  exam_proximity_factor: number;
  computed_at?: string;
}

export interface PerformancePrediction {
  predicted_score: number;
  confidence_lower: number;
  confidence_upper: number;
  model_version: string;
  prediction_date?: string;
  features?: Record<string, unknown>;
}

export interface RecoveryPlan {
  plan_id: string;
  trigger_reason: string;
  days_remaining: number;
  revised_completion_date: string;
  daily_hours_target: number;
  accelerated_chapters: Array<{
    chapter_id: string;
    chapter_name: string;
    subject_name: string;
    weightage: number;
    current_completion: number;
    priority: string;
  }>;
  skipped_chapters: Array<{
    chapter_id: string;
    chapter_name: string;
    subject_name: string;
    weightage: number;
    reason: string;
  }>;
  summary: {
    total_accelerated: number;
    total_skipped: number;
    days_per_chapter: number;
  };
}

export interface ExamOptimization {
  exam_date: string;
  days_remaining: number;
  phase: string;
  subject_analysis: Array<{
    subject_id: string;
    subject_name: string;
    total_chapters: number;
    total_subtopics: number;
    completed_subtopics: number;
    completion_rate: number;
    weak_chapters: Array<Record<string, unknown>>;
    strong_chapters: Array<Record<string, unknown>>;
  }>;
  recommendations: Array<{
    type: string;
    subject?: string;
    message: string;
    priority: string;
  }>;
  daily_target_hours: number;
  weekly_milestones: Array<{
    week: number;
    target_chapters: number;
    target_completion_pct: number;
    focus: string;
  }>;
}

export async function generateRoadmap(examDate?: string) {
  const params = examDate ? `?exam_date=${examDate}` : "";
  return apiFetch<{ priority_scores: PriorityScore[]; prediction: PerformancePrediction }>(
    `/v1/roadmap/generate${params}`,
    { method: "POST" },
  );
}

export async function getPriorityScores() {
  return apiFetch<{ scores: PriorityScore[] }>("/v1/roadmap/priority-scores");
}

export async function getPrediction() {
  return apiFetch<{ prediction: PerformancePrediction }>("/v1/roadmap/predict");
}

export async function getPredictionHistory(limit = 10) {
  return apiFetch<{ history: PerformancePrediction[] }>(
    `/v1/roadmap/predictions/history?limit=${limit}`,
  );
}

export async function generateRecoveryPlan(examDate: string, triggerReason = "behind_schedule") {
  return apiFetch<{ plan: RecoveryPlan }>(
    `/v1/roadmap/recovery?exam_date=${examDate}&trigger_reason=${triggerReason}`,
    { method: "POST" },
  );
}

export async function getActiveRecoveryPlan() {
  return apiFetch<{ plan: RecoveryPlan | null }>("/v1/roadmap/recovery/active");
}

export async function optimizeForExam(examDate: string) {
  return apiFetch<{ optimization: ExamOptimization }>(
    `/v1/roadmap/optimize?exam_date=${examDate}`,
    { method: "POST" },
  );
}
