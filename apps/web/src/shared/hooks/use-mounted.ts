"use client";

import { useEffect, useState } from "react";

/** Avoids hydration mismatches for client-only UI (e.g. theme). */
export function useMounted(): boolean {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => {
      setMounted(true);
    });
    return () => cancelAnimationFrame(id);
  }, []);
  return mounted;
}
