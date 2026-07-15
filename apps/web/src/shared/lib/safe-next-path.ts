import { DEFAULT_LOGIN_REDIRECT, ROUTES } from "@/shared/config/routes";

/**
 * Sanitize `next` query values to prevent open redirects (only same-origin relative paths).
 */
export function safeNextPath(raw: string | null | undefined, fallback = DEFAULT_LOGIN_REDIRECT): string {
  if (!raw || typeof raw !== "string") return fallback;
  const trimmed = raw.trim();
  if (!trimmed.startsWith("/") || trimmed.startsWith("//") || trimmed.includes("://")) {
    return fallback;
  }
  return trimmed;
}

export function loginUrlWithNext(nextPath: string): string {
  const safe = safeNextPath(nextPath);
  const url = new URL(ROUTES.login, "http://local.invalid");
  url.searchParams.set("next", safe);
  return `${ROUTES.login}?${url.searchParams.toString()}`;
}
