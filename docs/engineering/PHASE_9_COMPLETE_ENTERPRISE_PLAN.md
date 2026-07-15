# StudyOS — Complete Enterprise Implementation Plan

**Date:** 2026-05-18
**Scope:** All 20 enterprise features + infrastructure
**Current State:** 5 enterprise-grade, 8 basic, 3 planned, 7 not started
**Target:** 20 enterprise-grade features + full infrastructure stack

---

## Phase 0: Infrastructure Foundation (Prerequisites)

**Timeline:** 2 sprints (4 weeks)
**Goal:** Build the infrastructure backbone that all features depend on

### 0.1 Event Architecture
- [ ] Redis Streams message broker
- [ ] Event bus service (`services/event_bus.py`)
- [ ] Event types: `study.completed`, `quiz.finished`, `roadmap.generated`, `revision.due`
- [ ] Event consumers for async processing
- [ ] Dead letter queue for failed events
- **Files:** `services/event_bus.py`, `services/event_types.py`, `services/event_consumer.py`
- **Tests:** 20+ tests for event publishing/consuming/retry

### 0.2 Distributed Task Queue
- [x] Celery + Redis broker setup
- [x] Task workers: AI generation, report building, email notifications
- [x] Task monitoring dashboard
- [x] Retry policies with exponential backoff
- **Files:** `tasks/celery_app.py`, `tasks/ai_tasks.py`, `tasks/report_tasks.py`, `tasks/notification_tasks.py`
- **Docker:** Celery worker + beat containers in docker-compose
- **Tests:** 52 tests for Celery config, AI tasks, report tasks, notification tasks

### 0.3 Vector Database Pipeline
- [x] pgvector embedding pipeline
- [x] Text chunking service (recursive character split)
- [x] Embedding generation (OpenAI/Anthropic)
- [x] Semantic search service
- [x] RAG pipeline for NotebookLM
- **Files:** `services/embedding_pipeline.py`, `services/chunker.py`, `services/semantic_search.py`
- **DB Migration:** `20260518010000_vector_pipeline.sql` (embedding_store, chunk_store, search_index, HNSW index)
- **Tests:** 53 tests for chunker, embedding pipeline, semantic search, RAG

### 0.4 Realtime Infrastructure
- [x] WebSocket server (FastAPI WebSocket)
- [x] Supabase Realtime subscriptions
- [x] Presence tracking (online users)
- [x] Realtime event broadcasting
- **Files:** `services/websocket_manager.py`, `services/presence.py`, `services/websocket_handlers.py`, `api/v1/routes/websocket.py`
- **Tests:** 49 tests for WebSocket manager, presence tracking, handler registry

### 0.5 Observability Stack
- [x] OpenTelemetry Collector (Docker)
- [x] Prometheus + Grafana (Docker)
- [x] Jaeger tracing (Docker)
- [x] OTLP instrumentation in FastAPI
- [x] SLO dashboards (Grafana)
- [x] Alert rules (Prometheus)
- **Files:** `middleware/otel.py`, `docker/otel-collector-config.yaml`, `docker/prometheus.yml`, `docker/prometheus/alerts/studyos_alerts.yml`, `docker/grafana/dashboards/`
- **Docker:** 4 new services (otel-collector, jaeger, prometheus, grafana) with `observability` profile
- **Tests:** 8 tests for OTel middleware

### 0.6 Cost & Governance (Free-Tier Friendly)
- [x] AI token cost tracking per user (always $0, analytics only)
- [x] Budget alerts (email/in-app) — soft, informational, never blocks
- [x] Prompt injection guards (safety, not monetization)
- [x] Content filter middleware (quality control)
- [x] AI output audit trail
- **Files:** `services/ai_usage_tracker.py`, `services/budget_alerts.py`, `middleware/prompt_guard.py`, `middleware/content_filter.py`, `services/ai_audit.py`
- **DB Migration:** `20260518020000_ai_cost_governance.sql` (ai_usage_logs, ai_audit_trail, ai_budget_thresholds, ai_safety_log)
- **Tests:** 70 tests for usage tracker, budget alerts, prompt guard, content filter, audit trail

### 0.7 Feature Flag System
- [x] PostHog flag sync to local cache
- [x] `useFeatureFlag` hook wired into app config
- [x] Server-side flag evaluation
- [x] Gradual rollout support
- **Files:** `services/feature_flags.py`, `middleware/feature_flag.py`
- **DB Migration:** `20260518030000_feature_flags.sql` (feature_flags, flag_sync_log, flag_evaluation_log + 8 seed flags)
- **Tests:** 38 tests for flag service, rollout, conditions, PostHog sync, middleware

### 0.8 Disaster Recovery
- [x] Automated backup scheduling
- [x] DR drill scripts
- [x] Multi-region readiness checklist
- [x] Runbook automation
- **Files:** `scripts/backup/automated-backup.sh`, `scripts/dr/dr-drill.sh`, `docs/runbooks/disaster-recovery.md`, `docs/runbooks/multi-region-readiness.md`
- **Tests:** 24 tests for backup scripts, DR drill, runbooks, multi-region checklist

---

## Phase 1: Smart Revision Engine + Mistake Intelligence

**Timeline:** 3 sprints (6 weeks)
**Dependencies:** Phase 0.1 (event bus), Phase 0.3 (vector pipeline)

### 1.1 Smart Revision Engine (PLANNED → ENTERPRISE)

