# SKILL_ANALYTICS.md
# StudyOS — Analytics Patterns & Event Catalog
# Read before adding any tracking, building dashboards, or querying metrics

---

## 1. EVENT NAMING CONVENTION

```
Format:     snake_case, past tense verb
Structure:  {noun}_{verb}
Examples:   subtopic_completed, roadmap_generated, chapter_opened

Rules:
  ✅ Past tense: subtopic_completed (not subtopic_complete)
  ✅ Noun first: chapter_opened (not opened_chapter)
  ✅ Specific: quiz_submitted (not action_taken)
  ❌ No PII in event names or properties (use user_id, not email)
  ❌ No nested objects in properties (flatten to top-level keys)
  ❌ No arrays in properties (join as comma-separated string)
```

---

## 2. REQUIRED PROPERTIES (every event)

```typescript
interface BaseEventProperties {
  user_id: string;          // Supabase user UUID (never email/phone)
  session_id: string;       // Browser session UUID (regenerate each app open)
  timestamp: string;        // ISO 8601 UTC
  app_version: string;      // e.g., "1.2.3"
  platform: 'web' | 'pwa' | 'android' | 'ios';
  exam_type: 'NEET_2026' | 'JEE_MAINS' | 'JEE_ADVANCED' | 'custom';
}
```

---

## 3. COMPLETE EVENT CATALOG

