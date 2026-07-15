"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import type { SupabaseClient } from "@supabase/supabase-js";

import { createSupabaseBrowserClient } from "@/shared/lib/supabase/browser-client";

const SupabaseClientContext = createContext<SupabaseClient | null>(null);

/** Supabase browser client when `NEXT_PUBLIC_SUPABASE_*` is set; otherwise null. */
export function useSupabaseOptional(): SupabaseClient | null {
  return useContext(SupabaseClientContext);
}

export function SupabaseBrowserProvider({ children }: { children: ReactNode }) {
  const client = useMemo(() => createSupabaseBrowserClient(), []);
  return <SupabaseClientContext.Provider value={client}>{children}</SupabaseClientContext.Provider>;
}
