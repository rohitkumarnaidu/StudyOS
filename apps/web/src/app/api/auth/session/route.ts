import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import {
  STUDYOS_ACCESS_COOKIE,
  STUDYOS_SESSION_COOKIE,
} from "@/features/auth/constants";
import { verifyStudyosAccessJwt } from "@/server/auth/verify-access-jwt";
import { fetchProfileForAuthedUser } from "@/server/supabase/profile-read";
import { tryCreateSupabaseServerClient } from "@/server/supabase/server-client";

export type SessionAuthSource = "studyos" | "supabase" | "legacy" | "none";

export async function GET() {
  const jar = await cookies();
  let authenticated = false;
  let sub: string | undefined;
  let roles: string[] = [];
  let authSource: SessionAuthSource = "none";

  const access = jar.get(STUDYOS_ACCESS_COOKIE)?.value;
  if (access) {
    const claims = await verifyStudyosAccessJwt(access);
    if (claims) {
      authenticated = true;
      authSource = "studyos";
      sub = typeof claims.sub === "string" ? claims.sub : undefined;
      roles = Array.isArray(claims.roles)
        ? claims.roles.filter((r): r is string => typeof r === "string")
        : [];
    }
  }

  if (!authenticated) {
    const legacy = jar.get(STUDYOS_SESSION_COOKIE)?.value;
    if (legacy) {
      authenticated = true;
      authSource = "legacy";
    }
  }

  const supabase = await tryCreateSupabaseServerClient();
  const supabasePayload: {
    user: { id: string; email: string | null } | null;
    profile: Awaited<ReturnType<typeof fetchProfileForAuthedUser>>;
  } = { user: null, profile: null };

  if (supabase) {
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (user) {
      supabasePayload.user = { id: user.id, email: user.email ?? null };
      supabasePayload.profile = await fetchProfileForAuthedUser(supabase, user.id);
      if (!authenticated) {
        authenticated = true;
        authSource = "supabase";
        sub = user.id;
        const role = supabasePayload.profile?.app_role;
        roles = role ? [role] : [];
      }
    }
  }

  return NextResponse.json({
    authenticated,
    sub,
    roles,
    authSource,
    supabase: supabasePayload,
  });
}
