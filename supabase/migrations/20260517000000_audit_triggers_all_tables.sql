-- StudyOS — Wire audit triggers to all domain tables.
-- This migration attaches the studyos_audit_row() trigger to tables that
-- were created after the initial audit framework migration.

-- Profiles (user accounts)
DROP TRIGGER IF EXISTS audit_profiles ON public.profiles;
CREATE TRIGGER audit_profiles
  AFTER INSERT OR UPDATE OR DELETE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Subtopic completions (progress tracking)
DROP TRIGGER IF EXISTS audit_subtopic_completions ON public.subtopic_completions;
CREATE TRIGGER audit_subtopic_completions
  AFTER INSERT OR UPDATE OR DELETE ON public.subtopic_completions
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Streaks (gamification)
DROP TRIGGER IF EXISTS audit_streaks ON public.streaks;
CREATE TRIGGER audit_streaks
  AFTER INSERT OR UPDATE OR DELETE ON public.streaks
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- AI token usage (cost tracking)
DROP TRIGGER IF EXISTS audit_ai_token_usage ON public.ai_token_usage;
CREATE TRIGGER audit_ai_token_usage
  AFTER INSERT OR UPDATE OR DELETE ON public.ai_token_usage
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Chat sessions (AI tutor)
DROP TRIGGER IF EXISTS audit_chat_sessions ON public.chat_sessions;
CREATE TRIGGER audit_chat_sessions
  AFTER INSERT OR UPDATE OR DELETE ON public.chat_sessions
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Chat messages (AI tutor)
DROP TRIGGER IF EXISTS audit_chat_messages ON public.chat_messages;
CREATE TRIGGER audit_chat_messages
  AFTER INSERT OR UPDATE OR DELETE ON public.chat_messages
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Notes (PDF/mindmap uploads)
DROP TRIGGER IF EXISTS audit_notes ON public.notes;
CREATE TRIGGER audit_notes
  AFTER INSERT OR UPDATE OR DELETE ON public.notes
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Quiz sessions (mock tests)
DROP TRIGGER IF EXISTS audit_quiz_sessions ON public.quiz_sessions;
CREATE TRIGGER audit_quiz_sessions
  AFTER INSERT OR UPDATE OR DELETE ON public.quiz_sessions
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Quiz responses (mock test answers)
DROP TRIGGER IF EXISTS audit_quiz_responses ON public.quiz_responses;
CREATE TRIGGER audit_quiz_responses
  AFTER INSERT OR UPDATE OR DELETE ON public.quiz_responses
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Mistake log (learning from errors)
DROP TRIGGER IF EXISTS audit_mistake_log ON public.mistake_log;
CREATE TRIGGER audit_mistake_log
  AFTER INSERT OR UPDATE OR DELETE ON public.mistake_log
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Study annotations (highlights/bookmarks)
DROP TRIGGER IF EXISTS audit_study_annotations ON public.study_annotations;
CREATE TRIGGER audit_study_annotations
  AFTER INSERT OR UPDATE OR DELETE ON public.study_annotations
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Roadmap items (AI-generated study plans)
DROP TRIGGER IF EXISTS audit_roadmap_items ON public.roadmap_items;
CREATE TRIGGER audit_roadmap_items
  AFTER INSERT OR UPDATE OR DELETE ON public.roadmap_items
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Achievements (gamification milestones)
DROP TRIGGER IF EXISTS audit_user_achievements ON public.user_achievements;
CREATE TRIGGER audit_user_achievements
  AFTER INSERT OR UPDATE OR DELETE ON public.user_achievements
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Auth credentials (password hashes — audit only, no row version)
DROP TRIGGER IF EXISTS audit_auth_credentials ON public.auth_credentials;
CREATE TRIGGER audit_auth_credentials
  AFTER INSERT OR UPDATE OR DELETE ON public.auth_credentials
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Refresh sessions (token rotation)
DROP TRIGGER IF EXISTS audit_refresh_sessions ON public.refresh_sessions;
CREATE TRIGGER audit_refresh_sessions
  AFTER INSERT OR UPDATE OR DELETE ON public.refresh_sessions
  FOR EACH ROW EXECUTE FUNCTION public.studyos_audit_row();

-- Audit log retention policy (auto-delete older than 1 year)
-- This is a soft retention — adjust based on compliance requirements.
CREATE OR REPLACE FUNCTION public.purge_old_audit_logs()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  DELETE FROM public.audit_log
  WHERE occurred_at < now() - interval '1 year';
END;
$$;

COMMENT ON FUNCTION public.purge_old_audit_logs() IS 'Delete audit logs older than 1 year. Schedule via cron or Supabase pg_cron.';
