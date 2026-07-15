"use client";

import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

export function isSupabaseBrowserConfigured(): boolean {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"]?.trim();
  const key = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"]?.trim();
  return Boolean(url && key);
}

/** Browser client for RLS-backed reads/writes. Returns null if env is incomplete. */
export function createSupabaseBrowserClient(): SupabaseClient | null {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"]?.trim();
  const key = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"]?.trim();
  if (!url || !key) return null;
  return createBrowserClient(url, key);
}
