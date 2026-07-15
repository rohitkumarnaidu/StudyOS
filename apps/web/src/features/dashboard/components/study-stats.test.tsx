import { render, screen, cleanup } from "@testing-library/react";
import { describe, it, expect, afterEach, vi, beforeEach } from "vitest";
import type { Mock } from "vitest";

import { StudyStats } from "./study-stats";

afterEach(() => {
  cleanup();
});

vi.mock("@/features/progress/hooks/use-progress", () => ({
  useStreak: vi.fn(),
}));

const { useStreak } = await import("@/features/progress/hooks/use-progress");

beforeEach(() => {
  vi.clearAllMocks();
});

describe("StudyStats", () => {
  it("renders overall progress ring", () => {
    (useStreak as Mock).mockReturnValue({ data: null, isLoading: false });
    render(
      <StudyStats
        examProgress={50}
        chaptersCompleted={10}
        totalChapters={20}
        subtopicsCompleted={50}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText("Overall")).toBeTruthy();
  });

  it("displays chapter completion stats", () => {
    (useStreak as Mock).mockReturnValue({ data: null, isLoading: false });
    render(
      <StudyStats
        examProgress={50}
        chaptersCompleted={10}
        totalChapters={20}
        subtopicsCompleted={50}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText("Chapters")).toBeTruthy();
    expect(screen.getByText("10 / 20")).toBeTruthy();
  });

  it("displays subtopic completion stats", () => {
    (useStreak as Mock).mockReturnValue({ data: null, isLoading: false });
    render(
      <StudyStats
        examProgress={50}
        chaptersCompleted={10}
        totalChapters={20}
        subtopicsCompleted={50}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText("Subtopics")).toBeTruthy();
    expect(screen.getByText("50 / 100")).toBeTruthy();
  });

  it("shows streak loading skeleton", () => {
    (useStreak as Mock).mockReturnValue({ data: null, isLoading: true });
    render(
      <StudyStats
        examProgress={50}
        chaptersCompleted={10}
        totalChapters={20}
        subtopicsCompleted={50}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText("Overall")).toBeTruthy();
  });

  it("shows streak message when no streak", () => {
    (useStreak as Mock).mockReturnValue({ data: null, isLoading: false });
    render(
      <StudyStats
        examProgress={0}
        chaptersCompleted={0}
        totalChapters={20}
        subtopicsCompleted={0}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText("Start studying to build a streak!")).toBeTruthy();
  });

  it("shows streak badge when streak exists", () => {
    (useStreak as Mock).mockReturnValue({
      data: { current_streak: 5, longest_streak: 10 },
      isLoading: false,
    });
    render(
      <StudyStats
        examProgress={25}
        chaptersCompleted={5}
        totalChapters={20}
        subtopicsCompleted={25}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText(/days/i)).toBeTruthy();
  });

  it("renders with zero progress", () => {
    (useStreak as Mock).mockReturnValue({ data: null, isLoading: false });
    render(
      <StudyStats
        examProgress={0}
        chaptersCompleted={0}
        totalChapters={20}
        subtopicsCompleted={0}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText("Chapters")).toBeTruthy();
    expect(screen.getByText("0 / 20")).toBeTruthy();
  });

  it("renders with 100% progress", () => {
    (useStreak as Mock).mockReturnValue({
      data: { current_streak: 30, longest_streak: 30 },
      isLoading: false,
    });
    render(
      <StudyStats
        examProgress={100}
        chaptersCompleted={20}
        totalChapters={20}
        subtopicsCompleted={100}
        totalSubtopics={100}
      />
    );
    expect(screen.getByText("20 / 20")).toBeTruthy();
    expect(screen.getByText("100 / 100")).toBeTruthy();
  });
});
