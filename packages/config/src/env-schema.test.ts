import { describe, expect, it } from "vitest";
import { isSupabaseConfigured, publicEnvSchema } from "./index";

describe("publicEnvSchema — Supabase pairing", () => {
  it("accepts both unset", () => {
    const r = publicEnvSchema.safeParse({
      NEXT_PUBLIC_APP_ENV: "development",
      NEXT_PUBLIC_SUPABASE_URL: undefined,
      NEXT_PUBLIC_SUPABASE_ANON_KEY: undefined,
    });
    expect(r.success).toBe(true);
    if (r.success) expect(isSupabaseConfigured(r.data)).toBe(false);
  });

  it("accepts empty string as unset", () => {
    const r = publicEnvSchema.safeParse({
      NEXT_PUBLIC_APP_ENV: "development",
      NEXT_PUBLIC_SUPABASE_URL: "",
      NEXT_PUBLIC_SUPABASE_ANON_KEY: "",
    });
    expect(r.success).toBe(true);
  });

  it("rejects URL without anon key", () => {
    const r = publicEnvSchema.safeParse({
      NEXT_PUBLIC_APP_ENV: "development",
      NEXT_PUBLIC_SUPABASE_URL: "https://abc.supabase.co",
      NEXT_PUBLIC_SUPABASE_ANON_KEY: undefined,
    });
    expect(r.success).toBe(false);
  });

  it("accepts both set", () => {
    const r = publicEnvSchema.safeParse({
      NEXT_PUBLIC_APP_ENV: "development",
      NEXT_PUBLIC_SUPABASE_URL: "https://abc.supabase.co",
      NEXT_PUBLIC_SUPABASE_ANON_KEY: "eyJhbGciOiJIUzI1NiJ9.test",
    });
    expect(r.success).toBe(true);
    if (r.success) expect(isSupabaseConfigured(r.data)).toBe(true);
  });
});
