import { unwrapApiPayload } from "@/shared/api/envelope";
import { getPublicEnv } from "@/shared/config/env";

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

type FetchJsonInit = Omit<RequestInit, "body"> & { body?: unknown };

export type ApiFetchOptions = FetchJsonInit & {
  /**
   * When true, unwrap `{ success: true, data }` payloads from the StudyOS API.
   * Default: on for `/v1/*` and `/v2/*` paths (versioned JSON).
   */
  unwrapEnvelope?: boolean;
};

function pathnameKey(path: string): string {
  if (path.startsWith("http")) {
    try {
      return new URL(path).pathname;
    } catch {
      return path;
    }
  }
  return path.startsWith("/") ? path.split("?")[0] ?? path : `/${path}`;
}

function inferUnwrapEnvelope(path: string): boolean {
  const p = pathnameKey(path);
  return p.startsWith("/v1/") || p.startsWith("/v2/") || p === "/v1" || p === "/v2";
}

/**
 * Typed JSON fetch against the configured API base (or same-origin relative paths).
 */
export async function apiFetch<T>(path: string, init: ApiFetchOptions = {}): Promise<T> {
  const { unwrapEnvelope, ...fetchInit } = init;
  const env = getPublicEnv();
  const base = env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "";
  const url = path.startsWith("http") ? path : `${base}${path.startsWith("/") ? "" : "/"}${path}`;
  const headers = new Headers(fetchInit.headers);
  if (fetchInit.body !== undefined && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(url, {
    ...fetchInit,
    headers,
    body: fetchInit.body === undefined ? undefined : JSON.stringify(fetchInit.body),
    credentials: "include",
  });
  const text = await res.text();
  let json: unknown = undefined;
  if (text) {
    try {
      json = JSON.parse(text) as unknown;
    } catch {
      json = text;
    }
  }
  if (!res.ok) {
    throw new ApiError(res.statusText || "Request failed", res.status, json);
  }
  const unwrap = unwrapEnvelope ?? inferUnwrapEnvelope(path);
  const payload = unwrap ? unwrapApiPayload<T>(json) : (json as T);
  return payload;
}