**Backend:**
- [ ] `services/spaced_repetition.py` — SM-2 algorithm
- [ ] `services/retention_tracker.py` — Forgetting curve model
- [ ] `services/revision_pack_generator.py` — AI-curated packs
- [ ] `services/active_recall.py` — Active recall sessions
- [ ] `api/v1/routes/revision.py` — 7 endpoints
- [ ] `controllers/revision_controller.py`

**Frontend:**
- [ ] `features/revision/components/revision-dashboard.tsx`
- [ ] `features/revision/components/revision-card.tsx` — Flashcard UI
- [ ] `features/revision/components/retention-graph.tsx`
- [ ] `features/revision/components/forgetting-curve.tsx`
- [ ] `features/revision/components/revision-pack-viewer.tsx`
- [ ] `features/revision/components/active-recall-session.tsx`
- [ ] `features/revision/hooks/use-revision-queue.ts`
- [ ] `features/revision/hooks/use-spaced-repetition.ts`
- [ ] `features/revision/api.ts`

**Database:**
- [ ] `supabase/migrations/20260519000000_smart_revision.sql`
  - `revision_items` (ease_factor, interval, repetitions, next_review)
  - `revision_sessions` (items_reviewed, retention_rate)
  - `retention_records` (quality_score, predicted/actual retention)
  - `revision_packs` (pack_type, items JSONB)

**Tests:**
- [ ] `tests/services/test_spaced_repetition.py` — SM-2 algorithm (15 tests)
- [ ] `tests/services/test_retention_tracker.py` — Forgetting curve (10 tests)
- [ ] `tests/services/test_revision_pack_generator.py` — Pack generation (8 tests)
- [ ] `tests/api/test_revision_routes.py` — Endpoint tests (12 tests)
- [ ] Web component tests for revision components (20 tests)

### 1.2 AI Mistake Intelligence (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/mistake_tracker.py` — Detailed mistake logging
- [ ] `services/concept_gap_analyzer.py` — Gap detection from patterns
- [ ] `services/mistake_predictor.py` — Future mistake prediction
- [ ] `services/semantic_clusterer.py` — Embedding-based error clustering
- [ ] `services/cognitive_pattern_detector.py` — Time pressure, guessing detection
- [ ] `api/v1/routes/mistakes.py` — 8 endpoints
- [ ] `controllers/mistake_controller.py`

**Frontend:**
- [ ] `features/mistakes/components/mistake-dashboard.tsx`
- [ ] `features/mistakes/components/concept-gap-viewer.tsx`
- [ ] `features/mistakes/components/weakness-heatmap.tsx`
- [ ] `features/mistakes/components/recovery-plan-viewer.tsx`
- [ ] `features/mistakes/components/pattern-insights.tsx`
- [ ] `features/mistakes/hooks/use-mistake-analysis.ts`
- [ ] `features/mistakes/hooks/use-concept-gaps.ts`
- [ ] `features/mistakes/api.ts`

**Database:**
- [ ] `supabase/migrations/20260520000000_mistake_intelligence.sql`
  - `mistake_logs` (mistake_type, concept_tags, confidence_level)
  - `concept_gaps` (severity, first/last detected, resolved)
  - `mistake_patterns` (pattern_type, confidence, is_active)
  - `recovery_recommendations` (type, priority, completed)

**Tests:**
- [ ] `tests/services/test_mistake_tracker.py` — Logging + categorization (12 tests)
- [ ] `tests/services/test_concept_gap_analyzer.py` — Gap detection (10 tests)
- [ ] `tests/services/test_semantic_clusterer.py` — Embedding clustering (8 tests)
- [ ] `tests/api/test_mistake_routes.py` — Endpoint tests (15 tests)
- [ ] Web component tests (15 tests)

---

## Phase 2: AI Mock Test Engine + Predictive Analytics

**Timeline:** 3 sprints (6 weeks)
**Dependencies:** Phase 0.2 (task queue), Phase 1.1 (revision engine)

### 2.1 AI Mock Test Engine (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/mock_test_generator.py` — 180Q NEET-pattern generation
- [ ] `services/adaptive_difficulty.py` — IRT-based difficulty adjustment
- [ ] `services/negative_marking_analyzer.py` — Guess pattern detection
- [ ] `services/anti_cheat_monitor.py` — Tab switch, focus loss tracking
- [ ] `services/question_bank_manager.py` — Question pool management
- [ ] `api/v1/routes/mock_tests.py` — 8 endpoints
- [ ] `controllers/mock_test_controller.py`

**Frontend:**
- [ ] `features/mock-test/components/mock-test-setup.tsx`
- [ ] `features/mock-test/components/mock-test-player.tsx` — Full-screen player
- [ ] `features/mock-test/components/omr-sheet.tsx` — 180Q grid
- [ ] `features/mock-test/components/question-navigator.tsx`
- [ ] `features/mock-test/components/mock-test-results.tsx`
- [ ] `features/mock-test/components/difficulty-indicator.tsx`
- [ ] `features/mock-test/components/anti-cheat-banner.tsx`
- [ ] `features/mock-test/hooks/use-mock-test.ts`
- [ ] `features/mock-test/hooks/use-adaptive-difficulty.ts`
- [ ] `features/mock-test/hooks/use-anti-cheat.ts`
- [ ] `features/mock-test/api.ts`

**Database:**
- [ ] `supabase/migrations/20260521000000_mock_test_engine.sql`
  - `mock_tests` (test_type, difficulty_profile, tab_switches, focus_loss)
  - `mock_test_questions` (question_order, difficulty_at_delivery, flagged)
  - `anti_cheat_events` (event_type, event_data JSONB)
  - `difficulty_profiles` (easy/medium/hard ratios, subject weights)

