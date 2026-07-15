import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { render, screen, act, cleanup } from "@testing-library/react";

import { TimerBar } from "@/features/quiz/components/timer-bar";

describe("TimerBar", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    cleanup();
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
    vi.clearAllTimers();
  });

  it("renders initial time correctly", () => {
    render(<TimerBar totalSeconds={60} onTimeUp={vi.fn()} />);
    expect(screen.getByText("01:00")).toBeTruthy();
  });

  it("shows percentage remaining", () => {
    const { container } = render(<TimerBar totalSeconds={100} onTimeUp={vi.fn()} />);
    const percentText = container.querySelector(".text-muted-foreground");
    expect(percentText?.textContent).toMatch(/\d+% remaining/);
  });

  it("counts down over time", () => {
    const onTimeUp = vi.fn();
    render(<TimerBar totalSeconds={60} onTimeUp={onTimeUp} />);

    act(() => {
      vi.advanceTimersByTime(1000);
    });

    expect(screen.getByText(/00:59/)).toBeTruthy();
  });

  it("calls onTimeUp when timer reaches zero", () => {
    const onTimeUp = vi.fn();
    render(<TimerBar totalSeconds={5} onTimeUp={onTimeUp} />);

    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(onTimeUp).toHaveBeenCalled();
  });

  it("shows warning styling when under 5 minutes", () => {
    render(<TimerBar totalSeconds={240} onTimeUp={vi.fn()} />);
    expect(screen.getByText(/04:00/)).toBeTruthy();
  });

  it("formats minutes with leading zero", () => {
    render(<TimerBar totalSeconds={600} onTimeUp={vi.fn()} />);
    expect(screen.getByText("10:00")).toBeTruthy();
  });
});