```typescript
// lib/analytics.ts
export type AnalyticsEvent =
  // ── ONBOARDING ──────────────────────────────────────────
  | { event: 'onboarding_started' }
  | { event: 'exam_profile_selected'; exam_type: string }
  | { event: 'exam_date_set'; days_remaining: number; urgency_level: string }
  | { event: 'chapters_assessed'; chapters_marked: number }
  | { event: 'llm_provider_configured'; provider: string }
  | { event: 'onboarding_completed'; duration_seconds: number }
  | { event: 'onboarding_skipped'; step: string }

  // ── AUTH ────────────────────────────────────────────────
  | { event: 'user_signed_up'; method: 'email' | 'google' | 'phone' }
  | { event: 'user_signed_in'; method: 'email' | 'google' | 'phone' | 'magic_link' }
  | { event: 'user_signed_out' }
  | { event: 'password_reset_requested' }

  // ── STUDY / CHECKLIST ───────────────────────────────────
  | { event: 'chapter_opened'; chapter_id: string; chapter_name: string; subject: string; tier: number }
  | { event: 'topic_expanded'; topic_id: string; chapter_id: string }
  | { event: 'subtopic_completed'; subtopic_id: string; chapter_id: string; subject: string; is_high_yield: boolean }
  | { event: 'subtopic_uncompleted'; subtopic_id: string; chapter_id: string }
  | { event: 'chapter_completed'; chapter_id: string; chapter_name: string; subject: string; time_to_complete_days: number }
  | { event: 'all_tier1_complete'; subject: string }
  | { event: 'study_session_started'; chapters_planned: string }
  | { event: 'study_session_ended'; duration_minutes: number; subtopics_completed: number }

  // ── STREAKS ─────────────────────────────────────────────
  | { event: 'streak_achieved'; days: number; milestone: boolean }
  | { event: 'streak_broken'; previous_streak: number }
  | { event: 'streak_freeze_used'; streak_days: number }

  // ── AI CHAT ─────────────────────────────────────────────
  | { event: 'chat_opened'; chapter_id: string; trigger: 'fab' | 'subtopic' | 'suggestion' }
  | { event: 'message_sent'; chapter_id: string; message_length: number; provider: string }
  | { event: 'ai_response_received'; chapter_id: string; response_tokens: number; latency_ms: number; provider: string }
  | { event: 'chat_suggestion_clicked'; suggestion_text: string; chapter_id: string }
  | { event: 'chat_exported_as_note'; chapter_id: string; message_count: number }
  | { event: 'chat_provider_switched'; from_provider: string; to_provider: string }

  // ── NOTES ───────────────────────────────────────────────
  | { event: 'note_upload_started'; source_type: 'image' | 'pdf' | 'text' | 'camera' }
  | { event: 'note_ocr_completed'; pages: number; quality_score: number; duration_ms: number }
  | { event: 'note_extraction_completed'; topics_found: number; confidence: number; gaps_detected: number }
  | { event: 'note_saved'; chapter_id: string; source_type: string; word_count: number }
  | { event: 'note_deleted'; chapter_id: string }
  | { event: 'note_extraction_rejected'; reason: string }

  // ── ROADMAP ─────────────────────────────────────────────
  | { event: 'roadmap_generated'; weeks_remaining: number; urgency_level: string; readiness_score: number; generation_ms: number }
  | { event: 'roadmap_viewed'; week_number: number }
  | { event: 'roadmap_regenerated'; trigger: 'manual' | 'weekly_auto' | 'progress_change' }
  | { event: 'roadmap_exported'; format: 'pdf' | 'image' | 'calendar' }
  | { event: 'week_plan_expanded'; week_number: number }

  // ── QUIZ ────────────────────────────────────────────────
  | { event: 'quiz_started'; chapter_id: string; question_count: number; mode: 'practice' | 'exam' }
  | { event: 'question_answered'; chapter_id: string; is_correct: boolean; time_taken_seconds: number; difficulty: string }
  | { event: 'quiz_completed'; chapter_id: string; score: number; total: number; accuracy_pct: number; time_taken_seconds: number }
  | { event: 'mistake_logged'; chapter_id: string; subtopic: string }
  | { event: 'mistake_resolved'; chapter_id: string; subtopic: string }
  | { event: 'pyq_viewed'; question_id: string; year: number; chapter_id: string }

  // ── ANALYTICS ───────────────────────────────────────────
  | { event: 'analytics_viewed'; section: 'overview' | 'heatmap' | 'weak_areas' | 'velocity' }
  | { event: 'report_exported'; format: 'pdf'; recipient: 'self' | 'teacher' | 'parent' }
  | { event: 'rank_predictor_used'; predicted_score: number; estimated_air: number }

  // ── INTEGRATIONS ────────────────────────────────────────
  | { event: 'notebooklm_exported'; chapter_count: number; format: 'single' | 'zip' }
  | { event: 'drive_connected' }
  | { event: 'drive_synced'; files_pushed: number }
  | { event: 'whatsapp_opted_in'; notification_type: string }
  | { event: 'whatsapp_opted_out' }

  // ── PAYMENTS ────────────────────────────────────────────
  // NOTE: Payments are out of scope for StudyOS (free platform).
  // These events are reserved for future monetization if needed.
  // | { event: 'upgrade_clicked'; ... }
  // | { event: 'plan_selected'; ... }
  // | { event: 'payment_completed'; ... }
  // | { event: 'subscription_cancelled'; ... }

  // ── APP ─────────────────────────────────────────────────
  | { event: 'app_opened'; source: 'direct' | 'notification' | 'whatsapp' | 'deeplink' }
  | { event: 'pwa_installed' }
  | { event: 'offline_mode_entered' }
  | { event: 'sync_completed'; records_synced: number; duration_ms: number }
  | { event: 'settings_changed'; setting: string; value: string }
  | { event: 'dark_mode_toggled'; to: 'dark' | 'light' | 'system' }
  | { event: 'language_changed'; to: string };
```

---

## 4. ANALYTICS CLIENT IMPLEMENTATION

