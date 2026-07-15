-- StudyOS — Performance indexes for hot query patterns.
-- Covers progress, dashboard, notes, quiz, mistakes, roadmap, streaks,
-- token usage, annotations, achievements, and vector search.

-- ============================================================================
-- 1. Progress lookups: completions by profile + subtopic
--    Already covered by subtopic_completions_live_uidx (unique on profile_id, subtopic_id)
--    and subtopic_completions_profile_time_idx (profile_id, completed_at DESC).
--    Adding a covering index for subtopic-first lookups (e.g. "who completed this?").
-- ============================================================================
CREATE INDEX IF NOT EXISTS subtopic_completions_subtopic_profile_idx
    ON public.subtopic_completions (subtopic_id, profile_id)
    WHERE deleted_at IS NULL;

-- ============================================================================
-- 2. Dashboard aggregates: completions by profile with date range
--    Query pattern: SELECT COUNT(*) FROM subtopic_completions
--      WHERE profile_id = $1 AND completed_at BETWEEN $2 AND $3
--    Already covered by subtopic_completions_profile_time_idx.
--    Adding index on user_chapter_progress for dashboard chapter overview.
-- ============================================================================
CREATE INDEX IF NOT EXISTS user_chapter_progress_profile_pct_idx
    ON public.user_chapter_progress (profile_id, progress_pct)
    WHERE deleted_at IS NULL;

-- ============================================================================
-- 3. Notes listing: notes by profile + chapter + status
--    Query pattern: SELECT * FROM notes WHERE profile_id = $1
--      AND (chapter_id = $2 OR chapter_id IS NULL) AND status = $3
-- ============================================================================
CREATE INDEX IF NOT EXISTS notes_profile_chapter_status_live_idx
    ON public.notes (profile_id, chapter_id, status)
    WHERE deleted_at IS NULL;

-- Partial index for notes awaiting processing (common admin/dashboard query)
CREATE INDEX IF NOT EXISTS notes_processing_pending_idx
    ON public.notes (profile_id, created_at DESC)
    WHERE deleted_at IS NULL AND status IN ('uploading', 'processing');

-- ============================================================================
-- 4. Search: notes by profile + title (full text)
--    Query pattern: SELECT * FROM notes WHERE profile_id = $1
--      AND to_tsvector(title) @@ plainto_tsquery($2)
-- ============================================================================
CREATE INDEX IF NOT EXISTS notes_title_tsv_idx
    ON public.notes
    USING GIN (profile_id, to_tsvector('simple', title))
    WHERE deleted_at IS NULL;

-- ============================================================================
-- 5. Quiz history: sessions by profile + date range
--    Already covered by quiz_sessions_profile_live_idx (profile_id, started_at DESC).
--    Adding index for completed sessions only (most common dashboard query).
-- ============================================================================
CREATE INDEX IF NOT EXISTS quiz_sessions_completed_profile_idx
    ON public.quiz_sessions (profile_id, completed_at DESC)
    WHERE deleted_at IS NULL AND completed_at IS NOT NULL;

-- Index for in-progress sessions (active quiz recovery)
CREATE INDEX IF NOT EXISTS quiz_sessions_in_progress_idx
    ON public.quiz_sessions (profile_id, started_at DESC)
    WHERE deleted_at IS NULL AND completed_at IS NULL;

-- ============================================================================
-- 6. Quiz responses: responses by session
--    Already covered by quiz_responses_session_idx.
--    Adding covering index for score calculation (session + correctness).
-- ============================================================================
CREATE INDEX IF NOT EXISTS quiz_responses_session_correct_idx
    ON public.quiz_responses (session_id, is_correct);

-- ============================================================================
-- 7. Mistake tracking: mistakes by profile + reviewed status
--    Already covered by mistake_log_reviewed_live_idx (profile_id, reviewed).
--    Adding index for unreviewed mistakes (review queue).
-- ============================================================================
CREATE INDEX IF NOT EXISTS mistake_log_unreviewed_idx
    ON public.mistake_log (profile_id, created_at DESC)
    WHERE deleted_at IS NULL AND reviewed = false;

-- Index for mistake frequency analysis (repeated mistakes)
CREATE INDEX IF NOT EXISTS mistake_log_question_reviewed_idx
    ON public.mistake_log (question_id, reviewed, review_count DESC)
    WHERE deleted_at IS NULL;

