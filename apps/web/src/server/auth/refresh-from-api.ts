import { internalApiBaseUrl } from "@/server/auth/internal-api-base";

import type { TokenBundle } from "./auth-cookies";

/** Server-side refresh call (BFF / middleware); forwards User-Agent when provided. */
export async function refreshTokensFromApi(
  refreshToken: string,
  userAgent: string | null,
): Promise<TokenBundle | null> {
  const base = internalApiBaseUrl();
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (userAgent) headers["User-Agent"] = userAgent;
    const res = await fetch(`${base}/v1/auth/refresh`, {
      method: "POST",
      headers,
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    });
    if (!res.ok) return null;
    const data = (await res.json()) as Partial<TokenBundle>;
    if (
      typeof data.access_token !== "string" ||
      typeof data.refresh_token !== "string" ||
      typeof data.expires_in !== "number"
    ) {
      return null;
    }
    return {
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      expires_in: data.expires_in,
    };
  } catch {
    return null;
  }
}
