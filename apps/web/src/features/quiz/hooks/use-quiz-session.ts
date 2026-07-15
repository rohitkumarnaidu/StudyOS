"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { getQuizQuestions, finishQuizSession, getQuizResult, type QuizQuestion, type QuizResult } from "@/features/quiz/api";
import { notifyError } from "@/shared/lib";

// eslint-disable-next-line @typescript-eslint/no-unused-vars -- reserved for future quiz type-specific logic
export function useQuizSession(sessionId: string, _quizType: "practice" | "timed" | "mock") {
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [finished, setFinished] = useState(false);
  const loadingRef = useRef(false);

  useEffect(() => {
    let cancelled = false;
    loadingRef.current = true;
    getQuizQuestions(sessionId)
      .then((data) => {
        if (!cancelled) setQuestions(data);
      })
      .catch(() => {
        if (!cancelled) notifyError("Failed to load quiz questions");
      })
      .finally(() => {
        if (!cancelled) {
          loadingRef.current = false;
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleFinish = useCallback(async () => {
    try {
      const res = await finishQuizSession(sessionId);
      setResult(res);
      setFinished(true);
    } catch {
      notifyError("Failed to finish quiz");
    }
  }, [sessionId]);

  const loadResult = useCallback(async () => {
    try {
      const res = await getQuizResult(sessionId);
      setResult(res);
      setFinished(true);
    } catch {
      notifyError("Failed to load quiz result");
    }
  }, [sessionId]);

  return {
    questions,
    loading,
    result,
    finished,
    handleFinish,
    loadResult,
  };
}