**Tests:**
- [ ] `tests/services/test_mock_test_generator.py` — Subject balance, difficulty (15 tests)
- [ ] `tests/services/test_adaptive_difficulty.py` — IRT calibration (12 tests)
- [ ] `tests/services/test_anti_cheat_monitor.py` — Detection logic (10 tests)
- [ ] `tests/api/test_mock_test_routes.py` — Full flow tests (15 tests)
- [ ] E2E: Full 180Q mock test flow (Playwright)
- [ ] Web component tests (20 tests)

### 2.2 Predictive Analytics Dashboard (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/rank_predictor.py` — Score → NEET rank mapping
- [ ] `services/score_predictor.py` — Multi-feature regression (upgrade from heuristic)
- [ ] `services/burnout_detector.py` — Decline detection, alert generation
- [ ] `services/learning_velocity.py` — Weekly velocity computation
- [ ] `services/revision_efficiency.py` — Retention × speed scoring
- [ ] `api/v1/routes/predictions.py` — 6 endpoints
- [ ] `controllers/predictions_controller.py`

**Frontend:**
- [ ] `features/predictions/components/rank-predictor.tsx`
- [ ] `features/predictions/components/score-predictor.tsx`
- [ ] `features/predictions/components/burnout-warning.tsx`
- [ ] `features/predictions/components/learning-velocity-chart.tsx`
- [ ] `features/predictions/components/revision-efficiency-chart.tsx`
- [ ] `features/predictions/components/prediction-confidence-band.tsx`
- [ ] `features/predictions/hooks/use-predictions.ts`
- [ ] `features/predictions/hooks/use-burnout-alert.ts`
- [ ] `features/predictions/api.ts`

**Database:**
- [ ] `supabase/migrations/20260522000000_predictive_analytics.sql`
  - `predictions` (type, value, confidence interval, features_snapshot)
  - `burnout_alerts` (level, trigger_factors, recommended_actions)
  - `velocity_records` (weekly chapters, study_minutes, trend)
  - `efficiency_records` (items reviewed/retained, time per item)

**Tests:**
- [ ] `tests/services/test_score_predictor.py` — Regression accuracy (12 tests)
- [ ] `tests/services/test_burnout_detector.py` — Threshold detection (10 tests)
- [ ] `tests/services/test_learning_velocity.py` — Trend detection (8 tests)
- [ ] `tests/api/test_prediction_routes.py` — Endpoint tests (12 tests)
- [ ] Web component tests (15 tests)

---

## Phase 3: Knowledge Graph Engine + AI NotebookLM

**Timeline:** 4 sprints (8 weeks)
**Dependencies:** Phase 0.3 (vector pipeline), Phase 0.4 (realtime)

### 3.1 Knowledge Graph Engine (PLANNED → ENTERPRISE)

**Backend:**
- [ ] `services/graph_builder.py` — Build graph from syllabus
- [ ] `services/prerequisite_resolver.py` — Topological sort
- [ ] `services/concept_traverser.py` — BFS/DFS/shortest-path
- [ ] `services/relationship_engine.py` — Embedding similarity relationships
- [ ] `services/learning_path_generator.py` — Optimal path through graph
- [ ] `api/v1/routes/knowledge_graph.py` — 7 endpoints
- [ ] `controllers/knowledge_graph_controller.py`

**Frontend:**
- [ ] `features/knowledge-graph/components/concept-map.tsx` — @xyflow/react force-directed
- [ ] `features/knowledge-graph/components/prerequisite-chain.tsx`
- [ ] `features/knowledge-graph/components/concept-detail-panel.tsx`
- [ ] `features/knowledge-graph/components/learning-path-viewer.tsx`
- [ ] `features/knowledge-graph/components/relationship-explorer.tsx`
- [ ] `features/knowledge-graph/hooks/use-concept-graph.ts`
- [ ] `features/knowledge-graph/hooks/use-learning-path.ts`
- [ ] `features/knowledge-graph/api.ts`

**Database:**
- [ ] `supabase/migrations/20260523000000_knowledge_graph.sql`
  - `concepts` (name, type, difficulty, embedding_id)
  - `concept_relationships` (source, target, type, strength)
  - `prerequisites` (concept_id, prerequisite_id, is_required, priority)
  - `learning_paths` (target_concept, path_nodes JSONB, estimated_hours)

**Tests:**
- [ ] `tests/services/test_graph_builder.py` — Graph construction (12 tests)
- [ ] `tests/services/test_prerequisite_resolver.py` — Topological sort (10 tests)
- [ ] `tests/services/test_concept_traverser.py` — BFS/DFS/path (12 tests)
- [ ] `tests/services/test_relationship_engine.py` — Similarity (8 tests)
- [ ] `tests/api/test_knowledge_graph_routes.py` — Endpoint tests (15 tests)
- [ ] Web component tests (15 tests)

### 3.2 AI NotebookLM System (NOT STARTED → ENTERPRISE)

**Backend:**
- [ ] `services/document_processor.py` — PDF/text/audio ingestion
- [ ] `services/summarizer.py` — AI-generated summaries
- [ ] `services/flashcard_generator.py` — Auto flashcards from content
- [ ] `services/concept_mapper.py` — Concept graph from documents
- [ ] `services/contextual_search.py` — RAG-based semantic search
- [ ] `services/quiz_from_notes.py` — Auto-generate quizzes from notes
- [ ] `api/v1/routes/notebooklm.py` — 8 endpoints
- [ ] `controllers/notebooklm_controller.py`

