import "server-only";

import { createServerClient, type CookieOptions } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";

/** Server Components / Route Handlers — respects RLS for the signed-in user. */
export async function createSupabaseServerClient(): Promise<SupabaseClient> {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"]?.trim();
  const anonKey = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"]?.trim();
  if (!url || !anonKey) {
    throw new Error(
      "Supabase is not configured: set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY",
    );
  }

  const cookieStore = await cookies();

  return createServerClient(url, anonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
        try {
          cookiesToSet.forEach(({ name, value, options }) => {
            cookieStore.set(name, value, options);
          });
        } catch {
          /* called from a Server Component that cannot mutate cookies */
        }
      },
    },
  });
}

export async function tryCreateSupabaseServerClient(): Promise<SupabaseClient | null> {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"]?.trim();
  const anonKey = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"]?.trim();
  if (!url || !anonKey) return null;
  return createSupabaseServerClient();
}

/**
 * Route Handlers that **must** persist auth cookies (OAuth callback). Server Components
 * use `createSupabaseServerClient` instead (cookie writes may be no-ops there).
 */
export async function createSupabaseRouteHandlerClient(): Promise<SupabaseClient> {
  const url = process.env["NEXT_PUBLIC_SUPABASE_URL"]?.trim();
  const anonKey = process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"]?.trim();
  if (!url || !anonKey) {
    throw new Error(
      "Supabase is not configured: set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY",
    );
  }

  const cookieStore = await cookies();

  return createServerClient(url, anonKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
        cookiesToSet.forEach(({ name, value, options }) => {
          cookieStore.set(name, value, options);
        });
      },
    },
  });
}
