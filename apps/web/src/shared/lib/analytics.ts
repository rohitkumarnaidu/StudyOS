import { posthog } from "@/shared/lib/posthog";

export type StudyOSEvent =
  | { event: "signup_completed"; properties: { method: "email" | "google" } }
  | { event: "login_completed"; properties: { method: "email" | "google" } }
  | { event: "logout"; properties: Record<string, never> }
  | { event: "subtopic_completed"; properties: { subtopic_id: string; chapter_id: string } }
  | { event: "subtopic_uncompleted"; properties: { subtopic_id: string; chapter_id: string } }
  | { event: "quiz_started"; properties: { quiz_type: string; question_count: number; chapter_id?: string } }
  | { event: "quiz_completed"; properties: { session_id: string; score: number; question_count: number } }
  | { event: "streak_achieved"; properties: { days: number; milestone: boolean } }
  | { event: "streak_broken"; properties: { previous_streak: number } }
  | { event: "note_uploaded"; properties: { note_type: string; file_size: number } }
  | { event: "note_viewed"; properties: { note_id: string; note_type: string } }
  | { event: "chat_message_sent"; properties: { has_chapter_context: boolean } }
  | { event: "roadmap_generated"; properties: { item_count: number } }
  | { event: "achievement_unlocked"; properties: { code: string; title: string } }
  | { event: "settings_updated"; properties: { section: string } }
  | { event: "offline_action_queued"; properties: { action: string } }
  | { event: "sync_completed"; properties: { items_synced: number } };

export function trackEvent(event: StudyOSEvent) {
  try {
    posthog.capture(event.event, event.properties);
  } catch {
    // PostHog not initialized or unavailable
  }
}
