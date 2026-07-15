"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getChapterProgress, getStreak, toggleSubtopic } from "@/features/progress/api";

export function useChapterProgress(chapterId: string) {
  return useQuery({
    queryKey: ["chapter-progress", chapterId],
    queryFn: () => getChapterProgress(chapterId),
    enabled: !!chapterId,
  });
}

export function useStreak() {
  return useQuery({
    queryKey: ["streak"],
    queryFn: getStreak,
  });
}

export function useToggleSubtopic() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: toggleSubtopic,
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