```typescript
// lib/analytics.ts
import posthog from 'posthog-js';

let sessionId = crypto.randomUUID();

export const analytics = {
  init(userId?: string) {
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_KEY!, {
      api_host: 'https://app.posthog.com',
      capture_pageview: false,          // manual page tracking
      capture_pageleave: true,
      session_recording: {
        maskAllInputs: true,            // mask all inputs (privacy)
        maskTextSelector: '.note-content, .chat-message', // mask note/chat content
      },
      persistence: 'localStorage+cookie',
      loaded: (ph) => {
        if (process.env.NODE_ENV === 'development') ph.opt_out_capturing(); // no tracking in dev
      },
    });
    if (userId) this.identify(userId);
  },

  identify(userId: string, traits?: Record<string, unknown>) {
    posthog.identify(userId, {
      ...traits,
      // NEVER include: email, phone, name in identify (use user_id only)
    });
  },

  track(eventName: string, properties: Record<string, unknown> = {}) {
    posthog.capture(eventName, {
      ...properties,
      session_id: sessionId,
      app_version: process.env.NEXT_PUBLIC_APP_VERSION || '0.1.0',
      platform: isPWA() ? 'pwa' : 'web',
    });
  },

  page(pageName: string) {
    posthog.capture('$pageview', { page: pageName });
  },

  reset() {
    posthog.reset();
    sessionId = crypto.randomUUID(); // new session on logout
  },
};

// Type-safe wrapper
export function trackEvent(event: AnalyticsEvent) {
  const { event: eventName, ...properties } = event;
  analytics.track(eventName, properties);
}
```

---

## 5. KEY FUNNELS TO TRACK

```
Activation Funnel:
  user_signed_up
    → onboarding_completed
    → chapter_opened (first time)
    → subtopic_completed (first time)
    → study_session_ended (>10 min)

  Target: >60% reach subtopic_completed within 24h of signup

Engagement Funnel:
  chapter_opened
    → subtopic_completed (>1)
    → chapter_completed
    → next chapter_opened

  Target: >40% chapter completion rate on opened chapters

AI Adoption:
  chapter_opened
    → chat_opened
    → message_sent
    → ai_response_received

  Target: >50% of chapters opened have at least 1 AI interaction

Payment Funnel:
  upgrade_clicked
    → plan_selected
    → payment_completed

  Target: >20% conversion from upgrade_clicked to payment_completed

Retention:
  Day 1:  app_opened (day of signup) → target 100%
  Day 7:  study_session_started → target >50%
  Day 30: study_session_started → target >35%
  Day 90: study_session_started → target >25%
```

---

## 6. STUDENT ANALYTICS DASHBOARD QUERIES

```sql
-- Study time this week (for personal dashboard)
SELECT
  SUM(total_minutes) as total_minutes,
  COUNT(DISTINCT DATE(started_at)) as days_studied
FROM study_sessions
WHERE user_id = $1
  AND started_at >= DATE_TRUNC('week', NOW());

-- Chapter completion by subject
SELECT
  s.name as subject,
  COUNT(c.id) as total_chapters,
  COUNT(CASE WHEN get_chapter_completion_pct($1, c.id) = 100 THEN 1 END) as completed,
  ROUND(AVG(get_chapter_completion_pct($1, c.id)), 1) as avg_completion_pct
FROM chapters c
JOIN subjects s ON c.subject_id = s.id
WHERE c.is_deleted = FALSE
GROUP BY s.name;

-- Daily study heatmap (last 52 weeks)
SELECT
  DATE(started_at) as study_date,
  SUM(total_minutes) as minutes
FROM study_sessions
WHERE user_id = $1
  AND started_at >= NOW() - INTERVAL '364 days'
GROUP BY DATE(started_at)
ORDER BY study_date;

-- Quiz accuracy by chapter (for weak area detection)
SELECT
  c.name as chapter_name,
  c.subject_id,
  c.tier,
  COUNT(qr.id) as questions_attempted,
  SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) as correct,
  ROUND(
    SUM(CASE WHEN qr.is_correct THEN 1.0 ELSE 0.0 END) / NULLIF(COUNT(qr.id), 0) * 100,
    1
  ) as accuracy_pct
FROM quiz_responses qr
JOIN questions q ON qr.question_id = q.id
JOIN chapters c ON q.chapter_id = c.id
JOIN quiz_sessions qs ON qr.session_id = qs.id
WHERE qs.user_id = $1
  AND qs.started_at >= NOW() - INTERVAL '30 days'
GROUP BY c.id, c.name, c.subject_id, c.tier
HAVING COUNT(qr.id) >= 3
ORDER BY accuracy_pct ASC
LIMIT 10;
```