**Frontend:**
- [ ] `features/notebooklm/components/document-upload.tsx`
- [ ] `features/notebooklm/components/summary-viewer.tsx`
- [ ] `features/notebooklm/components/flashcard-generator.tsx`
- [ ] `features/notebooklm/components/concept-map-viewer.tsx`
- [ ] `features/notebooklm/components/semantic-search.tsx`
- [ ] `features/notebooklm/components/quiz-from-notes.tsx`
- [ ] `features/notebooklm/components/notebook-dashboard.tsx`
- [ ] `features/notebooklm/hooks/use-document-processing.ts`
- [ ] `features/notebooklm/hooks/use-semantic-search.ts`
- [ ] `features/notebooklm/api.ts`

**Database:**
- [ ] `supabase/migrations/20260524000000_notebooklm.sql`
  - `notebooks` (name, description, document_count)
  - `notebook_documents` (type, file_path, chunk_count, embedding_status)
  - `document_chunks` (content, embedding_id, chunk_order)
  - `notebook_summaries` (summary_text, generated_by, model_version)
  - `notebook_flashcards` (front, back, difficulty, source_chunk)

**Tests:**
- [ ] `tests/services/test_document_processor.py` — Ingestion pipeline (12 tests)
- [ ] `tests/services/test_summarizer.py` — Summary quality (10 tests)
- [ ] `tests/services/test_flashcard_generator.py` — Card generation (8 tests)
- [ ] `tests/services/test_semantic_search.py` — RAG accuracy (12 tests)
- [ ] `tests/api/test_notebooklm_routes.py` — Endpoint tests (15 tests)
- [ ] Web component tests (20 tests)

---

## Phase 4: AI Study Twin + Voice Tutor

**Timeline:** 4 sprints (8 weeks)
**Dependencies:** Phase 1 (revision + mistakes), Phase 2 (predictions), Phase 3 (knowledge graph)

### 4.1 AI Study Twin (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/study_twin.py` — Twin orchestration
- [ ] `services/habit_learner.py` — Study pattern recognition
- [ ] `services/burnout_predictor.py` — Twin-specific burnout model
- [ ] `services/teaching_style_adapter.py` — Adaptive teaching
- [ ] `services/daily_path_generator.py` — Adaptive daily learning path
- [ ] `services/mood_tracker.py` — Productivity + mood correlation
- [ ] `services/long_term_memory.py` — Vector-based learning history
- [ ] `api/v1/routes/study_twin.py` — 8 endpoints
- [ ] `controllers/study_twin_controller.py`

**Frontend:**
- [ ] `features/study-twin/components/twin-dashboard.tsx`
- [ ] `features/study-twin/components/habit-insights.tsx`
- [ ] `features/study-twin/components/daily-path.tsx`
- [ ] `features/study-twin/components/mood-tracker.tsx`
- [ ] `features/study-twin/components/teaching-style.tsx`
- [ ] `features/study-twin/components/memory-timeline.tsx`
- [ ] `features/study-twin/components/twin-chat.tsx`
- [ ] `features/study-twin/hooks/use-twin.ts`
- [ ] `features/study-twin/hooks/use-habits.ts`
- [ ] `features/study-twin/api.ts`

**Database:**
- [ ] `supabase/migrations/20260525000000_study_twin.sql`
  - `twin_profiles` (learning_style, habit_patterns, mood_baseline)
  - `habit_records` (study_session, focus_score, productivity_score)
  - `twin_memories` (vector_embedding, memory_type, recalled_count)
  - `daily_paths` (path_nodes, completion_status, adaptation_reason)
  - `mood_records` (mood_score, energy_level, study_quality)

**Tests:**
- [ ] `tests/services/test_study_twin.py` — Twin orchestration (15 tests)
- [ ] `tests/services/test_habit_learner.py` — Pattern recognition (12 tests)
- [ ] `tests/services/test_teaching_style_adapter.py` — Adaptation (10 tests)
- [ ] `tests/services/test_long_term_memory.py` — Vector memory (10 tests)
- [ ] `tests/api/test_study_twin_routes.py` — Endpoint tests (15 tests)
- [ ] Web component tests (20 tests)

### 4.2 AI Voice Tutor (NOT STARTED → ENTERPRISE)

**Backend:**
- [ ] `services/voice_tutor.py` — Voice tutor orchestration
- [ ] `services/speech_to_text.py` — STT pipeline (Whisper/OpenAI)
- [ ] `services/text_to_speech.py` — TTS pipeline (ElevenLabs/OpenAI)
- [ ] `services/voice_quiz.py` — Voice-based quiz delivery
- [ ] `services/pronunciation_checker.py` — Pronunciation scoring
- [ ] `services/emotion_detector.py` — Voice emotion analysis
- [ ] `api/v1/routes/voice_tutor.py` — WebSocket + REST endpoints
- [ ] `controllers/voice_tutor_controller.py`

**Frontend:**
- [ ] `features/voice-tutor/components/voice-chat.tsx` — Streaming audio
- [ ] `features/voice-tutor/components/voice-quiz.tsx`
- [ ] `features/voice-tutor/components/pronunciation-feedback.tsx`
- [ ] `features/voice-tutor/components/emotion-indicator.tsx`
- [ ] `features/voice-tutor/components/language-selector.tsx`
- [ ] `features/voice-tutor/hooks/use-voice-session.ts`
- [ ] `features/voice-tutor/hooks/use-speech-recognition.ts`
- [ ] `features/voice-tutor/api.ts`

