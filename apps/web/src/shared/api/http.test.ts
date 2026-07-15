import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { apiFetch, ApiError } from "@/shared/api/http";

const mockFetch = vi.fn();

vi.stubGlobal("fetch", mockFetch);

vi.mock("@/shared/config/env", () => ({
  getPublicEnv: () => ({
    NEXT_PUBLIC_APP_ENV: "test",
    NEXT_PUBLIC_API_BASE_URL: "http://localhost:8000",
  }),
}));

describe("apiFetch", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("fetches JSON with correct headers", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      text: () => Promise.resolve(JSON.stringify({ success: true, data: { id: 1 } })),
    });

    const result = await apiFetch<{ id: number }>("/v1/test");
    expect(result).toEqual({ id: 1 });
    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/v1/test",
      expect.objectContaining({
        headers: expect.any(Headers),
        credentials: "include",
      }),
    );
  });

  it("throws ApiError on non-ok response", async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "Not Found",
      text: () => Promise.resolve(JSON.stringify({ error: "not found" })),
    });

    await expect(apiFetch("/v1/missing")).rejects.toThrow(ApiError);
    await expect(apiFetch("/v1/missing")).rejects.toMatchObject({
      status: 404,
      body: { error: "not found" },
    });
  });

  it("unwraps success envelope for v1 paths", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      text: () => Promise.resolve(JSON.stringify({ success: true, data: { name: "test" } })),
    });

    const result = await apiFetch<{ name: string }>("/v1/items");
    expect(result).toEqual({ name: "test" });
  });

  it("does not unwrap for non-versioned paths", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      text: () => Promise.resolve(JSON.stringify({ raw: true })),
    });

    const result = await apiFetch<{ raw: boolean }>("/api/health", { unwrapEnvelope: false });
    expect(result).toEqual({ raw: true });
  });

  it("serializes body as JSON", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      text: () => Promise.resolve(JSON.stringify({ ok: true })),
    });

    await apiFetch("/v1/items", {
      method: "POST",
      body: { name: "new item" },
    });

    const callArgs = mockFetch.mock.calls[0];
    expect(callArgs[1].body).toBe(JSON.stringify({ name: "new item" }));
    expect(callArgs[1].headers.get("Content-Type")).toBe("application/json");
  });

  it("handles plain text error responses", async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      status: 500,
      text: () => Promise.resolve("Internal Server Error"),
    });

    await expect(apiFetch("/v1/broken")).rejects.toThrow(ApiError);
  });

  it("handles empty response body", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      status: 204,
      text: () => Promise.resolve(""),
    });

    const result = await apiFetch<void>("/v1/no-content");
    expect(result).toBeUndefined();
  });
});

describe("ApiError", () => {
  it("extends Error with status and body", () => {
    const err = new ApiError("Not Found", 404, { detail: "missing" });
    expect(err).toBeInstanceOf(Error);
    expect(err.name).toBe("ApiError");
    expect(err.status).toBe(404);
    expect(err.body).toEqual({ detail: "missing" });
    expect(err.message).toBe("Not Found");
  });
});
