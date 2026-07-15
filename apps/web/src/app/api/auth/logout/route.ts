import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { STUDYOS_REFRESH_COOKIE } from "@/features/auth/constants";
import { clearAuthCookies } from "@/server/auth/auth-cookies";
import { internalApiBaseUrl } from "@/server/auth/internal-api-base";

export async function POST() {
  const jar = await cookies();
  const refresh = jar.get(STUDYOS_REFRESH_COOKIE)?.value;

  if (refresh) {
    const base = internalApiBaseUrl();
    try {
      await fetch(`${base}/v1/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
        cache: "no-store",
      });
    } catch {
      /* still clear cookies client-side */
    }
  }

  const res = NextResponse.json({ ok: true });
  clearAuthCookies(res);
  return res;
}
