import "server-only";

import type { SupabaseClient } from "@supabase/supabase-js";

export type PublicProfileRow = {
  id: string;
  email: string | null;
  display_name: string | null;
  app_role: string;
};

/** Loads `public.profiles` for the current Supabase user (RLS must allow `select`). */
export async function fetchProfileForAuthedUser(
  supabase: SupabaseClient,
  userId: string,
): Promise<PublicProfileRow | null> {
  const { data, error } = await supabase
    .from("profiles")
    .select("id, email, display_name, app_role")
    .eq("id", userId)
    .is("deleted_at", null)
    .maybeSingle();

  if (error || !data) return null;
  return data as PublicProfileRow;
}
