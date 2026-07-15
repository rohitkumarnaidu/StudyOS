-- StudyOS — Phase 3: Chat tables for AI tutor with chapter context.

CREATE TABLE IF NOT EXISTS public.chat_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  chapter_id uuid REFERENCES public.chapters(id) ON DELETE SET NULL,
  title text NOT NULL DEFAULT 'New conversation',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.chat_sessions IS 'AI chat sessions scoped to a user and optional chapter context.';

CREATE INDEX IF NOT EXISTS chat_sessions_profile_live_idx ON public.chat_sessions(profile_id, updated_at DESC)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS chat_sessions_chapter_live_idx ON public.chat_sessions(chapter_id)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS chat_sessions_touch_updated ON public.chat_sessions;
CREATE TRIGGER chat_sessions_touch_updated
  BEFORE UPDATE ON public.chat_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS chat_sessions_bump_version ON public.chat_sessions;
CREATE TRIGGER chat_sessions_bump_version
  BEFORE UPDATE ON public.chat_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

CREATE TABLE IF NOT EXISTS public.chat_messages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
  role text NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content text NOT NULL,
  token_count int DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.chat_messages IS 'Individual messages within a chat session.';

CREATE INDEX IF NOT EXISTS chat_messages_session_live_idx ON public.chat_messages(session_id, created_at ASC)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS chat_messages_touch_updated ON public.chat_messages;
CREATE TRIGGER chat_messages_touch_updated
  BEFORE UPDATE ON public.chat_messages
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS chat_messages_bump_version ON public.chat_messages;
CREATE TRIGGER chat_messages_bump_version
  BEFORE UPDATE ON public.chat_messages
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

-- RLS
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own chat sessions" ON public.chat_sessions;
CREATE POLICY "Users can view own chat sessions" ON public.chat_sessions
  FOR SELECT USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can create chat sessions" ON public.chat_sessions;
CREATE POLICY "Users can create chat sessions" ON public.chat_sessions
  FOR INSERT WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can update own chat sessions" ON public.chat_sessions;
CREATE POLICY "Users can update own chat sessions" ON public.chat_sessions
  FOR UPDATE USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can delete own chat sessions" ON public.chat_sessions;
CREATE POLICY "Users can delete own chat sessions" ON public.chat_sessions
  FOR DELETE USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can view messages in own sessions" ON public.chat_messages;
CREATE POLICY "Users can view messages in own sessions" ON public.chat_messages
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions
      WHERE chat_sessions.id = chat_messages.session_id
      AND chat_sessions.profile_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can insert messages in own sessions" ON public.chat_messages;
CREATE POLICY "Users can insert messages in own sessions" ON public.chat_messages
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.chat_sessions
      WHERE chat_sessions.id = chat_messages.session_id
      AND chat_sessions.profile_id = auth.uid()
    )
  );

DROP POLICY IF EXISTS "Users can delete messages in own sessions" ON public.chat_messages;
CREATE POLICY "Users can delete messages in own sessions" ON public.chat_messages
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.chat_sessions
      WHERE chat_sessions.id = chat_messages.session_id
      AND chat_sessions.profile_id = auth.uid()
    )
  );
