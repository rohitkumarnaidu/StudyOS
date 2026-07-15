import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";

import { QuizAnalytics } from "./quiz-analytics";

afterEach(() => {
  cleanup();
});

describe("QuizAnalytics", () => {
  it("renders empty state message", () => {
    render(<QuizAnalytics data={[]} />);
    expect(screen.getByText("No quiz data yet. Take a quiz to see your trends.")).toBeTruthy();
  });

  it("renders header with data", () => {
    render(
      <QuizAnalytics
        data={[
          { date: "2026-01-01", score: 75, question_count: 20 },
        ]}
      />
    );
    expect(screen.getByText("Quiz Performance")).toBeTruthy();
  });

  it("renders with single quiz result", () => {
    render(
      <QuizAnalytics
        data={[
          { date: "2026-01-01", score: 75, question_count: 20 },
        ]}
      />
    );
    expect(screen.getByText("Quiz Performance")).toBeTruthy();
  });

  it("renders with multiple quiz results", () => {
    render(
      <QuizAnalytics
        data={[
          { date: "2026-01-01", score: 60, question_count: 20 },
          { date: "2026-01-05", score: 70, question_count: 20 },
          { date: "2026-01-10", score: 85, question_count: 20 },
        ]}
      />
    );
    expect(screen.getByText("Quiz Performance")).toBeTruthy();
  });

  it("handles perfect score", () => {
    render(
      <QuizAnalytics
        data={[
          { date: "2026-01-01", score: 100, question_count: 20 },
        ]}
      />
    );
    expect(screen.getByText("Quiz Performance")).toBeTruthy();
  });

  it("handles zero score", () => {
    render(
      <QuizAnalytics
        data={[
          { date: "2026-01-01", score: 0, question_count: 20 },
        ]}
      />
    );
    expect(screen.getByText("Quiz Performance")).toBeTruthy();
  });
});
