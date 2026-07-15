import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { getPublicEnv } from "./env";

describe("getPublicEnv", () => {
  beforeEach(() => {
    vi.stubEnv("NEXT_PUBLIC_APP_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "");
  });

  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("uses safe defaults when optional vars are absent", () => {
    const env = getPublicEnv();
    expect(env.NEXT_PUBLIC_APP_ENV).toBe("development");
  });
});