**Database:**
- [ ] `supabase/migrations/20260526000000_voice_tutor.sql`
  - `voice_sessions` (language, duration, transcription_status)
  - `voice_transcriptions` (text, confidence, emotion_tags)
  - `pronunciation_records` (word, expected_phoneme, actual_score)
  - `voice_quiz_responses` (question_audio, response_audio, accuracy)

**Tests:**
- [ ] `tests/services/test_speech_to_text.py` — STT accuracy (10 tests)
- [ ] `tests/services/test_text_to_speech.py` — TTS quality (8 tests)
- [ ] `tests/services/test_voice_quiz.py` — Quiz flow (10 tests)
- [ ] `tests/services/test_pronunciation_checker.py` — Scoring (8 tests)
- [ ] `tests/api/test_voice_tutor_routes.py` — Endpoint tests (12 tests)
- [ ] Web component tests (15 tests)

---

## Phase 5: Gamification + Productivity + Career

**Timeline:** 3 sprints (6 weeks)
**Dependencies:** Phase 2 (mock tests), Phase 4 (study twin)

### 5.1 NEET Battle Arena (NOT STARTED → ENTERPRISE)

**Backend:**
- [ ] `services/matchmaking.py` — ELO-based matchmaking
- [ ] `services/battle_engine.py` — 1v1 quiz battle logic
- [ ] `services/leaderboard.py` — Seasonal leaderboards
- [ ] `services/clan_manager.py` — Group/clan system
- [ ] `services/xp_system.py` — XP + achievement tracking
- [ ] `services/anti_cheat_battle.py` — Battle-specific anti-cheat
- [ ] `api/v1/routes/battle.py` — WebSocket + REST
- [ ] `controllers/battle_controller.py`

**Frontend:**
- [ ] `features/battle/components/battle-lobby.tsx`
- [ ] `features/battle/components/battle-arena.tsx` — Live battle UI
- [ ] `features/battle/components/leaderboard.tsx`
- [ ] `features/battle/components/clan-view.tsx`
- [ ] `features/battle/components/achievement-gallery.tsx`
- [ ] `features/battle/components/xp-progress.tsx`
- [ ] `features/battle/hooks/use-battle.ts`
- [ ] `features/battle/hooks/use-matchmaking.ts`
- [ ] `features/battle/api.ts`

**Database:**
- [ ] `supabase/migrations/20260527000000_battle_arena.sql`
  - `battles` (player1, player2, status, winner, elo_change)
  - `battle_questions` (question_id, player1_answer, player2_answer, time_taken)
  - `leaderboards` (season, player_id, rank, elo_score)
  - `clans` (name, description, member_count, created_by)
  - `clan_members` (clan_id, user_id, role, joined_at)
  - `achievements` (code, title, icon, unlock_condition)
  - `user_achievements` (user_id, achievement_id, unlocked_at)

**Tests:**
- [ ] `tests/services/test_matchmaking.py` — ELO matching (12 tests)
- [ ] `tests/services/test_battle_engine.py` — Battle logic (15 tests)
- [ ] `tests/services/test_leaderboard.py` — Ranking (10 tests)
- [ ] `tests/services/test_xp_system.py` — XP calculation (8 tests)
- [ ] `tests/api/test_battle_routes.py` — Endpoint tests (15 tests)
- [ ] E2E: Full battle flow (Playwright)
- [ ] Web component tests (20 tests)

### 5.2 Productivity & Focus System (NOT STARTED → ENTERPRISE)

**Backend:**
- [ ] `services/pomodoro_ai.py` — AI-optimized Pomodoro
- [ ] `services/focus_analytics.py` — Focus session analytics
- [ ] `services/distraction_detector.py` — Pattern detection
- [ ] `services/study_music.py` — Ambient music generation
- [ ] `services/dopamine_tracker.py` — Reward scheduling
- [ ] `api/v1/routes/productivity.py` — 6 endpoints
- [ ] `controllers/productivity_controller.py`

**Frontend:**
- [ ] `features/productivity/components/pomodoro-timer.tsx`
- [ ] `features/productivity/components/focus-dashboard.tsx`
- [ ] `features/productivity/components/distraction-blocker.tsx`
- [ ] `features/productivity/components/study-music-player.tsx`
- [ ] `features/productivity/components/dopamine-tracker.tsx`
- [ ] `features/productivity/components/burnout-prevention.tsx`
- [ ] `features/productivity/hooks/use-pomodoro.ts`
- [ ] `features/productivity/hooks/use-focus.ts`
- [ ] `features/productivity/api.ts`

**Database:**
- [ ] `supabase/migrations/20260528000000_productivity.sql`
  - `pomodoro_sessions` (duration, interruptions, focus_score)
  - `focus_records` (session_id, distraction_count, productivity_score)
  - `distraction_logs` (type, timestamp, duration, context)
  - `dopamine_records` (reward_type, satisfaction_score, timestamp)

**Tests:**
- [ ] `tests/services/test_pomodoro_ai.py` — Optimization (10 tests)
- [ ] `tests/services/test_focus_analytics.py` — Analytics (8 tests)
- [ ] `tests/services/test_distraction_detector.py` — Detection (8 tests)
- [ ] `tests/api/test_productivity_routes.py` — Endpoint tests (10 tests)
- [ ] Web component tests (15 tests)

### 5.3 AI Career Guidance (NOT STARTED → ENTERPRISE)

**Backend:**
- [ ] `services/college_predictor.py` — College prediction model
- [ ] `services/career_mapper.py` — Career path mapping
- [ ] `services/scholarship_finder.py` — Scholarship matching
- [ ] `services/strategy_optimizer.py` — Exam strategy
- [ ] `services/counseling_ai.py` — AI counseling prompts
- [ ] `api/v1/routes/career.py` — 6 endpoints
- [ ] `controllers/career_controller.py`

