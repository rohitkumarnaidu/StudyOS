import { NextResponse } from "next/server";

import { createSupabaseRouteHandlerClient } from "@/server/supabase/server-client";
import { ROUTES } from "@/shared/config/routes";
import { safeNextPath } from "@/shared/lib/safe-next-path";

/**
 * Supabase OAuth (Google) PKCE callback — exchanges `code` for a session and sets cookies.
 * @see https://supabase.com/docs/guides/auth/server-side/nextjs
 */
export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const next = safeNextPath(url.searchParams.get("next"));
  const origin = url.origin;

  if (!code) {
    return NextResponse.redirect(`${origin}${ROUTES.login}?error=oauth`);
  }

  try {
    const supabase = await createSupabaseRouteHandlerClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (error) {
      return NextResponse.redirect(
        `${origin}${ROUTES.login}?error=oauth&message=${encodeURIComponent(error.message)}`,
      );
    }
    return NextResponse.redirect(`${origin}${next}`);
  } catch {
    return NextResponse.redirect(`${origin}${ROUTES.login}?error=oauth`);
  }
}
