import { describe, expect, it } from "vitest";

import { loginFormSchema, signupFormSchema } from "@/features/auth/schema";

describe("loginFormSchema", () => {
  it("accepts valid email and password", () => {
    const result = loginFormSchema.safeParse({
      email: "test@example.com",
      password: "secret123",
    });
    expect(result.success).toBe(true);
  });

  it("rejects invalid email", () => {
    const result = loginFormSchema.safeParse({
      email: "not-an-email",
      password: "secret123",
    });
    expect(result.success).toBe(false);
  });

  it("rejects empty password", () => {
    const result = loginFormSchema.safeParse({
      email: "test@example.com",
      password: "",
    });
    expect(result.success).toBe(false);
  });

  it("rejects email over 320 chars", () => {
    const result = loginFormSchema.safeParse({
      email: "a".repeat(315) + "@b.com",
      password: "secret",
    });
    expect(result.success).toBe(false);
  });

  it("rejects password over 256 chars", () => {
    const result = loginFormSchema.safeParse({
      email: "test@example.com",
      password: "x".repeat(257),
    });
    expect(result.success).toBe(false);
  });
});

describe("signupFormSchema", () => {
  it("accepts valid signup data", () => {
    const result = signupFormSchema.safeParse({
      email: "new@example.com",
      password: "securepass123",
      displayName: "Test User",
      terms: true,
    });
    expect(result.success).toBe(true);
  });

  it("rejects password shorter than 8 chars", () => {
    const result = signupFormSchema.safeParse({
      email: "new@example.com",
      password: "short",
      displayName: "Test User",
      terms: true,
    });
    expect(result.success).toBe(false);
  });

  it("rejects missing display name", () => {
    const result = signupFormSchema.safeParse({
      email: "new@example.com",
      password: "securepass123",
      displayName: "",
      terms: true,
    });
    expect(result.success).toBe(false);
  });

  it("rejects unchecked terms", () => {
    const result = signupFormSchema.safeParse({
      email: "new@example.com",
      password: "securepass123",
      displayName: "Test User",
      terms: false,
    });
    expect(result.success).toBe(false);
  });

  it("rejects display name over 100 chars", () => {
    const result = signupFormSchema.safeParse({
      email: "new@example.com",
      password: "securepass123",
      displayName: "x".repeat(101),
      terms: true,
    });
    expect(result.success).toBe(false);
  });
});
