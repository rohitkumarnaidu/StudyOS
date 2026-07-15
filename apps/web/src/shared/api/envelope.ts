/** Standard StudyOS API success envelope (FastAPI web app). */
export type ApiSuccessEnvelope<T> = {
  success: true;
  data: T;
  meta?: {
    request_id?: string | null;
    api_version?: string;
  };
};

export function isApiSuccessEnvelope(value: unknown): value is ApiSuccessEnvelope<unknown> {
  if (typeof value !== "object" || value === null) return false;
  const v = value as Record<string, unknown>;
  return v["success"] === true && "data" in v;
}

export function unwrapApiPayload<T>(value: unknown): T {
  if (isApiSuccessEnvelope(value)) {
    return value.data as T;
  }
  return value as T;
}
