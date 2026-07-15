"use client";

import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/shared/api/http";
import { getPublicEnv } from "@/shared/config/env";

export const apiQueryKeys = {
  healthz: ["api", "v1", "healthz"] as const,
} as const;

/**
 * Example server-state hook: probes the FastAPI `/v1/healthz` when `NEXT_PUBLIC_API_BASE_URL` is set.
 */
export function useApiHealthz() {
  const enabled = Boolean(getPublicEnv().NEXT_PUBLIC_API_BASE_URL);
  return useQuery({
    queryKey: apiQueryKeys.healthz,
    queryFn: () => apiFetch<{ status: string }>("/v1/healthz"),
    enabled,
    staleTime: 120_000,
    gcTime: 15 * 60_000,
  });
}
