"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  analyzeGaps,
  clusterMistakes,
  getHighRiskConcepts,
  getImprovementTrend,
  getIntelligenceReport,
  getMasteryLevel,
  getMistakeStats,
  getMistakes,
  getPredictions,
  getStudyPlan,
  getWeakConcepts,
  logMistake,
} from "@/features/mistake-intelligence/api";

export function useMistakeStats() {
  return useQuery({
    queryKey: ["mistake-intelligence", "stats"],
    queryFn: getMistakeStats,
  });
}

export function useMistakes(filters?: { mistake_type?: string; concept?: string }) {
  return useQuery({
    queryKey: ["mistake-intelligence", "mistakes", filters],
    queryFn: () => getMistakes(filters),
  });
}

export function useLogMistake() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: logMistake,
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["mistake-intelligence"] });
    },
  });
}

export function useKnowledgeGaps(minAttempts = 3) {
  return useQuery({
    queryKey: ["mistake-intelligence", "gaps", minAttempts],
    queryFn: () => analyzeGaps(minAttempts),
  });
}

export function useWeakConcepts(topN = 5) {
  return useQuery({
    queryKey: ["mistake-intelligence", "weak-concepts", topN],
    queryFn: () => getWeakConcepts(topN),
  });
}

export function useMasteryLevel(concept: string | null) {
  return useQuery({
    queryKey: ["mistake-intelligence", "mastery", concept],
    queryFn: () => getMasteryLevel(concept!),
    enabled: !!concept,
  });
}

export function useStudyPlan(maxConcepts = 5) {
  return useQuery({
    queryKey: ["mistake-intelligence", "study-plan", maxConcepts],
    queryFn: () => getStudyPlan(maxConcepts),
  });
}

export function usePredictions(concepts?: string[]) {
  return useQuery({
    queryKey: ["mistake-intelligence", "predictions", concepts],
    queryFn: () => getPredictions(concepts),
  });
}

export function useHighRiskConcepts(threshold = 0.7) {
  return useQuery({
    queryKey: ["mistake-intelligence", "high-risk", threshold],
    queryFn: () => getHighRiskConcepts(threshold),
  });
}

export function useImprovementTrend(concept: string | null) {
  return useQuery({
    queryKey: ["mistake-intelligence", "trend", concept],
    queryFn: () => getImprovementTrend(concept!),
    enabled: !!concept,
  });
}

export function useClusterMistakes() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ minClusterSize = 2 }: { minClusterSize?: number } = {}) => clusterMistakes(minClusterSize),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["mistake-intelligence", "clusters"] });
    },
  });
}

export function useIntelligenceReport() {
  return useQuery({
    queryKey: ["mistake-intelligence", "report"],
    queryFn: getIntelligenceReport,
  });
}
