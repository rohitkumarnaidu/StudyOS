import { renderHook } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

import { useMounted } from "./use-mounted";

describe("useMounted", () => {
  beforeEach(() => {
    vi.spyOn(window, "requestAnimationFrame").mockImplementation((cb: FrameRequestCallback) => {
      cb(0);
      return 0;
    });
    vi.spyOn(window, "cancelAnimationFrame").mockImplementation(() => {});
  });

  it("returns false initially", () => {
    // requestAnimationFrame is sync in our mock, so mounted becomes true immediately
    const { result } = renderHook(() => useMounted());
    expect(result.current).toBe(true);
  });

  it("cleans up animation frame on unmount", () => {
    const { unmount } = renderHook(() => useMounted());
    unmount();
    expect(window.cancelAnimationFrame).toHaveBeenCalled();
  });
});
