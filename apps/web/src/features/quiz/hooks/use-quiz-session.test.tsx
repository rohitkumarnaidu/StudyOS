import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act } from "react";

import * as quizApi from "@/features/quiz/api";
import { useQuizSession } from "@/features/quiz/hooks/use-quiz-session";

vi.mock("@/features/quiz/api", () => ({
  getQuizQuestions: vi.fn(),
  finishQuizSession: vi.fn(),
  getQuizResult: vi.fn(),
}));

vi.mock("@/shared/lib", () => ({
  notifyError: vi.fn(),
}));

function createWrapper() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
  }
  Wrapper.displayName = "QueryClientWrapper";
  return Wrapper;
}

describe("useQuizSession", () => {
  const mockQuestions = [
    { id: "q1", question_text: "What is 2+2?", question_type: "mcq" as const, option_a: "3", option_b: "4", option_c: "5", option_d: "6", difficulty: 1 },
    { id: "q2", question_text: "What is 3*3?", question_type: "mcq" as const, option_a: "6", option_b: "9", option_c: "12", option_d: "15", difficulty: 1 },
  ];

  const mockResult = {
    session_id: "s1",
    total_questions: 2,
    correct: 1,
    incorrect: 0,
    skipped: 1,
    score_percent: 50,
    time_taken_seconds: 120,
    responses: [],
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("loads questions on mount", async () => {
    vi.mocked(quizApi.getQuizQuestions).mockResolvedValue(mockQuestions);

    const { result } = renderHook(() => useQuizSession("s1", "practice"), {
      wrapper: createWrapper(),
    });

    expect(result.current.loading).toBe(true);

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.questions).toHaveLength(2);
  });

  it("handles load failure gracefully", async () => {
    vi.mocked(quizApi.getQuizQuestions).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useQuizSession("s1", "practice"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.questions).toHaveLength(0);
  });

  it("finishes quiz and sets result", async () => {
    vi.mocked(quizApi.getQuizQuestions).mockResolvedValue(mockQuestions);
    vi.mocked(quizApi.finishQuizSession).mockResolvedValue(mockResult);

    const { result } = renderHook(() => useQuizSession("s1", "practice"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.handleFinish();
    });

    expect(result.current.finished).toBe(true);
    expect(result.current.result).toEqual(mockResult);
  });

  it("loads existing result", async () => {
    vi.mocked(quizApi.getQuizResult).mockResolvedValue(mockResult);

    const { result } = renderHook(() => useQuizSession("s1", "practice"), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.loadResult();
    });

    expect(result.current.finished).toBe(true);
    expect(result.current.result).toEqual(mockResult);
  });
});
