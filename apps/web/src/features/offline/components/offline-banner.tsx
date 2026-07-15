"use client";

import { useEffect, useState } from "react";
import { CloudOff } from "lucide-react";
import { useSyncQueue } from "@/features/offline/sync-queue";

export function OfflineBanner() {
  const [online, setOnline] = useState(() =>
    typeof navigator !== "undefined" ? navigator.onLine : true,
  );
  const { queueSize, syncing } = useSyncQueue();
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const onOnline = () => {
      setOnline(true);
      setDismissed(false);
    };
    const onOffline = () => {
      setOnline(false);
      setDismissed(false);
    };
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  if (online || dismissed) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-amber-500 text-amber-950 px-4 py-2 text-sm">
      <div className="max-w-screen-xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CloudOff className="h-4 w-4" />
          <span className="font-medium">You are offline</span>
          {queueSize > 0 && (
            <span className="text-xs opacity-80">
              {syncing ? `Syncing ${queueSize} item${queueSize > 1 ? "s" : ""}...` : `${queueSize} item${queueSize > 1 ? "s" : ""} will sync when online`}
            </span>
          )}
        </div>
        <button
          onClick={() => setDismissed(true)}
          className="text-xs underline opacity-80 hover:opacity-100"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
