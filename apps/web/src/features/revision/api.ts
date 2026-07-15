import { apiFetch } from "@/shared/api";

export interface SpacedRepetitionItem {
  id: string;
  profile_id: string;
  content_type: string;
  content_id: string;
  ease_factor: number;
  interval: number;
  repetitions: number;
  next_review: string;
  quality: number;
}

export interface ReviewResult {
  item_id: string;
  new_interval: number;
  new_ease_factor: number;
  next_review: string;
  quality: number;
}

export interface RetentionSummary {
  average_retention: number;
  total_records: number;
  weak_items: Array<{
    item_id: string;
    retention: number;
    last_review: string;
  }>;
  model_accuracy: number;
}

export interface RevisionPack {
  pack_id: string;
  profile_id: string;
  mode: "due" | "weak" | "mixed" | "cram";
  items: Array<{
    item_id: string;
    content_type: string;
    content_id: string;
    priority: number;
  }>;
  created_at: string;
}

export interface ActiveRecallSession {
  session_id: string;
  profile_id: string;
  questions: Array<{
    question_id: string;
    question: string;
    answer: string;
    hint?: string;
  }>;
  current_index: number;
  completed: boolean;
  score: number;
  created_at: string;
}

export interface ActiveRecallResult {
  question_id: string;
  correct: boolean;
  user_answer: string;
}

export async function getDueItems(): Promise<SpacedRepetitionItem[]> {
  const response = await apiFetch<{ data: { items: SpacedRepetitionItem[] } }>("/v1/revision/due-items");
  return response.data.items;
}

export async function reviewItem(itemId: string, quality: number): Promise<ReviewResult> {
  const response = await apiFetch<{ data: ReviewResult }>(`/v1/revision/items/${itemId}/review`, {
    method: "POST",
    body: { quality },
  });
  return response.data;
}

export async function createItem(contentType: string, contentId: string): Promise<SpacedRepetitionItem> {
  const response = await apiFetch<{ data: SpacedRepetitionItem }>("/v1/revision/items", {
    method: "POST",
    body: { content_type: contentType, content_id: contentId },
  });
  return response.data;
}

export async function getRetentionSummary(): Promise<RetentionSummary> {
  const response = await apiFetch<{ data: RetentionSummary }>("/v1/revision/retention");
  return response.data;
}

export async function generateRevisionPack(mode: "due" | "weak" | "mixed" | "cram" = "due", maxItems = 20): Promise<RevisionPack> {
  const response = await apiFetch<{ data: RevisionPack }>("/v1/revision/packs", {
    method: "POST",
    body: { mode, max_items: maxItems },
  });
  return response.data;
}

export async function getRevisionPack(packId: string): Promise<RevisionPack | null> {
  const response = await apiFetch<{ data: RevisionPack | null }>(`/v1/revision/packs/${packId}`);
  return response.data;
}

export async function createActiveRecallSession(packId?: string, maxQuestions = 10): Promise<ActiveRecallSession> {
  const response = await apiFetch<{ data: ActiveRecallSession }>("/v1/revision/active-recall", {
    method: "POST",
    body: { pack_id: packId, max_questions: maxQuestions },
  });
  return response.data;
}

export async function submitActiveRecallAnswer(sessionId: string, questionId: string, answer: string): Promise<{ correct: boolean }> {
  const response = await apiFetch<{ data: { correct: boolean } }>(`/v1/revision/active-recall/${sessionId}/answer`, {
    method: "POST",
    body: { question_id: questionId, answer },
  });
  return response.data;
}

export async function getActiveRecallSession(sessionId: string): Promise<ActiveRecallSession> {
  const response = await apiFetch<{ data: ActiveRecallSession }>(`/v1/revision/active-recall/${sessionId}`);
  return response.data;
}
