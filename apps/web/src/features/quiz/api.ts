import { apiFetch } from "@/shared/api";

export interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: "mcq" | "numeric" | "assertion_reason" | "match_following";
  option_a: string | null;
  option_b: string | null;
  option_c: string | null;
  option_d: string | null;
  difficulty: number;
}

export interface QuizSession {
  id: string;
  title: string;
  quiz_type: "practice" | "timed" | "mock";
  chapter_id: string | null;
  total_questions: number;
  time_limit_minutes: number | null;
  started_at: string;
  completed_at: string | null;
  score: number | null;
}

export interface QuizResult {
  session_id: string;
  total_questions: number;
  correct: number;
  incorrect: number;
  skipped: number;
  score_percent: number;
  time_taken_seconds: number;
  responses: Array<{
    question_id: string;
    question_text: string;
    user_answer: string | null;
    correct_answer: string;
    is_correct: boolean;
    explanation: string | null;
    difficulty: number;
  }>;
}

export interface MistakeEntry {
  id: string;
  question_id: string;
  question_text: string;
  user_answer: string | null;
  correct_answer: string;
  explanation: string | null;
  reviewed: boolean;
  review_count: number;
  created_at: string;
}

export interface CreateQuizRequest {
  chapter_id?: string;
  topic_ids?: string[];
  question_count: number;
  quiz_type: "practice" | "timed" | "mock";
  time_limit_minutes?: number;
  difficulty?: number;
}

export async function createQuizSession(body: CreateQuizRequest): Promise<QuizSession> {
  return apiFetch<QuizSession>("/v1/quizzes", { method: "POST", body });
}

export async function getQuizQuestions(sessionId: string): Promise<QuizQuestion[]> {
  return apiFetch<QuizQuestion[]>(`/v1/quizzes/${sessionId}/questions`);
}

export async function submitAnswer(
  sessionId: string,
  questionId: string,
  answer: string,
): Promise<{ is_correct: boolean }> {
  return apiFetch(`/v1/quizzes/${sessionId}/answers`, {
    method: "POST",
    body: { question_id: questionId, answer },
  });
}

export async function finishQuizSession(sessionId: string): Promise<QuizResult> {
  return apiFetch<QuizResult>(`/v1/quizzes/${sessionId}/finish`, {
    method: "POST",
  });
}

export async function getQuizResult(sessionId: string): Promise<QuizResult> {
  return apiFetch<QuizResult>(`/v1/quizzes/${sessionId}/result`);
}

export async function listQuizSessions(chapterId?: string): Promise<QuizSession[]> {
  const params = chapterId ? `?chapter_id=${chapterId}` : "";
  return apiFetch<QuizSession[]>(`/v1/quizzes/sessions${params}`);
}

export async function listMistakes(chapterId?: string): Promise<MistakeEntry[]> {
  const params = chapterId ? `?chapter_id=${chapterId}` : "";
  return apiFetch<MistakeEntry[]>(`/v1/quizzes/mistakes${params}`);
}

export async function reviewMistake(mistakeId: string): Promise<void> {
  await apiFetch(`/v1/quizzes/mistakes/${mistakeId}/review`, { method: "POST" });
}

export async function deleteMistake(mistakeId: string): Promise<void> {
  await apiFetch(`/v1/quizzes/mistakes/${mistakeId}`, { method: "DELETE" });
}