**Frontend:**
- [ ] `features/career/components/college-predictor.tsx`
- [ ] `features/career/components/career-path-viewer.tsx`
- [ ] `features/career/components/scholarship-finder.tsx`
- [ ] `features/career/components/strategy-optimizer.tsx`
- [ ] `features/career/components/counseling-chat.tsx`
- [ ] `features/career/hooks/use-career.ts`
- [ ] `features/career/api.ts`

**Database:**
- [ ] `supabase/migrations/20260529000000_career_guidance.sql`
  - `college_data` (name, cutoff_rank, category, state, fees)
  - `career_paths` (name, description, required_score, growth_rate)
  - `scholarships` (name, eligibility, amount, deadline)
  - `career_predictions` (user_id, predicted_colleges, confidence)

**Tests:**
- [ ] `tests/services/test_college_predictor.py` — Prediction (10 tests)
- [ ] `tests/services/test_career_mapper.py` — Mapping (8 tests)
- [ ] `tests/services/test_scholarship_finder.py` — Matching (8 tests)
- [ ] `tests/api/test_career_routes.py` — Endpoint tests (10 tests)
- [ ] Web component tests (12 tests)

---

## Phase 6: Visual Learning + Research + Voice

**Timeline:** 3 sprints (6 weeks)
**Dependencies:** Phase 0.3 (vector pipeline), Phase 3 (knowledge graph)

### 6.1 AI Visual Learning Engine (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/diagram_generator.py` — AI diagram generation
- [ ] `services/biology_animator.py` — Biology system animations
- [ ] `services/chemistry_visualizer.py` — Reaction visualization
- [ ] `services/physics_simulator.py` — Physics simulations
- [ ] `services/concept_illustrator.py` — Concept illustrations
- [ ] `api/v1/routes/visual.py` — 6 endpoints
- [ ] `controllers/visual_controller.py`

**Frontend:**
- [ ] `features/visual/components/diagram-viewer.tsx`
- [ ] `features/visual/components/biology-animation.tsx`
- [ ] `features/visual/components/chemistry-reactor.tsx`
- [ ] `features/visual/components/physics-simulator.tsx`
- [ ] `features/visual/components/concept-illustrator.tsx`
- [ ] `features/visual/components/3d-model-viewer.tsx`
- [ ] `features/visual/hooks/use-visual.ts`
- [ ] `features/visual/api.ts`

**Database:**
- [ ] `supabase/migrations/20260530000000_visual_learning.sql`
  - `visual_assets` (type, chapter_id, file_path, generated_by)
  - `diagram_cache` (concept_hash, svg_data, model_version)
  - `animation_sequences` (concept_id, frames_json, duration)

**Tests:**
- [ ] `tests/services/test_diagram_generator.py` — Generation (10 tests)
- [ ] `tests/services/test_biology_animator.py` — Animation (8 tests)
- [ ] `tests/services/test_physics_simulator.py` — Simulation (8 tests)
- [ ] `tests/api/test_visual_routes.py` — Endpoint tests (10 tests)
- [ ] Web component tests (15 tests)

### 6.2 AI Research & Trend System (NOT STARTED → ENTERPRISE)

**Backend:**
- [ ] `services/trend_analyzer.py` — NEET trend analysis
- [ ] `services/pattern_detector.py` — Question pattern detection
- [ ] `services/importance_predictor.py` — Topic importance prediction
- [ ] `services/weightage_forecaster.py` — Chapter weight forecasting
- [ ] `services/pyq_intelligence.py` — PYQ analysis engine
- [ ] `api/v1/routes/research.py` — 6 endpoints
- [ ] `controllers/research_controller.py`

**Frontend:**
- [ ] `features/research/components/trend-dashboard.tsx`
- [ ] `features/research/components/pattern-viewer.tsx`
- [ ] `features/research/components/importance-predictor.tsx`
- [ ] `features/research/components/weightage-forecast.tsx`
- [ ] `features/research/components/pyq-intelligence.tsx`
- [ ] `features/research/hooks/use-research.ts`
- [ ] `features/research/api.ts`

**Database:**
- [ ] `supabase/migrations/20260531000000_research_trends.sql`
  - `pyq_records` (year, question_id, topic, difficulty, marks)
  - `trend_records` (topic, frequency, year_over_year_change)
  - `importance_scores` (topic, score, prediction_confidence)
  - `weightage_forecasts` (chapter, predicted_weight, confidence)

**Tests:**
- [ ] `tests/services/test_trend_analyzer.py` — Trend analysis (10 tests)
- [ ] `tests/services/test_pattern_detector.py` — Pattern detection (10 tests)
- [ ] `tests/services/test_importance_predictor.py` — Prediction (8 tests)
- [ ] `tests/api/test_research_routes.py` — Endpoint tests (10 tests)
- [ ] Web component tests (12 tests)

---

## Phase 7: Multi-Tenant B2B + Marketplace

**Timeline:** 4 sprints (8 weeks)
**Dependencies:** Phase 0.5 (observability), Phase 0.7 (feature flags)

### 7.1 Enterprise Multi-Tenant B2B (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/tenant_manager.py` — Tenant lifecycle
- [ ] `services/institute_dashboard.py` — Institute analytics
- [ ] `services/teacher_tools.py` — Teacher classroom management
- [ ] `services/billing.py` — Subscription management
- [ ] `services/branding.py` — Custom branding
- [ ] `services/tenant_isolation.py` — Runtime tenant context
- [ ] `api/v1/routes/tenant.py` — 10 endpoints
- [ ] `controllers/tenant_controller.py`

