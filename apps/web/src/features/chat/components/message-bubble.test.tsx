import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { MessageBubble } from "@/features/chat/components/message-bubble";

describe("MessageBubble", () => {
  const userMessage = {
    id: "m1",
    session_id: "s1",
    role: "user" as const,
    content: "What is photosynthesis?",
    token_count: 0,
    created_at: "2024-01-01",
  };

  const assistantMessage = {
    id: "m2",
    session_id: "s1",
    role: "assistant" as const,
    content: "Photosynthesis is the process by which plants convert light into energy.",
    token_count: 100,
    created_at: "2024-01-01",
  };

  it("renders user message with correct content", () => {
    render(<MessageBubble message={userMessage} />);
    expect(screen.getByText("What is photosynthesis?")).toBeTruthy();
  });

  it("renders assistant message with correct content", () => {
    render(<MessageBubble message={assistantMessage} />);
    expect(
      screen.getByText("Photosynthesis is the process by which plants convert light into energy."),
    ).toBeTruthy();
  });

  it("shows streaming cursor when isStreaming is true", () => {
    const { container } = render(<MessageBubble message={assistantMessage} isStreaming />);
    const cursor = container.querySelector(".animate-pulse");
    expect(cursor).toBeTruthy();
  });

  it("does not show streaming cursor when isStreaming is false", () => {
    const { container } = render(<MessageBubble message={assistantMessage} isStreaming={false} />);
    const cursors = container.querySelectorAll(".animate-pulse");
    expect(cursors.length).toBe(0);
  });

  it("aligns user message to the right", () => {
    const { container } = render(<MessageBubble message={userMessage} />);
    const wrapper = container.firstChild;
    expect(wrapper).toHaveClass("flex-row-reverse");
  });

  it("aligns assistant message to the left", () => {
    const { container } = render(<MessageBubble message={assistantMessage} />);
    const wrapper = container.firstChild;
    expect(wrapper).toHaveClass("flex-row");
    expect(wrapper).not.toHaveClass("flex-row-reverse");
  });

  it("handles long content with word break", () => {
    const longMessage = {
      ...assistantMessage,
      content: "a".repeat(200),
    };
    render(<MessageBubble message={longMessage} />);
    expect(screen.getByText(longMessage.content)).toBeTruthy();
  });

  it("renders multiline content correctly", () => {
    const multiLine = {
      ...assistantMessage,
      content: "Line 1\nLine 2\nLine 3",
    };
    render(<MessageBubble message={multiLine} />);
    expect(screen.getByText(/Line 1/)).toBeTruthy();
  });
});
