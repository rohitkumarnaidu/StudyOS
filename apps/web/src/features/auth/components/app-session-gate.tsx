"use client";

import type { ReactNode } from "react";
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useSession } from "@/features/auth/session-provider";
import { Spinner } from "@/shared/components/ui/spinner";
import { VisuallyHidden } from "@/shared/components/ui/visually-hidden";
import { loginUrlWithNext } from "@/shared/lib/safe-next-path";

export function AppSessionGate({ children }: { children: ReactNode }) {
  const { authenticated, loading, refresh } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const onFocus = () => {
      void refresh();
    };
    window.addEventListener("focus", onFocus);
    return () => window.removeEventListener("focus", onFocus);
  }, [refresh]);

  useEffect(() => {
    if (loading) return;
    if (!authenticated) {
      router.replace(loginUrlWithNext(pathname));
    }
  }, [authenticated, loading, pathname, router]);

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center py-24" role="status" aria-live="polite">
        <Spinner className="size-8" aria-hidden />
        <VisuallyHidden>Loading session</VisuallyHidden>
      </div>
    );
  }

  if (!authenticated) {
    return null;
  }

  return children;
}
