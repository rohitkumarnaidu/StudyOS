import { describe, expect, it } from "vitest";

import { DEFAULT_LOGIN_REDIRECT } from "@/shared/config/routes";
import { loginUrlWithNext, safeNextPath } from "./safe-next-path";

describe("safeNextPath", () => {
  it("allows safe relative paths", () => {
    expect(safeNextPath("/courses/1")).toBe("/courses/1");
  });

  it("rejects protocol-relative and absolute URLs", () => {
    expect(safeNextPath("//evil.com")).toBe(DEFAULT_LOGIN_REDIRECT);
    expect(safeNextPath("https://evil.com")).toBe(DEFAULT_LOGIN_REDIRECT);
  });

  it("uses fallback when empty", () => {
    expect(safeNextPath(null)).toBe(DEFAULT_LOGIN_REDIRECT);
  });
});

describe("loginUrlWithNext", () => {
  it("builds login URL with encoded next", () => {
    expect(loginUrlWithNext("/dashboard")).toBe("/login?next=%2Fdashboard");
  });
});
