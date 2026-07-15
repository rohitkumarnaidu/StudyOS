-- StudyOS — learner progress (normalized facts + idempotent completion keys).

CREATE TABLE IF NOT EXISTS public.user_chapter_progress (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  profile_id uuid NOT NULL REFERENCES public.profiles (id) ON DELETE CASCADE,
  chapter_id uuid NOT NULL REFERENCES public.chapters (id) ON DELETE CASCADE,
  progress_pct real NOT NULL DEFAULT 0,
  last_studied_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1,
  CONSTRAINT user_chapter_progress_pct_range CHECK (
    progress_pct >= 0
    AND progress_pct <= 100
  )
);

COMMENT ON TABLE public.user_chapter_progress IS 'Aggregated chapter progress; upsert on (profile_id, chapter_id) for idempotent writes.';

CREATE UNIQUE INDEX IF NOT EXISTS user_chapter_progress_live_uidx ON public.user_chapter_progress (profile_id, chapter_id)
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS user_chapter_progress_chapter_live_idx ON public.user_chapter_progress (chapter_id)
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS user_chapter_progress_profile_time_idx ON public.user_chapter_progress (profile_id, last_studied_at DESC)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS user_chapter_progress_touch_updated ON public.user_chapter_progress;

CREATE TRIGGER user_chapter_progress_touch_updated
  BEFORE UPDATE ON public.user_chapter_progress
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS user_chapter_progress_bump_version ON public.user_chapter_progress;

CREATE TRIGGER user_chapter_progress_bump_version
  BEFORE UPDATE ON public.user_chapter_progress
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

CREATE TABLE IF NOT EXISTS public.subtopic_completions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  profile_id uuid NOT NULL REFERENCES public.profiles (id) ON DELETE CASCADE,
  subtopic_id uuid NOT NULL REFERENCES public.subtopics (id) ON DELETE CASCADE,
  completed_at timestamptz NOT NULL DEFAULT now(),
  source text NOT NULL DEFAULT 'app',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.subtopic_completions IS 'Atomic completion facts; unique (profile, subtopic) when live.';

CREATE UNIQUE INDEX IF NOT EXISTS subtopic_completions_live_uidx ON public.subtopic_completions (profile_id, subtopic_id)
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS subtopic_completions_profile_time_idx ON public.subtopic_completions (profile_id, completed_at DESC)
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS subtopic_completions_subtopic_idx ON public.subtopic_completions (subtopic_id)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS subtopic_completions_touch_updated ON public.subtopic_completions;

CREATE TRIGGER subtopic_completions_touch_updated
  BEFORE UPDATE ON public.subtopic_completions
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS subtopic_completions_bump_version ON public.subtopic_completions;

CREATE TRIGGER subtopic_completions_bump_version
  BEFORE UPDATE ON public.subtopic_completions
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();
