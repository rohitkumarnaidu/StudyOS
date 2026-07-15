"use client";

import type { ChatSession } from "@/features/chat/api";
import { Button } from "@/shared/components/ui/button";
import { ScrollArea } from "@/shared/components/ui/scroll-area";
import { Plus, MessageSquare, Trash2 } from "lucide-react";
import { cn } from "@/shared/lib";

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  loading?: boolean;
}

export function ChatSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  loading,
}: ChatSidebarProps) {
  return (
    <div className="flex h-full flex-col border-r border-border bg-muted/20">
      <div className="flex items-center justify-between border-b border-border p-3">
        <h2 className="text-sm font-semibold">Chats</h2>
        <Button size="sm" variant="ghost" onClick={onNewSession} aria-label="New chat">
          <Plus className="mr-1 h-3 w-3" />
          New
        </Button>
      </div>

      <ScrollArea className="flex-1 px-2 py-2">
        {loading ? (
          <div className="space-y-2 px-2 py-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 animate-pulse rounded-md bg-muted" />
            ))}
          </div>
        ) : sessions.length === 0 ? (
          <div className="px-2 py-8 text-center text-xs text-muted-foreground">
            No conversations yet
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={cn(
                  "group flex items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors hover:bg-muted/50",
                  activeSessionId === session.id && "bg-muted",
                )}
              >
                <button
                  className="flex flex-1 items-center gap-2 truncate"
                  onClick={() => onSelectSession(session.id)}
                >
                  <MessageSquare className="h-4 w-4 flex-shrink-0 text-muted-foreground" />
                  <span className="truncate">{session.title}</span>
                </button>
                <button
                  className="flex-shrink-0 opacity-0 transition-opacity group-hover:opacity-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                  aria-label={`Delete ${session.title}`}
                >
                  <Trash2 className="h-3 w-3 text-muted-foreground hover:text-destructive" />
                </button>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
