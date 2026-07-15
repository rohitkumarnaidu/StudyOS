import { describe, expect, it, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";

import * as chatApi from "@/features/chat/api";
import { useChat } from "@/features/chat/hooks/use-chat";

vi.mock("@/features/chat/api", () => ({
  streamChat: vi.fn(),
}));

describe("useChat", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("initializes with empty messages", () => {
    const { result } = renderHook(() => useChat({ sessionId: "s1" }));
    expect(result.current.messages).toEqual([]);
    expect(result.current.streaming).toBe(false);
    expect(result.current.streamingText).toBe("");
  });

  it("adds user message when sending", async () => {
    vi.mocked(chatApi.streamChat).mockResolvedValue(undefined);

    const { result } = renderHook(() => useChat({ sessionId: "s1" }));

    await act(async () => {
      await result.current.sendMessage("Hello");
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].content).toBe("Hello");
  });

  it("calls streamChat with correct parameters", async () => {
    vi.mocked(chatApi.streamChat).mockResolvedValue(undefined);

    const { result } = renderHook(() => useChat({ sessionId: "s1", chapterContext: "ch1" }));

    await act(async () => {
      await result.current.sendMessage("Test question");
    });

    expect(chatApi.streamChat).toHaveBeenCalledWith(
      { session_id: "s1", message: "Test question", chapter_context: "ch1" },
      expect.any(Function),
      expect.any(Function),
      expect.any(Function),
    );
  });

  it("does not send empty messages", async () => {
    const { result } = renderHook(() => useChat({ sessionId: "s1" }));

    await act(async () => {
      await result.current.sendMessage("");
    });

    expect(chatApi.streamChat).not.toHaveBeenCalled();
    expect(result.current.messages).toEqual([]);
  });

  it("does not send whitespace-only messages", async () => {
    const { result } = renderHook(() => useChat({ sessionId: "s1" }));

    await act(async () => {
      await result.current.sendMessage("   ");
    });

    expect(chatApi.streamChat).not.toHaveBeenCalled();
  });

  it("sets history from external source", () => {
    const history = [
      { id: "m1", session_id: "s1", role: "user" as const, content: "Hi", token_count: 0, created_at: "2024-01-01" },
    ];

    const { result } = renderHook(() => useChat({ sessionId: "s1" }));

    act(() => {
      result.current.setHistory(history);
    });

    expect(result.current.messages).toEqual(history);
  });
});
