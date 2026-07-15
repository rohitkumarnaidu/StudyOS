"use client";

import { useSyncQueue } from "@/features/offline/sync-queue";
import { CloudOff, Cloud, RefreshCw, Wifi } from "lucide-react";
import { useEffect, useState } from "react";

export function SyncIndicator() {
  const { queueSize, syncing, lastSynced } = useSyncQueue();
  const [online, setOnline] = useState(() =>
    typeof navigator !== "undefined" ? navigator.onLine : true,
  );

  useEffect(() => {
    const onOnline = () => setOnline(true);
    const onOffline = () => setOnline(false);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
    };
  }, []);

  if (!online && queueSize === 0) {
    return (
      <div className="flex items-center gap-1.5 rounded-md bg-amber-500/10 px-2 py-1 text-xs text-amber-600">
        <CloudOff className="h-3 w-3" />
        <span>Offline</span>
      </div>
    );
  }

  if (!online && queueSize > 0) {
    return (
      <div className="flex items-center gap-1.5 rounded-md bg-amber-500/10 px-2 py-1 text-xs text-amber-600">
        <CloudOff className="h-3 w-3" />
        <span>{queueSize} pending</span>
      </div>
    );
  }

  if (syncing) {
    return (
      <div className="flex items-center gap-1.5 rounded-md bg-blue-500/10 px-2 py-1 text-xs text-blue-600">
        <RefreshCw className="h-3 w-3 animate-spin" />
        <span>Syncing...</span>
      </div>
    );
  }

  if (queueSize > 0) {
    return (
      <div className="flex items-center gap-1.5 rounded-md bg-emerald-500/10 px-2 py-1 text-xs text-emerald-600">
        <Cloud className="h-3 w-3" />
        <span>{queueSize} to sync</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-muted-foreground">
      <Wifi className="h-3 w-3" />
      {lastSynced && <span>Synced {lastSynced.toLocaleTimeString()}</span>}
    </div>
  );
}
