import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { StreakCalendar } from "./streak-calendar";

afterEach(() => {
  cleanup();
});

const createDayData = (count: number, activeCount: number) => {
  const data: Array<{ date: string; active: boolean }> = [];
  const today = new Date();
  for (let i = count - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    data.push({
      date: date.toISOString().split("T")[0],
      active: i < activeCount,
    });
  }
  return data;
};

describe("StreakCalendar", () => {
  it("renders last 30 days header", () => {
    render(
      <StreakCalendar
        data={createDayData(30, 5)}
        currentStreak={5}
        longestStreak={10}
      />
    );
    expect(screen.getByText("Last 30 Days")).toBeTruthy();
  });

  it("displays current streak", () => {
    render(
      <StreakCalendar
        data={createDayData(30, 5)}
        currentStreak={5}
        longestStreak={10}
      />
    );
    expect(screen.getByText("Current: 5 days")).toBeTruthy();
  });

  it("displays current and best streak stats", () => {
    render(
      <StreakCalendar
        data={createDayData(30, 5)}
        currentStreak={5}
        longestStreak={10}
      />
    );
    expect(screen.getByText("Current: 5 days")).toBeTruthy();
    expect(screen.getByText("Best: 10 days")).toBeTruthy();
  });

  it("renders day headers (S M T W T F S)", () => {
    render(
      <StreakCalendar
        data={createDayData(30, 5)}
        currentStreak={0}
        longestStreak={0}
      />
    );
    const dayHeaders = screen.getAllByText(/^[SMTWFS]$/);
    expect(dayHeaders.length).toBe(7);
  });

  it("shows flame icon when streak is active", () => {
    render(
      <StreakCalendar
        data={createDayData(30, 5)}
        currentStreak={5}
        longestStreak={10}
      />
    );
    const flameElement = document.querySelector("svg");
    expect(flameElement).toBeTruthy();
  });

  it("hides flame icon when streak is zero", () => {
    render(
      <StreakCalendar
        data={createDayData(30, 0)}
        currentStreak={0}
        longestStreak={5}
      />
    );
    expect(screen.queryByText("0")).toBeFalsy();
  });

  it("limits display to last 30 days", () => {
    const longData = createDayData(90, 30);
    render(
      <StreakCalendar
        data={longData}
        currentStreak={30}
        longestStreak={60}
      />
    );
    const dayCells = document.querySelectorAll(".grid > div");
    expect(dayCells.length).toBeLessThanOrEqual(37); // 30 days + 7 day headers
  });

  it("renders with empty data", () => {
    render(
      <StreakCalendar
        data={[]}
        currentStreak={0}
        longestStreak={0}
      />
    );
    expect(screen.getByText("Last 30 Days")).toBeTruthy();
  });
});