---

## 7. BUSINESS METRICS (Metabase Queries)

```sql
-- DAU/WAU/MAU
SELECT
  COUNT(DISTINCT CASE WHEN e.created_at >= NOW() - INTERVAL '1 day' THEN e.user_id END) as dau,
  COUNT(DISTINCT CASE WHEN e.created_at >= NOW() - INTERVAL '7 days' THEN e.user_id END) as wau,
  COUNT(DISTINCT CASE WHEN e.created_at >= NOW() - INTERVAL '30 days' THEN e.user_id END) as mau
FROM events e
WHERE e.event_type = 'study_session_started';

-- Feature adoption (% of WAU using each feature)
SELECT
  feature,
  COUNT(DISTINCT user_id) as users,
  ROUND(COUNT(DISTINCT user_id)::FLOAT / wau.total * 100, 1) as adoption_pct
FROM (
  SELECT 'AI Chat' as feature, user_id FROM events WHERE event_type = 'chat_opened' AND created_at >= NOW() - INTERVAL '7 days'
  UNION ALL
  SELECT 'Roadmap', user_id FROM events WHERE event_type = 'roadmap_viewed' AND created_at >= NOW() - INTERVAL '7 days'
  UNION ALL
  SELECT 'Notes Upload', user_id FROM events WHERE event_type = 'note_saved' AND created_at >= NOW() - INTERVAL '7 days'
  UNION ALL
  SELECT 'Quiz', user_id FROM events WHERE event_type = 'quiz_completed' AND created_at >= NOW() - INTERVAL '7 days'
) features
CROSS JOIN (
  SELECT COUNT(DISTINCT user_id) as total FROM events WHERE event_type = 'app_opened' AND created_at >= NOW() - INTERVAL '7 days'
) wau
GROUP BY feature, wau.total;

-- D1/D7/D30 retention cohort
WITH signups AS (
  SELECT user_id, DATE(created_at) as signup_date
  FROM events WHERE event_type = 'user_signed_up'
),
activity AS (
  SELECT DISTINCT user_id, DATE(created_at) as active_date
  FROM events WHERE event_type = 'study_session_started'
)
SELECT
  s.signup_date,
  COUNT(DISTINCT s.user_id) as cohort_size,
  COUNT(DISTINCT CASE WHEN a.active_date = s.signup_date + 1 THEN s.user_id END) as d1,
  COUNT(DISTINCT CASE WHEN a.active_date = s.signup_date + 7 THEN s.user_id END) as d7,
  COUNT(DISTINCT CASE WHEN a.active_date = s.signup_date + 30 THEN s.user_id END) as d30
FROM signups s
LEFT JOIN activity a ON s.user_id = a.user_id
GROUP BY s.signup_date
ORDER BY s.signup_date DESC;
```

---

## 8. DO / DON'T

```
✅ DO:
  Track specific events (subtopic_completed, not just "interaction")
  Include chapter_id, subject on all study-related events
  Use user_id (UUID), never email or phone in events
  Track latency_ms on all AI calls (performance monitoring)
  Track conversion funnels end-to-end
  Include urgency_level in roadmap events (understand which users care about urgency)

❌ DON'T:
  Track PII (email, phone, name) in event properties
  Nest objects in event properties (flatten everything)
  Track in development (PostHog auto-disabled in dev mode above)
  Skip session_id (needed for funnel analysis)
  Batch events without flushing on page unload
  Track events before user consent (get consent during onboarding)
```

---
*SKILL_ANALYTICS.md — StudyOS Enterprise | May 2026*
