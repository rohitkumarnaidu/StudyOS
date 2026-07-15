export { assertDefined } from "./utils/invariant";

export const APP_NAME = "StudyOS";

export type HealthSource = string;

export function healthPayload(source: HealthSource) {
  return {
    ok: true as const,
    source,
    at: new Date().toISOString(),
  };
}
