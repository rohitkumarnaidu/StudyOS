import { QueryClient } from "@tanstack/react-query";

const isDev = process.env.NODE_ENV === "development";

/** Default query options for different data types */
const QUERY_PRESETS = {
  // Static data (syllabus, subjects, exams) — rarely changes
  static: {
    staleTime: 30 * 60 * 1000,    // 30 minutes
    gcTime: 60 * 60 * 1000,       // 1 hour
  },
  // User data (progress, streaks) — changes occasionally
  userData: {
    staleTime: 5 * 60 * 1000,     // 5 minutes
    gcTime: 15 * 60 * 1000,       // 15 minutes
  },
  // Real-time data (chat, quiz) — needs fresh data
  realtime: {
    staleTime: 0,                 // Always stale
    gcTime: 5 * 60 * 1000,        // 5 minutes
  },
} as const;

/** Browser QueryClient — one per tab; created in `AppProviders` via `useState`. */
export function createBrowserQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        /** Longer stale window reduces duplicate fetches for enterprise dashboards. */
        staleTime: 120_000,
        gcTime: 10 * 60_000,
        retry: 1,
        /** In production, avoid refetch storms on every tab focus (dev keeps fast feedback). */
        refetchOnWindowFocus: isDev,
        refetchOnReconnect: true,
        networkMode: "online",
      },
      mutations: {
        retry: 0,
      },
    },
  });
}

/** Get query options for static data (syllabus, subjects, exams) */
export function staticQueryOptions<T = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<T>
) {
  return {
    queryKey,
    queryFn,
    ...QUERY_PRESETS.static,
    refetchOnWindowFocus: false,
  };
}

/** Get query options for user data (progress, streaks) */
export function userDataQueryOptions<T = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<T>
) {
  return {
    queryKey,
    queryFn,
    ...QUERY_PRESETS.userData,
    refetchOnWindowFocus: true,
  };
}

/** Get query options for real-time data (chat, quiz) */
export function realtimeQueryOptions<T = unknown>(
  queryKey: readonly unknown[],
  queryFn: () => Promise<T>
) {
  return {
    queryKey,
    queryFn,
    ...QUERY_PRESETS.realtime,
    refetchOnWindowFocus: false,
  };
}

/** Prefetch helper for static data */
export async function prefetchStatic<T>(
  client: QueryClient,
  queryKey: readonly unknown[],
  queryFn: () => Promise<T>
) {
  return client.prefetchQuery(staticQueryOptions(queryKey, queryFn));
}
