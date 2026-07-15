import { apiFetch } from "@/shared/api";

export interface ChatSession {
  id: string;
  title: string;
  chapter_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  token_count: number;
  created_at: string;
}

export interface CreateChatSessionRequest {
  title?: string;
  chapter_id?: string;
}

export interface StreamChatRequest {
  session_id: string;
  message: string;
  model?: string;
  chapter_context?: string;
}

export async function listChatSessions(): Promise<ChatSession[]> {
  return apiFetch<ChatSession[]>("/v1/chat/sessions");
}

export async function getChatSession(sessionId: string): Promise<ChatSession> {
  return apiFetch<ChatSession>(`/v1/chat/sessions/${sessionId}`);
}

export async function createChatSession(
  body: CreateChatSessionRequest,
): Promise<ChatSession> {
  return apiFetch<ChatSession>("/v1/chat/sessions", {
    method: "POST",
    body,
  });
}

export async function deleteChatSession(sessionId: string): Promise<void> {
  await apiFetch(`/v1/chat/sessions/${sessionId}`, { method: "DELETE" });
}

export async function listChatMessages(sessionId: string): Promise<ChatMessage[]> {
  return apiFetch<ChatMessage[]>(`/v1/chat/sessions/${sessionId}/messages`);
}

export async function streamChat(
  body: StreamChatRequest,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (error: Error) => void,
): Promise<void> {
  try {
    const res = await fetch("/api/ai/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      onError(new Error(errText || `Stream failed: ${res.status}`));
      return;
    }

    const reader = res.body?.getReader();
    if (!reader) {
      onError(new Error("No response body"));
      return;
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            onDone();
            return;
          }
          try {
            const parsed = JSON.parse(data) as { text?: string; error?: string };
            if (parsed.error) {
              onError(new Error(parsed.error));
              return;
            }
            if (parsed.text) {
              onChunk(parsed.text);
            }
          } catch {
            // Skip malformed JSON
          }
        }
      }
    }

    onDone();
  } catch (e) {
    onError(e instanceof Error ? e : new Error(String(e)));
  }
}
