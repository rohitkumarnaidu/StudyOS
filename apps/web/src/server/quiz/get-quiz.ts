"use server";

import { apiFetch } from "@/shared/api";
import type { QuizResult } from "@/features/quiz/api";

export async function getQuizResult(sessionId: string): Promise<QuizResult | null> {
  try {
    const response = await apiFetch<QuizResult>(`/v1/quizzes/${sessionId}/result`);
    return response || null;
  } catch {
    return null;
  }
}

export async function getQuizQuestions(sessionId: string) {
  try {
    const response = await apiFetch(`/v1/quizzes/${sessionId}/questions`);
    return response || [];
  } catch {
    return [];
  }
}
