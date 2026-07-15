"use client";

import { useState, useEffect, useCallback } from "react";
import { db, type SyncQueueItem } from "@/features/offline/dexie";
import { toggleSubtopic } from "@/features/progress/api";

let syncInterval: ReturnType<typeof setInterval> | null = null;

export function useSyncQueue() {
  const [queueSize, setQueueSize] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [lastSynced, setLastSynced] = useState<Date | null>(null);

  const sync = useCallback(async () => {
    if (syncing) return;

    const items = await db.syncQueue.toArray();
    if (items.length === 0) return;

    setSyncing(true);

    const failed: SyncQueueItem[] = [];

    for (const item of items) {
      if (!navigator.onLine) {
        failed.push(item);
        continue;
      }

      try {
        await toggleSubtopic(item.subtopic_id);
        await db.completions.where("subtopic_id").equals(item.subtopic_id).modify({
          synced: true,
        });
        if (item.id !== undefined) {
          await db.syncQueue.delete(item.id);
        }
      } catch {
        failed.push({ ...item, attempts: item.attempts + 1 });
      }
    }

    if (failed.length > 0) {
      await db.syncQueue.clear();
      if (failed.some((f) => f.attempts < 5)) {
        await db.syncQueue.bulkPut(failed.filter((f) => f.attempts < 5));
      }
    }

    setLastSynced(new Date());
    setSyncing(false);
    const remaining = await db.syncQueue.count();
    setQueueSize(remaining);
  }, [syncing]);

  useEffect(() => {
    const checkQueue = async () => {
      const count = await db.syncQueue.count();
      setQueueSize(count);
    };

    void checkQueue();

    syncInterval = setInterval(() => {
      if (navigator.onLine && queueSize > 0) {
        void sync();
      }
    }, 15000);

    const onOnline = () => void sync();
    window.addEventListener("online", onOnline);

    return () => {
      if (syncInterval) clearInterval(syncInterval);
      window.removeEventListener("online", onOnline);
    };
  }, [sync, queueSize]);

  async function enqueue(subtopicId: string) {
    const existing = await db.syncQueue
      .where("subtopic_id")
      .equals(subtopicId)
      .first();

    if (existing) {
      await db.syncQueue.update(existing.id!, {
        timestamp: Date.now(),
        attempts: 0,
      });
    } else {
      await db.syncQueue.add({
        subtopic_id: subtopicId,
        action: "toggle",
        timestamp: Date.now(),
        attempts: 0,
      });
    }

    const count = await db.syncQueue.count();
    setQueueSize(count);
  }

  return { queueSize, syncing, lastSynced, sync, enqueue };
}
