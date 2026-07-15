import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

import { MistakeLog } from "@/features/quiz/components/mistake-log";
import * as quizApi from "@/features/quiz/api";

vi.mock("@/features/quiz/api", () => ({
  listMistakes: vi.fn(),
  reviewMistake: vi.fn(),
  deleteMistake: vi.fn(),
}));

const mockMistakes = [
  {
    id: "m1",
    question_id: "q1",
    question_text: "What is the speed of light?",
    user_answer: "A",
    correct_answer: "C",
    is_correct: false,
    explanation: "The speed of light is 3 x 10^8 m/s.",
    reviewed: false,
    review_count: 0,
    created_at: "2026-01-01T00:00:00Z",
  },
];

describe("MistakeLog", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state", () => {
    vi.mocked(quizApi.listMistakes).mockReturnValue(new Promise(() => {}));
    render(<MistakeLog />);
    expect(screen.getByText("Loading mistakes...")).toBeTruthy();
  });

  it("shows empty state", async () => {
    vi.mocked(quizApi.listMistakes).mockResolvedValue([]);
    render(<MistakeLog />);
    await waitFor(() => {
      expect(screen.getByText("No mistakes logged. Keep practicing!")).toBeTruthy();
    });
  });

  it("displays mistake questions", async () => {
    vi.mocked(quizApi.listMistakes).mockResolvedValue(mockMistakes);
    render(<MistakeLog />);
    await waitFor(() => {
      expect(screen.getByText("What is the speed of light?")).toBeTruthy();
    });
  });

  it("shows correct answer", async () => {
    vi.mocked(quizApi.listMistakes).mockResolvedValue(mockMistakes);
    render(<MistakeLog />);
    await waitFor(() => {
      expect(screen.getByText("C")).toBeTruthy();
    });
  });
});
