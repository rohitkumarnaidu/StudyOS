/** Extract a human-readable message from API problem bodies (FastAPI RFC7807-style, etc.). */
export function pickProblemMessage(body: unknown): string | undefined {
  if (!body || typeof body !== "object") return undefined;
  const o = body as Record<string, unknown>;
  if (typeof o.detail === "string") return o.detail;
  if (typeof o.title === "string") return o.title;
  if (typeof o.error === "string") return o.error;
  return undefined;
}
