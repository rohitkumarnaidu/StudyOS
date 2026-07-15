"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createActiveRecallSession,
  createItem,
  generateRevisionPack,
  getActiveRecallSession,
  getDueItems,
  getRetentionSummary,
  getRevisionPack,
  reviewItem,
  submitActiveRecallAnswer,
} from "@/features/revision/api";

export function useDueItems() {
  return useQuery({
    queryKey: ["revision", "due-items"],
    queryFn: getDueItems,
  });
}

export function useRetentionSummary() {
  return useQuery({
    queryKey: ["revision", "retention"],
    queryFn: getRetentionSummary,
  });
}

export function useReviewItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, quality }: { itemId: string; quality: number }) =>
      reviewItem(itemId, quality),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["revision", "due-items"] });
      void queryClient.invalidateQueries({ queryKey: ["revision", "retention"] });
    },
  });
}

export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ contentType, contentId }: { contentType: string; contentId: string }) =>
      createItem(contentType, contentId),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["revision", "due-items"] });
    },
  });
}

export function useGenerateRevisionPack() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ mode, maxItems }: { mode: "due" | "weak" | "mixed" | "cram"; maxItems?: number }) =>
      generateRevisionPack(mode, maxItems),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["revision", "packs"] });
    },
  });
}

export function useRevisionPack(packId: string | null) {
  return useQuery({
    queryKey: ["revision", "packs", packId],
    queryFn: () => getRevisionPack(packId!),
    enabled: !!packId,
  });
}

export function useCreateActiveRecallSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ packId, maxQuestions }: { packId?: string; maxQuestions?: number }) =>
      createActiveRecallSession(packId, maxQuestions),
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["revision", "active-recall"] });
    },
  });
}

export function useActiveRecallSession(sessionId: string | null) {
  return useQuery({
    queryKey: ["revision", "active-recall", sessionId],
    queryFn: () => getActiveRecallSession(sessionId!),
    enabled: !!sessionId,
  });
}

export function useSubmitActiveRecallAnswer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ sessionId, questionId, answer }: { sessionId: string; questionId: string; answer: string }) =>
      submitActiveRecallAnswer(sessionId, questionId, answer),
    onSettled: (_data, _error, variables) => {
      void queryClient.invalidateQueries({
        queryKey: ["revision", "active-recall", variables.sessionId],
      });
    },
  });
}
