import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import { ChatInput } from "@/features/chat/components/chat-input";

describe("ChatInput", () => {
  it("renders textarea with placeholder", () => {
    render(<ChatInput onSend={vi.fn()} onStop={vi.fn()} />);
    expect(screen.getByPlaceholderText("Ask about this chapter...")).toBeTruthy();
  });

  it("shows stop button when streaming", () => {
    render(<ChatInput onSend={vi.fn()} onStop={vi.fn()} streaming />);
    expect(screen.getByLabelText("Stop generating")).toBeTruthy();
  });

  it("uses custom placeholder", () => {
    render(
      <ChatInput onSend={vi.fn()} onStop={vi.fn()} placeholder="Type here..." />,
    );
    expect(screen.getByPlaceholderText("Type here...")).toBeTruthy();
  });
});
