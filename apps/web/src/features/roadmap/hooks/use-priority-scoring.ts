"use client";

import { useMemo } from "react";
import { usePriorityScores } from "@/features/roadmap/hooks/use-roadmap";
import type { PriorityScore } from "@/features/roadmap/api";

export function usePriorityScoring() {
  const { data, isLoading, error } = usePriorityScores();

  const scores = useMemo(() => {
    if (!data?.scores) return [];
    return data.scores;
  }, [data]);

  const criticalChapters = useMemo(() => {
    return scores.filter((s: PriorityScore) => s.score >= 80);
  }, [scores]);

  const highPriorityChapters = useMemo(() => {
    return scores.filter((s: PriorityScore) => s.score >= 60 && s.score < 80);
  }, [scores]);

  const bySubject = useMemo(() => {
    const grouped: Record<string, PriorityScore[]> = {};
    for (const score of scores) {
      if (!grouped[score.subject_name]) {
        grouped[score.subject_name] = [];
      }
      grouped[score.subject_name].push(score);
    }
    return grouped;
  }, [scores]);

  const averageScore = useMemo(() => {
    if (scores.length === 0) return 0;
    return scores.reduce((sum: number, s: PriorityScore) => sum + s.score, 0) / scores.length;
  }, [scores]);

  return {
    scores,
    isLoading,
    error,
    criticalChapters,
    highPriorityChapters,
    bySubject,
    averageScore: Math.round(averageScore),
  };
}
