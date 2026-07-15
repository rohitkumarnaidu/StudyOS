"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toggleSubtopic } from "@/features/progress/api";
import { useOfflineCompletions } from "@/features/offline/hooks/use-offline-completions";
import { useSyncQueue } from "@/features/offline/sync-queue";

export function useOfflineToggleSubtopic() {
  const queryClient = useQueryClient();
  const { toggleLocal } = useOfflineCompletions();
  const { enqueue } = useSyncQueue();

  return useMutation({
    mutationFn: async (subtopicId: string) => {
      const isOnline = navigator.onLine;

      if (isOnline) {
        try {
          await toggleSubtopic(subtopicId);
        } catch {
          await toggleLocal(subtopicId);
          await enqueue(subtopicId);
        }
      } else {
        await toggleLocal(subtopicId);
        await enqueue(subtopicId);
      }
    },
    onMutate: async (subtopicId) => {
      await queryClient.cancelQueries({ queryKey: ["chapter-progress"] });
      const previous = queryClient.getQueriesData({ queryKey: ["chapter-progress"] });

      queryClient.setQueriesData({ queryKey: ["chapter-progress"] }, (old: unknown) => {
        if (!old) return old;
        const data = old as { completed_subtopics?: string[] };
        const completed = data.completed_subtopics ?? [];
        const isCompleted = completed.includes(subtopicId);
        return {
          ...data,
          completed_subtopics: isCompleted
            ? completed.filter((id: string) => id !== subtopicId)
            : [...completed, subtopicId],
        };
      });

      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        for (const [key, value] of context.previous) {
          queryClient.setQueryData(key, value);
        }
      }
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["chapter-progress"] });
      void queryClient.invalidateQueries({ queryKey: ["streak"] });
    },
  });
}

export function useOfflineCompletedIds() {
  const { completedIds } = useOfflineCompletions();
  return completedIds;
}
