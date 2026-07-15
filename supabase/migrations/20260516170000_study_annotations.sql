-- StudyOS — Phase 4: Study annotations (highlights, personal notes, bookmarks).

CREATE TABLE IF NOT EXISTS public.highlights (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  note_id uuid NOT NULL REFERENCES public.notes(id) ON DELETE CASCADE,
  page_number int,
  color text NOT NULL DEFAULT 'yellow',
  text_content text NOT NULL,
  context_before text,
  context_after text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.highlights IS 'User highlights on PDF notes.';

CREATE INDEX IF NOT EXISTS highlights_note_live_idx ON public.highlights(note_id, page_number)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS highlights_profile_live_idx ON public.highlights(profile_id, created_at DESC)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS highlights_touch_updated ON public.highlights;
CREATE TRIGGER highlights_touch_updated
  BEFORE UPDATE ON public.highlights
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS highlights_bump_version ON public.highlights;
CREATE TRIGGER highlights_bump_version
  BEFORE UPDATE ON public.highlights
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

CREATE TABLE IF NOT EXISTS public.personal_notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  note_id uuid NOT NULL REFERENCES public.notes(id) ON DELETE CASCADE,
  page_number int,
  content text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.personal_notes IS 'User personal notes attached to PDF pages.';

CREATE INDEX IF NOT EXISTS personal_notes_note_live_idx ON public.personal_notes(note_id, page_number)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS personal_notes_touch_updated ON public.personal_notes;
CREATE TRIGGER personal_notes_touch_updated
  BEFORE UPDATE ON public.personal_notes
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS personal_notes_bump_version ON public.personal_notes;
CREATE TRIGGER personal_notes_bump_version
  BEFORE UPDATE ON public.personal_notes
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

CREATE TABLE IF NOT EXISTS public.bookmarks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  note_id uuid NOT NULL REFERENCES public.notes(id) ON DELETE CASCADE,
  page_number int NOT NULL,
  label text,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.bookmarks IS 'User bookmarks on PDF notes.';

CREATE UNIQUE INDEX IF NOT EXISTS bookmarks_note_page_live_uidx ON public.bookmarks(profile_id, note_id, page_number)
WHERE deleted_at IS NULL;

-- RLS
ALTER TABLE public.highlights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.personal_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookmarks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own highlights" ON public.highlights;
CREATE POLICY "Users can manage own highlights" ON public.highlights
  FOR ALL USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can manage own personal notes" ON public.personal_notes;
CREATE POLICY "Users can manage own personal notes" ON public.personal_notes
  FOR ALL USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can manage own bookmarks" ON public.bookmarks;
CREATE POLICY "Users can manage own bookmarks" ON public.bookmarks
  FOR ALL USING (auth.uid() = profile_id);
