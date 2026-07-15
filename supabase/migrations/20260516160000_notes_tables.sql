-- StudyOS — Phase 4: Notes tables for PDF + Mind Map pipeline.

CREATE TABLE IF NOT EXISTS public.notes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  chapter_id uuid REFERENCES public.chapters(id) ON DELETE SET NULL,
  title text NOT NULL,
  note_type text NOT NULL CHECK (note_type IN ('pdf', 'mindmap', 'text')),
  file_path text,
  file_size bigint,
  mime_type text,
  page_count int DEFAULT 0,
  status text NOT NULL DEFAULT 'uploading' CHECK (status IN ('uploading', 'processing', 'ready', 'failed')),
  structured_content jsonb,
  summary text,
  tags text[] DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.notes IS 'User-uploaded notes (PDFs, mind maps, text) with AI-processed content.';

CREATE INDEX IF NOT EXISTS notes_profile_live_idx ON public.notes(profile_id, updated_at DESC)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS notes_chapter_live_idx ON public.notes(chapter_id)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS notes_status_live_idx ON public.notes(profile_id, status)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS notes_tags_idx ON public.notes USING GIN(tags)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS notes_touch_updated ON public.notes;
CREATE TRIGGER notes_touch_updated
  BEFORE UPDATE ON public.notes
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS notes_bump_version ON public.notes;
CREATE TRIGGER notes_bump_version
  BEFORE UPDATE ON public.notes
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

CREATE TABLE IF NOT EXISTS public.note_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id uuid NOT NULL REFERENCES public.notes(id) ON DELETE CASCADE,
  version int NOT NULL DEFAULT 1,
  structured_content jsonb,
  summary text,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.note_versions IS 'Version history of note processing.';

CREATE INDEX IF NOT EXISTS note_versions_note_idx ON public.note_versions(note_id, version DESC);

CREATE TABLE IF NOT EXISTS public.note_embeddings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id uuid NOT NULL REFERENCES public.notes(id) ON DELETE CASCADE,
  chunk_index int NOT NULL,
  content text NOT NULL,
  embedding vector(1536),
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.note_embeddings IS 'pgvector embeddings for note content chunks.';

CREATE INDEX IF NOT EXISTS note_embeddings_note_idx ON public.note_embeddings(note_id);

CREATE TABLE IF NOT EXISTS public.note_mindmaps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  note_id uuid NOT NULL REFERENCES public.notes(id) ON DELETE CASCADE,
  tree_data jsonb NOT NULL,
  image_path text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.note_mindmaps IS 'Interactive mind map data extracted from PDFs.';

CREATE INDEX IF NOT EXISTS note_mindmaps_note_idx ON public.note_mindmaps(note_id);

DROP TRIGGER IF EXISTS note_mindmaps_touch_updated ON public.note_mindmaps;
CREATE TRIGGER note_mindmaps_touch_updated
  BEFORE UPDATE ON public.note_mindmaps
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

-- RLS
ALTER TABLE public.notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.note_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.note_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.note_mindmaps ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own notes" ON public.notes;
CREATE POLICY "Users can view own notes" ON public.notes
  FOR SELECT USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can create notes" ON public.notes;
CREATE POLICY "Users can create notes" ON public.notes
  FOR INSERT WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can update own notes" ON public.notes;
CREATE POLICY "Users can update own notes" ON public.notes
  FOR UPDATE USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can delete own notes" ON public.notes;
CREATE POLICY "Users can delete own notes" ON public.notes
  FOR DELETE USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can view note versions" ON public.note_versions;
CREATE POLICY "Users can view note versions" ON public.note_versions
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.notes WHERE notes.id = note_versions.note_id AND notes.profile_id = auth.uid())
  );

DROP POLICY IF EXISTS "Users can view note embeddings" ON public.note_embeddings;
CREATE POLICY "Users can view note embeddings" ON public.note_embeddings
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.notes WHERE notes.id = note_embeddings.note_id AND notes.profile_id = auth.uid())
  );

DROP POLICY IF EXISTS "Users can view note mindmaps" ON public.note_mindmaps;
CREATE POLICY "Users can view note mindmaps" ON public.note_mindmaps
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.notes WHERE notes.id = note_mindmaps.note_id AND notes.profile_id = auth.uid())
  );