**Frontend:**
- [ ] `features/tenant/components/institute-dashboard.tsx`
- [ ] `features/tenant/components/teacher-portal.tsx`
- [ ] `features/tenant/components/classroom-manager.tsx`
- [ ] `features/tenant/components/billing-portal.tsx`
- [ ] `features/tenant/components/branding-settings.tsx`
- [ ] `features/tenant/components/usage-analytics.tsx`
- [ ] `features/tenant/components/tenant-switcher.tsx`
- [ ] `features/tenant/hooks/use-tenant.ts`
- [ ] `features/tenant/api.ts`

**Database:**
- [ ] `supabase/migrations/20260601000000_multi_tenant.sql`
  - `tenants` (name, subdomain, plan, billing_email, branding_json)
  - `tenant_settings` (tenant_id, key, value)
  - `subscriptions` (tenant_id, plan, status, expires_at)
  - `usage_records` (tenant_id, metric, value, period)

**Tests:**
- [ ] `tests/services/test_tenant_manager.py` — Lifecycle (12 tests)
- [ ] `tests/services/test_tenant_isolation.py` — Isolation (15 tests)
- [ ] `tests/services/test_billing.py` — Subscription (10 tests)
- [ ] `tests/api/test_tenant_routes.py` — Endpoint tests (15 tests)
- [ ] Web component tests (20 tests)

### 7.2 AI Plugin & Extension Marketplace (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/plugin_registry.py` — Plugin discovery
- [ ] `services/plugin_sandbox.py` — Sandboxed execution
- [ ] `services/plugin_sdk.py` — SDK for plugin developers
- [ ] `services/marketplace.py` — Plugin marketplace
- [ ] `services/plugin_governance.py` — Plugin approval/review
- [ ] `api/v1/routes/plugins.py` — 8 endpoints
- [ ] `controllers/plugin_controller.py`

**Frontend:**
- [ ] `features/plugins/components/marketplace.tsx`
- [ ] `features/plugins/components/plugin-card.tsx`
- [ ] `features/plugins/components/plugin-detail.tsx`
- [ ] `features/plugins/components/plugin-installer.tsx`
- [ ] `features/plugins/components/plugin-manager.tsx`
- [ ] `features/plugins/components/sdk-docs.tsx`
- [ ] `features/plugins/hooks/use-plugins.ts`
- [ ] `features/plugins/api.ts`

**Database:**
- [ ] `supabase/migrations/20260602000000_plugin_marketplace.sql`
  - `plugins` (name, version, author, description, manifest_json)
  - `plugin_installs` (plugin_id, user_id, installed_at, status)
  - `plugin_reviews` (plugin_id, user_id, rating, review_text)
  - `plugin_permissions` (plugin_id, permission, granted)

**Tests:**
- [ ] `tests/services/test_plugin_registry.py` — Registry (10 tests)
- [ ] `tests/services/test_plugin_sandbox.py` — Sandboxing (12 tests)
- [ ] `tests/services/test_marketplace.py` — Marketplace (8 tests)
- [ ] `tests/api/test_plugin_routes.py` — Endpoint tests (12 tests)
- [ ] Web component tests (15 tests)

---

## Phase 8: Offline-First PWA + Real-Time Classroom

**Timeline:** 3 sprints (6 weeks)
**Dependencies:** Phase 0.4 (realtime), Phase 0.1 (event bus)

### 8.1 Offline-First PWA (BASIC → ENTERPRISE)

**Backend:**
- [ ] `services/sync_engine.py` — CRDT-based sync
- [ ] `services/conflict_resolver.py` — Sync conflict resolution
- [ ] `services/offline_queue.py` — Offline operation queue
- [ ] `services/edge_cache.py` — Edge CDN caching
- **Files:** Upgrade existing `features/offline/` with service worker

**Frontend:**
- [ ] Serwist service worker setup
- [ ] `public/manifest.json` — PWA manifest
- [ ] `features/offline/components/offline-indicator.tsx` — Upgrade existing
- [ ] `features/offline/hooks/use-sync.ts` — CRDT sync hook
- [ ] `features/offline/hooks/use-offline-queue.ts` — Queue management
- [ ] `features/offline/service-worker.ts` — Serwist worker
- [ ] Offline-first quiz, notes, flashcards

**Tests:**
- [ ] `tests/services/test_sync_engine.py` — CRDT sync (12 tests)
- [ ] `tests/services/test_conflict_resolver.py` — Resolution (10 tests)
- [ ] `tests/services/test_offline_queue.py` — Queue (8 tests)
- [ ] E2E: Offline flow tests (Playwright with offline mode)
- [ ] Web component tests (15 tests)

### 8.2 Real-Time AI Classroom (NOT STARTED → ENTERPRISE)

**Backend:**
- [ ] `services/classroom_manager.py` — Classroom lifecycle
- [ ] `services/live_session.py` — Live session management
- [ ] `services/ai_whiteboard.py` — Collaborative whiteboard
- [ ] `services/live_quiz_engine.py` — Real-time quiz
- [ ] `services/doubt_resolver.py` — AI doubt resolution
- [ ] `services/annotation_engine.py` — Real-time annotations
- [ ] `services/teacher_moderation.py` — Teacher tools
- [ ] `api/v1/websockets/classroom.py` — WebSocket handlers
- [ ] `controllers/classroom_controller.py`

