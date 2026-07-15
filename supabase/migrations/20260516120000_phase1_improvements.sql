-- StudyOS — Phase 1: soft deletes, indexing strategy, AI token tracking.

-- ---------------------------------------------------------------------------
-- Soft delete helper function and trigger
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.studyos_soft_delete()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.deleted_at := now();
  NEW.deleted_by := COALESCE(
    NULLIF(current_setting('studyos.actor_id', TRUE), '')::uuid,
    NULL
  );
  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.studyos_soft_delete() IS 'BEFORE UPDATE: sets deleted_at when a row is soft-deleted.';

-- ---------------------------------------------------------------------------
-- Add soft delete columns to key tables (if not exists)
-- ---------------------------------------------------------------------------
ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS deleted_at timestamptz,
  ADD COLUMN IF NOT EXISTS deleted_by uuid REFERENCES public.profiles(id);

ALTER TABLE public.syllabus_exams
  ADD COLUMN IF NOT EXISTS deleted_at timestamptz,
  ADD COLUMN IF NOT EXISTS deleted_by uuid REFERENCES public.profiles(id);

ALTER TABLE public.syllabus_chapters
  ADD COLUMN IF NOT EXISTS deleted_at timestamptz,
  ADD COLUMN IF NOT EXISTS deleted_by uuid REFERENCES public.profiles(id);

ALTER TABLE public.syllabus_topics
  ADD COLUMN IF NOT EXISTS deleted_at timestamptz,
  ADD COLUMN IF NOT EXISTS deleted_by uuid REFERENCES public.profiles(id);

ALTER TABLE public.syllabus_subtopics
  ADD COLUMN IF NOT EXISTS deleted_at timestamptz,
  ADD COLUMN IF NOT EXISTS deleted_by uuid REFERENCES public.profiles(id);

-- ---------------------------------------------------------------------------
-- Performance indexes for common query patterns
-- ---------------------------------------------------------------------------

-- Profiles: email lookup (login), role filtering
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_profiles_app_role ON public.profiles(app_role) WHERE deleted_at IS NULL;

-- Syllabus: hierarchical lookups
CREATE INDEX IF NOT EXISTS idx_chapters_exam_id ON public.syllabus_chapters(exam_id, sort_order) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_topics_chapter_id ON public.syllabus_topics(chapter_id, sort_order) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_subtopics_topic_id ON public.syllabus_subtopics(topic_id, sort_order) WHERE deleted_at IS NULL;

-- Progress: user-specific queries
CREATE INDEX IF NOT EXISTS idx_progress_user_topic ON public.progress(user_id, topic_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_progress_user_exam ON public.progress(user_id, exam_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_progress_updated ON public.progress(user_id, updated_at DESC) WHERE deleted_at IS NULL;

-- Auth sessions: active session lookup
CREATE INDEX IF NOT EXISTS idx_sessions_profile_active
  ON public.refresh_sessions(profile_id, expires_at DESC)
  WHERE revoked_at IS NULL AND expires_at > now();

-- Auth credentials: profile lookup
CREATE INDEX IF NOT EXISTS idx_credentials_profile ON public.auth_credentials(profile_id);

-- ---------------------------------------------------------------------------
-- AI token usage tracking table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ai_token_usage (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES public.profiles(id),
  provider text NOT NULL,
  model text NOT NULL,
  request_id text,
  input_tokens integer NOT NULL DEFAULT 0,
  output_tokens integer NOT NULL DEFAULT 0,
  total_tokens integer NOT NULL DEFAULT 0,
  cost_usd numeric(10, 6) DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.ai_token_usage IS 'Tracks AI/LLM token usage per request for billing and analytics.';

CREATE INDEX IF NOT EXISTS idx_ai_usage_user ON public.ai_token_usage(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_provider ON public.ai_token_usage(provider, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_usage_request ON public.ai_token_usage(request_id) WHERE request_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- AI usage daily aggregation view
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW public.ai_usage_daily AS
SELECT
  DATE(created_at) AS usage_date,
  provider,
  model,
  COUNT(*) AS request_count,
  SUM(input_tokens) AS total_input_tokens,
  SUM(output_tokens) AS total_output_tokens,
  SUM(total_tokens) AS total_tokens,
  SUM(cost_usd) AS total_cost_usd
FROM public.ai_token_usage
GROUP BY DATE(created_at), provider, model;

COMMENT ON VIEW public.ai_usage_daily IS 'Daily aggregated AI token usage by provider and model.';

-- ---------------------------------------------------------------------------
-- Enable audit triggers on key tables
-- ---------------------------------------------------------------------------
DROP TRIGGER IF EXISTS audit_profiles ON public.profiles;
CREATE TRIGGER audit_profiles
  AFTER INSERT OR UPDATE OR DELETE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

DROP TRIGGER IF EXISTS audit_syllabus_exams ON public.syllabus_exams;
CREATE TRIGGER audit_syllabus_exams
  AFTER INSERT OR UPDATE OR DELETE ON public.syllabus_exams
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

DROP TRIGGER IF EXISTS audit_progress ON public.progress;
CREATE TRIGGER audit_progress
  AFTER INSERT OR UPDATE OR DELETE ON public.progress
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();
