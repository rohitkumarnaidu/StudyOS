"use client";

import { useEffect, useRef } from "react";
import { MessageBubble } from "@/features/chat/components/message-bubble";
import { ChatInput } from "@/features/chat/components/chat-input";
import { useChat } from "@/features/chat/hooks/use-chat";
import type { ChatMessage } from "@/features/chat/api";
import { ScrollArea } from "@/shared/components/ui/scroll-area";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Bot } from "lucide-react";

interface ChatWindowProps {
  sessionId: string;
  chapterContext?: string;
  initialMessages?: ChatMessage[];
  loading?: boolean;
}

export function ChatWindow({
  sessionId,
  chapterContext,
  initialMessages,
  loading,
}: ChatWindowProps) {
  const { messages, streaming, streamingText, sendMessage, stopStreaming, setHistory } =
    useChat({ sessionId, chapterContext });
  const scrollRef = useRef<HTMLDivElement>(null);
  const hasSetInitial = useRef(false);

  useEffect(() => {
    if (initialMessages && !hasSetInitial.current) {
      setHistory(initialMessages);
      hasSetInitial.current = true;
    }
  }, [initialMessages, setHistory]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, streamingText]);

  if (loading) {
    return (
      <div className="flex h-full flex-col p-4">
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-12 w-full rounded-lg" />
          ))}
        </div>
      </div>
    );
  }

  const allMessages = streaming
    ? [
        ...messages,
        {
          id: "streaming",
          session_id: sessionId,
          role: "assistant" as const,
          content: streamingText,
          token_count: 0,
          created_at: new Date().toISOString(),
        },
      ]
    : messages;

  return (
    <div className="flex h-full flex-col">
      <ScrollArea className="flex-1 px-4 py-4">
        {allMessages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
              <Bot className="h-6 w-6 text-muted-foreground" />
            </div>
            <div>
              <h3 className="text-sm font-medium">Start a conversation</h3>
              <p className="text-xs text-muted-foreground">
                {chapterContext
                  ? `Ask about this chapter: ${chapterContext}`
                  : "Ask anything about your syllabus"}
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-0">
            {allMessages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                isStreaming={msg.id === "streaming"}
              />
            ))}
            <div ref={scrollRef} />
          </div>
        )}
      </ScrollArea>

      <ChatInput
        onSend={sendMessage}
        onStop={stopStreaming}
        streaming={streaming}
        placeholder={chapterContext ? "Ask about this chapter..." : "Ask me anything..."}
      />
    </div>
  );
}
