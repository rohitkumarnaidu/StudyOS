"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useSession } from "@/features/auth/session-provider";
import { ROUTES } from "@/shared/config/routes";
import { loginUrlWithNext } from "@/shared/lib/safe-next-path";

type UseRequireSessionOptions = {
  /** When redirecting to login, preserve the current destination (caller supplies pathname). */
  nextPath?: string;
};

/**
 * Client-side guard for authenticated views. Middleware already protects routes;
 * use this when a layout is shared or for progressive enhancement.
 */
export function useRequireSession(redirectTo = ROUTES.login, options?: UseRequireSessionOptions) {
  const { authenticated, loading } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!authenticated) {
      const target =
        redirectTo === ROUTES.login && options?.nextPath
          ? loginUrlWithNext(options.nextPath)
          : redirectTo;
      router.replace(target);
    }
  }, [authenticated, loading, options?.nextPath, redirectTo, router]);

  return { authenticated, loading };
}
