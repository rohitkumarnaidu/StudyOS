"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  generateRoadmap,
  getPriorityScores,
  getPrediction,
  getPredictionHistory,
  generateRecoveryPlan,
  getActiveRecoveryPlan,
  optimizeForExam,
} from "@/features/roadmap/api";
import { notifyError, notifySuccess } from "@/shared/lib";

export function useRoadmap(examDate?: string) {
  return useQuery({
    queryKey: ["roadmap", examDate],
    queryFn: () => generateRoadmap(examDate),
    enabled: false,
  });
}

export function usePriorityScores() {
  return useQuery({
    queryKey: ["roadmap", "priority-scores"],
    queryFn: getPriorityScores,
  });
}

export function usePrediction() {
  return useQuery({
    queryKey: ["roadmap", "prediction"],
    queryFn: getPrediction,
  });
}

export function usePredictionHistory(limit = 10) {
  return useQuery({
    queryKey: ["roadmap", "predictions", "history", limit],
    queryFn: () => getPredictionHistory(limit),
  });
}

export function useGenerateRoadmap() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (examDate?: string) => generateRoadmap(examDate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmap"] });
      notifySuccess("Roadmap generated successfully");
    },
    onError: () => {
      notifyError("Failed to generate roadmap");
    },
  });
}

export function useGenerateRecoveryPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ examDate, triggerReason }: { examDate: string; triggerReason?: string }) =>
      generateRecoveryPlan(examDate, triggerReason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmap", "recovery"] });
      notifySuccess("Recovery plan generated");
    },
    onError: () => {
      notifyError("Failed to generate recovery plan");
    },
  });
}

export function useActiveRecoveryPlan() {
  return useQuery({
    queryKey: ["roadmap", "recovery", "active"],
    queryFn: getActiveRecoveryPlan,
  });
}

export function useOptimizeExam() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (examDate: string) => optimizeForExam(examDate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["roadmap"] });
      notifySuccess("Study plan optimized");
    },
    onError: () => {
      notifyError("Failed to optimize study plan");
    },
  });
}
