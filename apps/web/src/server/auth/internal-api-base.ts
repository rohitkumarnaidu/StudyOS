/** Server-only FastAPI origin (never NEXT_PUBLIC_*). */
export function internalApiBaseUrl(): string {
  const raw = process.env.STUDYOS_INTERNAL_API_BASE_URL ?? "http://127.0.0.1:8000";
  return raw.replace(/\/$/, "");
}
