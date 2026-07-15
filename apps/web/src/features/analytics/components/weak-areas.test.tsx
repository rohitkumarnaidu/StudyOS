import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { WeakAreas } from "./weak-areas";
import type { WeakArea } from "@/features/analytics/api";

afterEach(() => {
  cleanup();
});

const createWeakArea = (overrides: Partial<WeakArea> = {}): WeakArea => ({
  chapter_id: "ch-1",
  chapter_name: "Mechanics",
  subject_name: "Physics",
  progress_pct: 25,
  quiz_avg: 30,
  last_studied: null,
  priority: "high",
  ...overrides,
});

describe("WeakAreas", () => {
  it("renders empty state message", () => {
    render(<WeakAreas data={[]} />);
    expect(screen.getByText("No weak areas detected. Keep studying!")).toBeTruthy();
  });

  it("renders weak areas list", () => {
    render(<WeakAreas data={[createWeakArea()]} />);
    expect(screen.getByText("Mechanics")).toBeTruthy();
  });

  it("displays subject name", () => {
    render(<WeakAreas data={[createWeakArea()]} />);
    expect(screen.getByText("Physics")).toBeTruthy();
  });

  it("displays progress percentage", () => {
    render(<WeakAreas data={[createWeakArea()]} />);
    expect(screen.getByText("25%")).toBeTruthy();
  });

  it("displays quiz average", () => {
    render(<WeakAreas data={[createWeakArea()]} />);
    expect(screen.getByText("Quiz: 30%")).toBeTruthy();
  });

  it("hides quiz average when null", () => {
    render(<WeakAreas data={[createWeakArea({ quiz_avg: null })]} />);
    expect(screen.queryByText(/Quiz:/)).toBeFalsy();
  });

  it("renders multiple weak areas", () => {
    const areas = [
      createWeakArea({ chapter_id: "ch-1", chapter_name: "Mechanics", priority: "high" }),
      createWeakArea({ chapter_id: "ch-2", chapter_name: "Organic Chemistry", priority: "medium" }),
      createWeakArea({ chapter_id: "ch-3", chapter_name: "Genetics", priority: "low" }),
    ];
    render(<WeakAreas data={areas} />);
    expect(screen.getByText("Mechanics")).toBeTruthy();
    expect(screen.getByText("Organic Chemistry")).toBeTruthy();
    expect(screen.getByText("Genetics")).toBeTruthy();
  });

  it("limits display to 8 areas", () => {
    const areas = Array.from({ length: 10 }, (_, i) =>
      createWeakArea({ chapter_id: `ch-${i}`, chapter_name: `Chapter ${i}` })
    );
    render(<WeakAreas data={areas} />);
    const chapterNames = screen.getAllByText(/Chapter \d/);
    expect(chapterNames.length).toBeLessThanOrEqual(8);
  });

  it("renders with header", () => {
    render(<WeakAreas data={[createWeakArea()]} />);
    expect(screen.getByText("Areas to Improve")).toBeTruthy();
  });
});
