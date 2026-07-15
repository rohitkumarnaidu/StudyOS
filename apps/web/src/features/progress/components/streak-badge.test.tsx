import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { StreakBadge } from "@/features/progress/components/streak-badge";

describe("StreakBadge", () => {
  it("renders current streak", () => {
    render(<StreakBadge currentStreak={5} longestStreak={5} />);
    expect(screen.getByText("5 days")).toBeTruthy();
  });

  it("returns null when streak is 0", () => {
    const { container } = render(<StreakBadge currentStreak={0} longestStreak={0} />);
    expect(container.firstChild).toBeNull();
  });

  it("shows singular 'day' for streak of 1", () => {
    render(<StreakBadge currentStreak={1} longestStreak={1} />);
    expect(screen.getByText("1 day")).toBeTruthy();
  });

  it("shows best streak when longest > current", () => {
    render(<StreakBadge currentStreak={3} longestStreak={10} />);
    expect(screen.getByText("(best: 10)")).toBeTruthy();
  });

  it("hides best streak when current equals longest", () => {
    const { container } = render(<StreakBadge currentStreak={7} longestStreak={7} />);
    expect(container.querySelector(".text-muted-foreground")).toBeNull();
  });

  it("applies milestone animation at 7 days", () => {
    const { container } = render(<StreakBadge currentStreak={7} longestStreak={7} />);
    const badge = container.firstChild;
    expect(badge).toHaveClass("animate-pulse");
  });

  it("applies milestone animation at 14 days", () => {
    const { container } = render(<StreakBadge currentStreak={14} longestStreak={14} />);
    const badge = container.firstChild;
    expect(badge).toHaveClass("animate-pulse");
  });

  it("no milestone animation at non-multiple of 7", () => {
    const { container } = render(<StreakBadge currentStreak={5} longestStreak={5} />);
    const badge = container.firstChild;
    expect(badge).not.toHaveClass("animate-pulse");
  });

  it("supports small size", () => {
    const { container } = render(<StreakBadge currentStreak={3} longestStreak={3} size="sm" />);
    const badge = container.firstChild;
    expect(badge).toHaveClass("px-2", "py-1");
  });

  it("supports large size", () => {
    const { container } = render(<StreakBadge currentStreak={3} longestStreak={3} size="lg" />);
    const badge = container.firstChild;
    expect(badge).toHaveClass("px-4", "py-2");
  });

  it("applies custom className", () => {
    const { container } = render(<StreakBadge currentStreak={3} longestStreak={3} className="custom" />);
    const badge = container.firstChild;
    expect(badge).toHaveClass("custom");
  });
});
