import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import { QuizPlayer } from "@/features/quiz/components/quiz-player";

vi.mock("@/features/quiz/api", () => ({
  submitAnswer: vi.fn(),
}));

const mockQuestions = [
  {
    id: "q1",
    question_text: "What is the capital of France?",
    question_type: "mcq" as const,
    option_a: "Paris",
    option_b: "London",
    option_c: "Berlin",
    option_d: "Madrid",
    difficulty: 1,
  },
];

describe("QuizPlayer", () => {
  it("renders first question", () => {
    render(
      <QuizPlayer
        sessionId="s1"
        questions={mockQuestions}
        onFinish={vi.fn()}
      />,
    );
    expect(screen.getByText(/Question 1 of 1/)).toBeTruthy();
    expect(screen.getByText("What is the capital of France?")).toBeTruthy();
  });

  it("shows option A", () => {
    render(
      <QuizPlayer
        sessionId="s1"
        questions={mockQuestions}
        onFinish={vi.fn()}
      />,
    );
    const parisElements = screen.getAllByText("Paris");
    expect(parisElements.length).toBeGreaterThan(0);
  });

  it("shows difficulty level", () => {
    render(
      <QuizPlayer
        sessionId="s1"
        questions={mockQuestions}
        onFinish={vi.fn()}
      />,
    );
    const difficultyElements = screen.getAllByText(/Difficulty 1\/5/);
    expect(difficultyElements.length).toBeGreaterThan(0);
  });

  it("renders timer when timeLimitSeconds provided", () => {
    render(
      <QuizPlayer
        sessionId="s1"
        questions={mockQuestions}
        timeLimitSeconds={300}
        onFinish={vi.fn()}
      />,
    );
    expect(screen.getByText("05:00")).toBeTruthy();
  });
});