-- ============================================================================
-- 8. Roadmap lookups: active roadmap by profile
--    Already covered by roadmaps_profile_live_idx (profile_id, is_active).
--    Adding partial index for the single active roadmap per user.
-- ============================================================================
CREATE INDEX IF NOT EXISTS roadmaps_active_profile_idx
    ON public.roadmaps (profile_id, end_date DESC)
    WHERE deleted_at IS NULL AND is_active = true;

-- Roadmap items by status (kanban-style views)
CREATE INDEX IF NOT EXISTS roadmap_items_status_profile_idx
    ON public.roadmap_items (roadmap_id, status, sort_order)
    WHERE deleted_at IS NULL;

-- Overdue roadmap items (urgent dashboard widget)
CREATE INDEX IF NOT EXISTS roadmap_items_overdue_idx
    ON public.roadmap_items (target_date, status)
    WHERE deleted_at IS NULL AND status IN ('pending', 'in_progress');

-- ============================================================================
-- 9. Streak lookups: streak by profile
--    Query pattern: SELECT * FROM streaks WHERE profile_id = $1
-- ============================================================================
CREATE INDEX IF NOT EXISTS streaks_profile_idx
    ON public.streaks (profile_id);

-- Streak leaderboard (top users by current streak)
CREATE INDEX IF NOT EXISTS streaks_leaderboard_idx
    ON public.streaks (current_streak DESC, last_activity_date DESC);

-- ============================================================================
-- 10. Token usage: usage by profile + date range
--     Query pattern: SELECT * FROM ai_token_usage
--       WHERE profile_id = $1 AND date BETWEEN $2 AND $3
-- ============================================================================
CREATE INDEX IF NOT EXISTS ai_token_usage_profile_date_idx
    ON public.ai_token_usage (profile_id, date);

-- ============================================================================
-- 11. AI cost tracking: usage by profile + date
--     Query pattern: SELECT SUM(cost) FROM ai_token_usage
--       WHERE profile_id = $1 AND date >= $2
-- ============================================================================
CREATE INDEX IF NOT EXISTS ai_token_usage_cost_profile_idx
    ON public.ai_token_usage (profile_id, date, cost);

-- AI usage logs by profile + feature (cost breakdown by feature)
CREATE INDEX IF NOT EXISTS ai_usage_logs_profile_feature_idx
    ON public.ai_usage_logs (profile_id, feature, created_at DESC);

-- AI usage logs by profile + cost (spending analysis)
CREATE INDEX IF NOT EXISTS ai_usage_logs_profile_cost_idx
    ON public.ai_usage_logs (profile_id, cost_usd, created_at DESC);

-- ============================================================================
-- 12. Highlights/bookmarks: by note + profile
--     Already covered by highlights_note_live_idx (note_id, page_number).
--     Adding index for profile-level annotation history.
-- ============================================================================
CREATE INDEX IF NOT EXISTS highlights_profile_note_idx
    ON public.highlights (profile_id, note_id, created_at DESC)
    WHERE deleted_at IS NULL;

-- Bookmarks by profile (recent bookmarks widget)
CREATE INDEX IF NOT EXISTS bookmarks_profile_recent_idx
    ON public.bookmarks (profile_id, created_at DESC);

-- Personal notes by profile + note
CREATE INDEX IF NOT EXISTS personal_notes_profile_note_idx
    ON public.personal_notes (profile_id, note_id, created_at DESC)
    WHERE deleted_at IS NULL;

-- ============================================================================
-- 13. Achievements: user achievements by profile
--     Already covered by user_achievements_profile_idx (profile_id, unlocked_at DESC).
--     Adding index for achievement completion checks.
-- ============================================================================
CREATE INDEX IF NOT EXISTS user_achievements_achievement_idx
    ON public.user_achievements (achievement_id, unlocked_at DESC);

-- ============================================================================
-- 14. Vector search: note_embeddings with ivfflat for pgvector
--     Query pattern: SELECT * FROM note_embeddings
--       ORDER BY embedding <-> $1 LIMIT $2
-- ============================================================================

-- Ensure pgvector extension is available
CREATE EXTENSION IF NOT EXISTS vector;

-- IVFFlat index for cosine similarity search on embeddings
-- Lists = rows / 1000 (tune based on dataset size; 100 is good for ~100k rows)
CREATE INDEX IF NOT EXISTS note_embeddings_vector_ivfflat_idx
    ON public.note_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- HNSW index for faster approximate nearest neighbor (pgvector 0.5+)
-- Better recall than IVFFlat but higher build time and memory
CREATE INDEX IF NOT EXISTS note_embeddings_vector_hnsw_idx
    ON public.note_embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Composite index for scoped vector search (by note)