**Frontend:**
- [ ] `features/classroom/components/classroom-lobby.tsx`
- [ ] `features/classroom/components/live-session.tsx`
- [ ] `features/classroom/components/ai-whiteboard.tsx`
- [ ] `features/classroom/components/live-quiz.tsx`
- [ ] `features/classroom/components/shared-notes.tsx`
- [ ] `features/classroom/components/doubt-resolver.tsx`
- [ ] `features/classroom/components/annotation-layer.tsx`
- [ ] `features/classroom/components/teacher-panel.tsx`
- [ ] `features/classroom/components/classroom-analytics.tsx`
- [ ] `features/classroom/hooks/use-classroom.ts`
- [ ] `features/classroom/hooks/use-websocket.ts`
- [ ] `features/classroom/api.ts`

**Database:**
- [ ] `supabase/migrations/20260603000000_realtime_classroom.sql`
  - `classrooms` (name, host_id, status, max_students)
  - `classroom_sessions` (classroom_id, started_at, ended_at)
  - `classroom_members` (session_id, user_id, role, joined_at)
  - `whiteboard_events` (session_id, event_type, data_json)
  - `live_quiz_sessions` (session_id, question_id, responses_json)
  - `doubt_requests` (session_id, user_id, question_text, resolved)

**Tests:**
- [ ] `tests/services/test_classroom_manager.py` — Lifecycle (12 tests)
- [ ] `tests/services/test_live_session.py` — Session management (10 tests)
- [ ] `tests/services/test_ai_whiteboard.py` — Whiteboard (8 tests)
- [ ] `tests/services/test_live_quiz_engine.py` — Live quiz (10 tests)
- [ ] `tests/api/test_classroom_routes.py` — Endpoint tests (15 tests)
- [ ] WebSocket tests (10 tests)
- [ ] Web component tests (20 tests)

---

## Phase 9: Future Features + Polish

**Timeline:** 4 sprints (8 weeks)
**Dependencies:** All previous phases

### 9.1 AI Autonomous Agents
- [ ] `services/agent_orchestrator.py` — Multi-agent coordination
- [ ] `services/study_agent.py` — Autonomous study planning
- [ ] `services/research_agent.py` — Autonomous research
- [ ] `services/review_agent.py` — Autonomous review scheduling

### 9.2 AI-Generated Courses
- [ ] `services/course_generator.py` — Full course generation
- [ ] `services/curriculum_mapper.py` — Curriculum alignment
- [ ] `services/assessment_builder.py` — Auto assessment creation

### 9.3 VR/AR Features
- [ ] `features/vr/components/vr-classroom.tsx`
- [ ] `features/ar/components/ar-biology.tsx`
- [ ] WebXR integration

### 9.4 Wearable Integration
- [ ] `services/wearable_sync.py` — Health data sync
- [ ] `services/focus_from_biometrics.py` — Brainwave focus tracking

### 9.5 Digital Twin Classrooms
- [ ] `services/digital_twin.py` — Classroom simulation
- [ ] `services/autonomous_orchestration.py` — Autonomous scheduling

---

## Implementation Summary

| Phase | Features | Sprints | Weeks | Services | Routes | Components | DB Tables | Tests |
|-------|----------|---------|-------|----------|--------|------------|-----------|-------|
| **0** | Infrastructure | 2 | 4 | 12 | 0 | 0 | 4 | 60 |
| **1** | Revision + Mistakes | 3 | 6 | 9 | 2 | 14 | 8 | 90 |
| **2** | Mock Test + Predictions | 3 | 6 | 10 | 2 | 17 | 4 | 85 |
| **3** | Knowledge Graph + NotebookLM | 4 | 8 | 12 | 2 | 17 | 9 | 110 |
| **4** | Study Twin + Voice | 4 | 8 | 14 | 2 | 15 | 8 | 105 |
| **5** | Battle + Productivity + Career | 3 | 6 | 12 | 3 | 20 | 11 | 100 |
| **6** | Visual + Research | 3 | 6 | 9 | 2 | 12 | 7 | 80 |
| **7** | B2B + Marketplace | 4 | 8 | 12 | 2 | 17 | 8 | 95 |
| **8** | Offline + Classroom | 3 | 6 | 9 | 2 | 19 | 6 | 105 |
| **9** | Future + Polish | 4 | 8 | 10 | 2 | 5 | 3 | 50 |
| **TOTAL** | **20 features** | **33** | **66** | **111** | **17** | **136** | **68** | **880** |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AI API costs exceed budget | High | High | Token caps, caching, fallback to local models |
| Real-time scalability issues | Medium | High | WebSocket sharding, Supabase Realtime fallback |
| Vector DB performance degradation | Medium | Medium | pgvector indexing, chunk size optimization |
| Feature scope creep | High | Medium | Strict phase boundaries, MVP-first approach |
| Test coverage gaps | Medium | Medium | Enforce 80%+ coverage per phase in CI |
| Database migration conflicts | Low | High | Sequential migration numbering, rollback scripts |
| Frontend bundle size bloat | Medium | Medium | Dynamic imports, code splitting per feature |
| Multi-tenant data leaks | Low | Critical | Automated isolation tests, RLS enforcement |

---

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| API test coverage | 90%+ | pytest --cov |
| Web test coverage | 80%+ | vitest --coverage |
| E2E test coverage | All critical flows | Playwright specs |
| API response time p95 | < 200ms | OpenTelemetry traces |
| Frontend load time | < 2s | Lighthouse |
| Feature completeness | 20/20 features | Feature audit checklist |
| Zero critical security issues | 0 | Trivy + manual review |
| Zero data leaks (multi-tenant) | 0 | Isolation test suite |
