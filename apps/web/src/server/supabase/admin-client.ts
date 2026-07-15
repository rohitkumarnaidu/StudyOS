import "server-only";

import { createClient } from "@supabase/supabase-js";

/**
 * Service-role client (bypasses RLS). Use only in trusted server code.
 * Returns null if `SUPABASE_SERVICE_ROLE_KEY` is unset.
 */
export function createSupabaseServiceRoleClient() {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"]?.trim();
  const serviceKey = process.env["SUPABASE_SERVICE_ROLE_KEY"]?.trim();
  if (!url || !serviceKey) return null;

  return createClient(url, serviceKey, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });
}
