import type { NextResponse } from "next/server";

import {
  STUDYOS_ACCESS_COOKIE,
  STUDYOS_REFRESH_COOKIE,
  STUDYOS_SESSION_COOKIE,
} from "@/features/auth/constants";

const DEFAULT_REFRESH_MAX_AGE = 60 * 60 * 24 * 7; // 604800s — align with API default refresh TTL

function refreshCookieMaxAge(): number {
  const raw = process.env.STUDYOS_REFRESH_COOKIE_MAX_AGE;
  if (!raw) return DEFAULT_REFRESH_MAX_AGE;
  const n = Number.parseInt(raw, 10);
  return Number.isFinite(n) && n > 60 ? n : DEFAULT_REFRESH_MAX_AGE;
}

function baseCookieOptions(): {
  httpOnly: boolean;
  sameSite: "lax";
  path: string;
  secure: boolean;
} {
  const isProd = process.env.NODE_ENV === "production";
  return {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: isProd,
  };
}

export type TokenBundle = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
};

export function applyAuthCookies(res: NextResponse, tokens: TokenBundle) {
  const base = baseCookieOptions();
  res.cookies.set(STUDYOS_ACCESS_COOKIE, tokens.access_token, {
    ...base,
    maxAge: tokens.expires_in,
  });
  res.cookies.set(STUDYOS_REFRESH_COOKIE, tokens.refresh_token, {
    ...base,
    maxAge: refreshCookieMaxAge(),
  });
}

export function clearAuthCookies(res: NextResponse) {
  const base = baseCookieOptions();
  for (const name of [STUDYOS_ACCESS_COOKIE, STUDYOS_REFRESH_COOKIE, STUDYOS_SESSION_COOKIE]) {
    res.cookies.set(name, "", { ...base, maxAge: 0 });
  }
}
