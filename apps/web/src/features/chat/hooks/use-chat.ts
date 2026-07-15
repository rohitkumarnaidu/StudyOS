"use client";

import { useState, useCallback, useRef } from "react";
import { streamChat, type ChatMessage } from "@/features/chat/api";

export interface UseChatOptions {
  sessionId: string;
  chapterContext?: string;
  onMessageSaved?: (message: ChatMessage) => void;
}

export function useChat({ sessionId, chapterContext }: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const abortRef = useRef(false);

  const sendMessage = useCallback(
    async (content: string) => {
      if (streaming || !content.trim()) return;

      const userMsg: ChatMessage = {
        id: `opt-${Date.now()}`,
        session_id: sessionId,
        role: "user",
        content: content.trim(),
        token_count: 0,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMsg]);
      setStreaming(true);
      setStreamingText("");
      abortRef.current = false;

      await streamChat(
        {
          session_id: sessionId,
          message: content.trim(),
          chapter_context: chapterContext,
        },
        (chunk) => {
          setStreamingText((prev) => prev + chunk);
        },
        () => {
          if (!abortRef.current) {
            const assistantMsg: ChatMessage = {
              id: `opt-${Date.now()}-assistant`,
              session_id: sessionId,
              role: "assistant",
              content: streamingText,
              token_count: 0,
              created_at: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
            setStreamingText("");
            setStreaming(false);
          }
        },
        (error) => {
          setStreaming(false);
          setStreamingText("");
          console.error("Chat stream error:", error);
        },
      );
    },
    [sessionId, chapterContext, streaming, streamingText],
  );

  const stopStreaming = useCallback(() => {
    abortRef.current = true;
    setStreaming(false);
    if (streamingText) {
      const assistantMsg: ChatMessage = {
        id: `opt-${Date.now()}-stop`,
        session_id: sessionId,
        role: "assistant",
        content: streamingText,
        token_count: 0,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      setStreamingText("");
    }
  }, [sessionId, streamingText]);

  const setHistory = useCallback((history: ChatMessage[]) => {
    setMessages(history);
  }, []);

  return {
    messages,
    streaming,
    streamingText,
    sendMessage,
    stopStreaming,
    setHistory,
  };
}
