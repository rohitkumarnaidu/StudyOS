"use client";

import { useCallback, useEffect, useState, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { getChapters, getExams, type ChapterData } from "@/server/syllabus/get-chapters";
import { db, type SyllabusChapter } from "@/features/offline/dexie";

export function useSyllabusCache(examId?: string) {
  const [chapters, setChapters] = useState<ChapterData[]>([]);
  const [loading, setLoading] = useState(true);
  const [fromCache, setFromCache] = useState(false);
  const queryClient = useQueryClient();
  const initialized = useRef(false);

  const fetchAndCache = useCallback(async () => {
    setLoading(true);
    setFromCache(false);

    try {
      const exams = examId ? [{ id: examId }] : await getExams();
      const targetExam = exams[0];

      if (!targetExam) {
        setChapters([]);
        return;
      }

      const data = await getChapters(targetExam.id);

      await db.chapters.put({
        id: targetExam.id,
        name: "NEET 2026",
        sort_order: 1,
        topics: [],
        cached_at: Date.now(),
        ...data,
      } as unknown as SyllabusChapter);

      setChapters(data);
      queryClient.setQueryData(["syllabus-cache", targetExam.id], data);
    } catch {
      const cached = await db.chapters.toArray();
      if (cached.length > 0) {
        const flat = cached.flatMap((c) => (c as unknown as ChapterData[]));
        setChapters(flat);
        setFromCache(true);
      }
    } finally {
      setLoading(false);
    }
  }, [examId, queryClient]);

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;
      void fetchAndCache();
    }
  }, [fetchAndCache]);

  return { chapters, loading, fromCache, refetch: fetchAndCache };
}
