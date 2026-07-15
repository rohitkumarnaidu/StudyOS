"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  startTransition,
} from "react";

type SessionState = {
  authenticated: boolean;
  loading: boolean;
  refresh: () => Promise<void>;
};

const SessionContext = createContext<SessionState | null>(null);

/** Coalesce concurrent session probes (Strict Mode + multiple layouts). */
let sessionInflight: Promise<boolean> | null = null;

async function fetchSession(): Promise<boolean> {
  if (sessionInflight === null) {
    sessionInflight = (async () => {
      const res = await fetch("/api/auth/session", {
        credentials: "include",
        cache: "no-store",
      });
      if (!res.ok) {
        return false;
      }
      const data = (await res.json()) as { authenticated?: boolean };
      return Boolean(data.authenticated);
    })().finally(() => {
      sessionInflight = null;
    });
  }
  return sessionInflight;
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      setAuthenticated(await fetchSession());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    startTransition(() => {
      void refresh();
    });
  }, [refresh]);

  const value = useMemo(
    () => ({ authenticated, loading, refresh }),
    [authenticated, loading, refresh],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): SessionState {
  const ctx = useContext(SessionContext);
  if (!ctx) {
    throw new Error("useSession must be used within SessionProvider");
  }
  return ctx;
}