CREATE INDEX IF NOT EXISTS note_embeddings_note_chunk_idx
    ON public.note_embeddings (note_id, chunk_index);

-- ============================================================================
-- 15. Bulk import jobs: by profile + status
--     Query pattern: SELECT * FROM bulk_import_jobs
--       WHERE profile_id = $1 ORDER BY created_at DESC
-- ============================================================================
CREATE INDEX IF NOT EXISTS bulk_import_jobs_profile_status_idx
    ON public.bulk_import_jobs (profile_id, status, created_at DESC);

-- Active/pending import jobs (monitoring)
CREATE INDEX IF NOT EXISTS bulk_import_jobs_active_idx
    ON public.bulk_import_jobs (status, created_at DESC)
    WHERE status IN ('pending', 'processing');

-- ============================================================================
-- 16. Revision engine indexes (Phase 1.1 tables)
-- ============================================================================

-- Revision items due for review today
CREATE INDEX IF NOT EXISTS revision_items_due_review_idx
    ON public.revision_items (next_review, profile_id)
    WHERE next_review <= CURRENT_DATE;

-- Revision sessions by profile + completion
CREATE INDEX IF NOT EXISTS revision_sessions_completed_idx
    ON public.revision_sessions (profile_id, completed_at DESC)
    WHERE completed_at IS NOT NULL;

-- Retention records by revision item (model calibration)
CREATE INDEX IF NOT EXISTS retention_records_item_days_idx
    ON public.revision_records (revision_item_id, days_since_review);

-- ============================================================================
-- 17. Note mindmaps: by note
--     Already covered by note_mindmaps_note_idx.
-- ============================================================================

-- ============================================================================
-- 18. Chapters/topics: syllabus tree lookups
-- ============================================================================

-- Chapters by exam + subject (syllabus tree root)
CREATE INDEX IF NOT EXISTS chapters_exam_subject_idx
    ON public.chapters (exam_id, subject_id, position);

-- Topics by chapter (syllabus tree branch)
CREATE INDEX IF NOT EXISTS topics_chapter_position_idx
    ON public.topics (chapter_id, position);

-- Subtopics by topic (syllabus tree leaf)
CREATE INDEX IF NOT EXISTS subtopics_topic_position_idx
    ON public.subtopics (topic_id, position);

-- ============================================================================
-- 19. Profiles: lookup by exam type
-- ============================================================================
CREATE INDEX IF NOT EXISTS profiles_exam_type_idx
    ON public.profiles (exam_type);

-- ============================================================================
-- 20. Refresh sessions: by profile + expiry (session cleanup)
-- ============================================================================
CREATE INDEX IF NOT EXISTS refresh_sessions_profile_expiry_idx
    ON public.refresh_sessions (profile_id, expires_at DESC);

-- Expired sessions (cleanup job)
CREATE INDEX IF NOT EXISTS refresh_sessions_expired_idx
    ON public.refresh_sessions (expires_at)
    WHERE expires_at < NOW();

-- ============================================================================
-- 21. Auth credentials: by profile + email (login lookup)
-- ============================================================================
CREATE INDEX IF NOT EXISTS auth_credentials_profile_idx
    ON public.auth_credentials (profile_id);

CREATE UNIQUE INDEX IF NOT EXISTS auth_credentials_email_uidx
    ON public.auth_credentials (email);

-- ============================================================================
-- 22. Note versions: by note + version (version history)
--     Already covered by note_versions_note_idx.
--     Adding index for latest version lookup.
-- ============================================================================
CREATE INDEX IF NOT EXISTS note_versions_latest_idx
    ON public.note_versions (note_id, version DESC NULLS LAST);

-- ============================================================================
-- 23. Embedding store: vector search (global embeddings)
--     Already has HNSW index from vector_pipeline migration.
--     Adding IVFFlat as alternative.
-- ============================================================================
CREATE INDEX IF NOT EXISTS embedding_store_vector_ivfflat_idx
    ON public.embedding_store
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- 24. Chunk store: by source + status (embedding pipeline)
-- ============================================================================
CREATE INDEX IF NOT EXISTS chunk_store_source_status_idx
    ON public.chunk_store (source_id, embedding_status, chunk_index);

-- ============================================================================
-- 25. Search index: by document type + last searched
-- ============================================================================
CREATE INDEX IF NOT EXISTS search_index_type_searched_idx
    ON public.search_index (document_type, last_searched_at DESC)
    WHERE last_searched_at IS NOT NULL;
