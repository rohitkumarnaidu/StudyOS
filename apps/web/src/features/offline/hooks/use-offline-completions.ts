"use client";

import { useEffect, useState } from "react";
import { db } from "@/features/offline/dexie";

export function useOfflineCompletions() {
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    const loadCompletions = async () => {
      const completions = await db.completions.toArray();
      const ids = new Set(
        completions.filter((c) => c.completed).map((c) => c.subtopic_id),
      );
      setCompletedIds(ids);
    };

    void loadCompletions();

    const interval = setInterval(() => void loadCompletions(), 5000);
    return () => clearInterval(interval);
  }, []);

  async function toggleLocal(subtopicId: string) {
    const existing = await db.completions.get(subtopicId);

    if (existing) {
      await db.completions.update(subtopicId, {
        completed: !existing.completed,
        synced: false,
        timestamp: Date.now(),
      });
    } else {
      await db.completions.put({
        subtopic_id: subtopicId,
        completed: true,
        synced: false,
        timestamp: Date.now(),
      });
    }

    setCompletedIds((prev) => {
      const next = new Set(prev);
      if (next.has(subtopicId)) {
        next.delete(subtopicId);
      } else {
        next.add(subtopicId);
      }
      return next;
    });
  }

  return { completedIds, toggleLocal };
}
