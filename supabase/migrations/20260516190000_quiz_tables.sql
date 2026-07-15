-- StudyOS — Phase 5: Quiz tables for self-assessment + mock tests.

CREATE TABLE IF NOT EXISTS public.questions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id uuid REFERENCES public.chapters(id) ON DELETE SET NULL,
  topic_id uuid REFERENCES public.topics(id) ON DELETE SET NULL,
  subtopic_id uuid REFERENCES public.subtopics(id) ON DELETE SET NULL,
  question_text text NOT NULL,
  question_type text NOT NULL DEFAULT 'mcq' CHECK (question_type IN ('mcq', 'numeric', 'assertion_reason', 'match_following')),
  option_a text,
  option_b text,
  option_c text,
  option_d text,
  correct_answer text NOT NULL,
  explanation text,
  difficulty int NOT NULL DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),
  source text DEFAULT 'ai',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.questions IS 'Question bank for quizzes and mock tests.';

CREATE INDEX IF NOT EXISTS questions_chapter_live_idx ON public.questions(chapter_id)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS questions_topic_live_idx ON public.questions(topic_id)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS questions_difficulty_live_idx ON public.questions(difficulty)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS questions_touch_updated ON public.questions;
CREATE TRIGGER questions_touch_updated
  BEFORE UPDATE ON public.questions
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS questions_bump_version ON public.questions;
CREATE TRIGGER questions_bump_version
  BEFORE UPDATE ON public.questions
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

CREATE TABLE IF NOT EXISTS public.quiz_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  chapter_id uuid REFERENCES public.chapters(id) ON DELETE SET NULL,
  quiz_type text NOT NULL DEFAULT 'practice' CHECK (quiz_type IN ('practice', 'timed', 'mock')),
  title text NOT NULL,
  total_questions int NOT NULL DEFAULT 0,
  time_limit_minutes int,
  started_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  score real,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.quiz_sessions IS 'Individual quiz attempts by users.';

CREATE INDEX IF NOT EXISTS quiz_sessions_profile_live_idx ON public.quiz_sessions(profile_id, started_at DESC)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS quiz_sessions_chapter_live_idx ON public.quiz_sessions(chapter_id)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS quiz_sessions_touch_updated ON public.quiz_sessions;
CREATE TRIGGER quiz_sessions_touch_updated
  BEFORE UPDATE ON public.quiz_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS quiz_sessions_bump_version ON public.quiz_sessions;
CREATE TRIGGER quiz_sessions_bump_version
  BEFORE UPDATE ON public.quiz_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

CREATE TABLE IF NOT EXISTS public.quiz_responses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL REFERENCES public.quiz_sessions(id) ON DELETE CASCADE,
  question_id uuid NOT NULL REFERENCES public.questions(id) ON DELETE CASCADE,
  user_answer text,
  is_correct boolean,
  time_taken_seconds int,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.quiz_responses IS 'User answers for each question in a quiz session.';

CREATE INDEX IF NOT EXISTS quiz_responses_session_idx ON public.quiz_responses(session_id);

CREATE INDEX IF NOT EXISTS quiz_responses_question_idx ON public.quiz_responses(question_id);

CREATE TABLE IF NOT EXISTS public.mistake_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  question_id uuid NOT NULL REFERENCES public.questions(id) ON DELETE CASCADE,
  session_id uuid REFERENCES public.quiz_sessions(id) ON DELETE SET NULL,
  user_answer text,
  correct_answer text,
  reviewed boolean NOT NULL DEFAULT false,
  review_count int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.mistake_log IS 'Tracks incorrect answers for spaced repetition review.';

CREATE INDEX IF NOT EXISTS mistake_log_profile_live_idx ON public.mistake_log(profile_id, created_at DESC)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS mistake_log_reviewed_live_idx ON public.mistake_log(profile_id, reviewed)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS mistake_log_touch_updated ON public.mistake_log;
CREATE TRIGGER mistake_log_touch_updated
  BEFORE UPDATE ON public.mistake_log
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS mistake_log_bump_version ON public.mistake_log;
CREATE TRIGGER mistake_log_bump_version
  BEFORE UPDATE ON public.mistake_log
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

-- RLS
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mistake_log ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public can read questions" ON public.questions;
CREATE POLICY "Public can read questions" ON public.questions
  FOR SELECT USING (true);

DROP POLICY IF EXISTS "Users can manage own quiz sessions" ON public.quiz_sessions;
CREATE POLICY "Users can manage own quiz sessions" ON public.quiz_sessions
  FOR ALL USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can view own quiz responses" ON public.quiz_responses;
CREATE POLICY "Users can view own quiz responses" ON public.quiz_responses
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.quiz_sessions WHERE quiz_sessions.id = quiz_responses.session_id AND quiz_sessions.profile_id = auth.uid())
  );

DROP POLICY IF EXISTS "Users can insert quiz responses" ON public.quiz_responses;
CREATE POLICY "Users can insert quiz responses" ON public.quiz_responses
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM public.quiz_sessions WHERE quiz_sessions.id = quiz_responses.session_id AND quiz_sessions.profile_id = auth.uid())
  );

DROP POLICY IF EXISTS "Users can manage own mistake log" ON public.mistake_log;
CREATE POLICY "Users can manage own mistake log" ON public.mistake_log
  FOR ALL USING (auth.uid() = profile_id);
