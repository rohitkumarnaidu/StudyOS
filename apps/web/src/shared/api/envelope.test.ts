import { describe, expect, it } from "vitest";

import { isApiSuccessEnvelope, unwrapApiPayload } from "./envelope";

describe("isApiSuccessEnvelope", () => {
  it("detects StudyOS success envelope", () => {
    expect(isApiSuccessEnvelope({ success: true, data: { x: 1 } })).toBe(true);
  });

  it("rejects plain objects", () => {
    expect(isApiSuccessEnvelope({ status: "ok" })).toBe(false);
    expect(isApiSuccessEnvelope(null)).toBe(false);
  });
});

describe("unwrapApiPayload", () => {
  it("unwraps data when envelope present", () => {
    expect(unwrapApiPayload<{ x: number }>({ success: true, data: { x: 2 } })).toEqual({ x: 2 });
  });

  it("passes through non-envelope JSON", () => {
    expect(unwrapApiPayload({ status: "ok" })).toEqual({ status: "ok" });
  });
});
