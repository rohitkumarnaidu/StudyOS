import { renderHook } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

import { useMediaQuery } from "./use-media-query";

describe("useMediaQuery", () => {
  const mockMatchMedia = (matches: boolean) => {
    const mql: Partial<MediaQueryList> = {
      matches,
      media: "(min-width: 768px)",
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      onchange: null,
    };

    vi.stubGlobal("matchMedia", vi.fn().mockReturnValue(mql));
    return mql;
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("returns false when query does not match", () => {
    mockMatchMedia(false);
    const { result } = renderHook(() => useMediaQuery("(min-width: 768px)"));
    expect(result.current).toBe(false);
  });

  it("returns true when query matches", () => {
    mockMatchMedia(true);
    const { result } = renderHook(() => useMediaQuery("(min-width: 768px)"));
    expect(result.current).toBe(true);
  });

  it("calls matchMedia with the provided query", () => {
    mockMatchMedia(true);
    renderHook(() => useMediaQuery("(max-width: 600px)"));
    expect(window.matchMedia).toHaveBeenCalledWith("(max-width: 600px)");
  });

  it("adds event listener for changes", () => {
    const mql = mockMatchMedia(false);
    renderHook(() => useMediaQuery("(min-width: 768px)"));
    expect(mql.addEventListener).toHaveBeenCalledWith("change", expect.any(Function));
  });

  it("removes event listener on unmount", () => {
    const mql = mockMatchMedia(false);
    const { unmount } = renderHook(() => useMediaQuery("(min-width: 768px)"));
    unmount();
    expect(mql.removeEventListener).toHaveBeenCalledWith("change", expect.any(Function));
  });
});
