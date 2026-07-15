/* eslint-disable react-hooks/set-state-in-effect */
"use client";

import { useState, useEffect, useCallback, startTransition } from "react";
import { ChatSidebar } from "@/features/chat/components/chat-sidebar";
import { ChatWindow } from "@/features/chat/components/chat-window";
import {
  listChatSessions,
  createChatSession,
  deleteChatSession,
  listChatMessages,
  type ChatSession,
  type ChatMessage,
} from "@/features/chat/api";
import { notifyError, notifySuccess } from "@/shared/lib";

let sessionsInflight: Promise<ChatSession[]> | null = null;

async function fetchSessions(): Promise<ChatSession[]> {
  if (sessionsInflight === null) {
    sessionsInflight = listChatSessions().finally(() => {
      sessionsInflight = null;
    });
  }
  return sessionsInflight;
}

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);

  const refreshSessions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchSessions();
      setSessions(data);
      setActiveSessionId((prev) => prev ?? (data.length > 0 ? data[0].id : null));
    } catch {
      notifyError("Failed to load chat sessions");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    startTransition(() => {
      void refreshSessions();
    });
  }, [refreshSessions]);

  useEffect(() => {
    if (!activeSessionId) return;

    setMessagesLoading(true);
    listChatMessages(activeSessionId)
      .then(setMessages)
      .catch(() => notifyError("Failed to load messages"))
      .finally(() => setMessagesLoading(false));
  }, [activeSessionId]);

  async function handleNewSession() {
    try {
      const session = await createChatSession({ title: "New conversation" });
      setSessions((prev) => [session, ...prev]);
      setActiveSessionId(session.id);
      setMessages([]);
    } catch {
      notifyError("Failed to create chat session");
    }
  }

  async function handleDeleteSession(id: string) {
    try {
      await deleteChatSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (activeSessionId === id) {
        setActiveSessionId(null);
        setMessages([]);
      }
      notifySuccess("Chat deleted");
    } catch {
      notifyError("Failed to delete chat");
    }
  }

  return (
    <div className="flex h-[calc(100vh-3.5rem)]">
      <div className="w-64 flex-shrink-0">
        <ChatSidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={setActiveSessionId}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
          loading={loading}
        />
      </div>

      <div className="flex-1">
        {activeSessionId ? (
          <ChatWindow
            sessionId={activeSessionId}
            initialMessages={messages}
            loading={messagesLoading}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
            Select a chat or start a new conversation
          </div>
        )}
      </div>
    </div>
  );
}
