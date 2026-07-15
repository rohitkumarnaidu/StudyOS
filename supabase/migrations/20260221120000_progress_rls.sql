-- StudyOS — Row-Level Security for progress tables

DO $$
BEGIN
  -- Check if auth schema exists (for local/non-Supabase environments)
  IF EXISTS (SELECT FROM information_schema.schemata WHERE schema_name = 'auth') THEN
    -- user_chapter_progress: users can only read/write their own progress
    ALTER TABLE public.user_chapter_progress ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS user_chapter_progress_own_read ON public.user_chapter_progress;
    CREATE POLICY user_chapter_progress_own_read ON public.user_chapter_progress
      FOR SELECT USING (profile_id = auth.uid());

    DROP POLICY IF EXISTS user_chapter_progress_own_write ON public.user_chapter_progress;
    CREATE POLICY user_chapter_progress_own_write ON public.user_chapter_progress
      FOR INSERT WITH CHECK (profile_id = auth.uid());

    DROP POLICY IF EXISTS user_chapter_progress_own_update ON public.user_chapter_progress;
    CREATE POLICY user_chapter_progress_own_update ON public.user_chapter_progress
      FOR UPDATE USING (profile_id = auth.uid());

    DROP POLICY IF EXISTS user_chapter_progress_own_delete ON public.user_chapter_progress;
    CREATE POLICY user_chapter_progress_own_delete ON public.user_chapter_progress
      FOR DELETE USING (profile_id = auth.uid());

    -- subtopic_completions: users can only read/write their own completions
    ALTER TABLE public.subtopic_completions ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS subtopic_completions_own_read ON public.subtopic_completions;
    CREATE POLICY subtopic_completions_own_read ON public.subtopic_completions
      FOR SELECT USING (profile_id = auth.uid());

    DROP POLICY IF EXISTS subtopic_completions_own_write ON public.subtopic_completions;
    CREATE POLICY subtopic_completions_own_write ON public.subtopic_completions
      FOR INSERT WITH CHECK (profile_id = auth.uid());

    DROP POLICY IF EXISTS subtopic_completions_own_update ON public.subtopic_completions;
    CREATE POLICY subtopic_completions_own_update ON public.subtopic_completions
      FOR UPDATE USING (profile_id = auth.uid());

    DROP POLICY IF EXISTS subtopic_completions_own_delete ON public.subtopic_completions;
    CREATE POLICY subtopic_completions_own_delete ON public.subtopic_completions
      FOR DELETE USING (profile_id = auth.uid());
  END IF;
END $$;
