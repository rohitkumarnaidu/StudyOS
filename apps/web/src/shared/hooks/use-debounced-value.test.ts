import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import { useDebouncedValue } from "./use-debounced-value";

describe("useDebouncedValue", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  it("returns initial value immediately", () => {
    const { result } = renderHook(() => useDebouncedValue("initial", 100));
    expect(result.current).toBe("initial");
  });

  it("updates value after delay", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebouncedValue(value, delay),
      { initialProps: { value: "first", delay: 100 } }
    );

    expect(result.current).toBe("first");

    rerender({ value: "second", delay: 100 });

    // Value should still be "first" before delay
    expect(result.current).toBe("first");

    // Advance timers past the delay
    act(() => {
      vi.advanceTimersByTime(100);
    });

    expect(result.current).toBe("second");
  });

  it("resets timer on value change", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebouncedValue(value, delay),
      { initialProps: { value: "first", delay: 200 } }
    );

    rerender({ value: "second", delay: 200 });

    // Advance only half the delay
    act(() => {
      vi.advanceTimersByTime(100);
    });

    // Change value again before delay completes
    rerender({ value: "third", delay: 200 });

    // Should still be "first" because timer was reset
    expect(result.current).toBe("first");

    // Advance full delay from last change
    act(() => {
      vi.advanceTimersByTime(200);
    });

    expect(result.current).toBe("third");
  });

  it("uses custom delay", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebouncedValue(value, delay),
      { initialProps: { value: "first", delay: 500 } }
    );

    rerender({ value: "second", delay: 500 });

    // Advance less than delay
    act(() => {
      vi.advanceTimersByTime(400);
    });

    expect(result.current).toBe("first");

    // Advance past delay
    act(() => {
      vi.advanceTimersByTime(100);
    });

    expect(result.current).toBe("second");
  });

  it("works with non-string values", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebouncedValue(value, delay),
      { initialProps: { value: { count: 1 }, delay: 100 } }
    );

    expect(result.current).toEqual({ count: 1 });

    rerender({ value: { count: 2 }, delay: 100 });

    act(() => {
      vi.advanceTimersByTime(100);
    });

    expect(result.current).toEqual({ count: 2 });
  });

  it("works with numeric values", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebouncedValue(value, delay),
      { initialProps: { value: 42, delay: 100 } }
    );

    expect(result.current).toBe(42);

    rerender({ value: 100, delay: 100 });

    act(() => {
      vi.advanceTimersByTime(100);
    });

    expect(result.current).toBe(100);
  });
});
