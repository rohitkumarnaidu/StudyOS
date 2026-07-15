import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import {
  STUDYOS_ACCESS_COOKIE,
  STUDYOS_REFRESH_COOKIE,
  STUDYOS_SESSION_COOKIE,
} from "@/features/auth/constants";
import { PROTECTED_ROUTE_PREFIXES } from "@/shared/config/routes";
import { applyAuthCookies } from "@/server/auth/auth-cookies";
import { refreshTokensFromApi } from "@/server/auth/refresh-from-api";
import { verifyStudyosAccessJwt } from "@/server/auth/verify-access-jwt";
import { isSupabaseEdgeConfigured } from "@/server/supabase/env-edge";
import { updateSupabaseSession } from "@/server/supabase/middleware";

function forwardCookies(from: NextResponse, to: NextResponse) {
  for (const c of from.cookies.getAll()) {
    to.cookies.set(c.name, c.value);
  }
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const { response: baseResponse, user: supabaseUser } = isSupabaseEdgeConfigured()
    ? await updateSupabaseSession(request)
    : { response: NextResponse.next({ request }), user: null };

  const needsAuth = PROTECTED_ROUTE_PREFIXES.some((prefix) => pathname.startsWith(prefix));
  if (!needsAuth) {
    return baseResponse;
  }

  const access = request.cookies.get(STUDYOS_ACCESS_COOKIE)?.value;
  if (access) {
    const claims = await verifyStudyosAccessJwt(access);
    if (claims) return baseResponse;
  }

  if (request.cookies.get(STUDYOS_SESSION_COOKIE)?.value) {
    return baseResponse;
  }

  const refresh = request.cookies.get(STUDYOS_REFRESH_COOKIE)?.value;
  if (refresh) {
    const ua = request.headers.get("user-agent");
    const tokens = await refreshTokensFromApi(refresh, ua);
    if (tokens) {
      applyAuthCookies(baseResponse, tokens);
      return baseResponse;
    }
  }

  if (supabaseUser) {
    return baseResponse;
  }

  const login = new URL("/login", request.url);
  login.searchParams.set("next", pathname);
  const redirectRes = NextResponse.redirect(login);
  forwardCookies(baseResponse, redirectRes);
  return redirectRes;
}

export const config = {
  matcher: [
    /*
     * Run on all paths except static assets so Supabase auth cookies refresh.
     * StudyOS JWT checks still apply only when `needsAuth` is true.
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
