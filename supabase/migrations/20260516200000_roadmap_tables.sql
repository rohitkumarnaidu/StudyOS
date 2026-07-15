-- StudyOS — Phase 6: Roadmap tables for AI-generated personalized study plans.

CREATE TABLE IF NOT EXISTS public.roadmaps (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title text NOT NULL,
  exam_id uuid REFERENCES public.exam_profiles(id) ON DELETE SET NULL,
  generated_by text NOT NULL DEFAULT 'ai',
  start_date date NOT NULL,
  end_date date NOT NULL,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.roadmaps IS 'Personalized study roadmaps generated for users.';

CREATE INDEX IF NOT EXISTS roadmaps_profile_live_idx ON public.roadmaps(profile_id, is_active)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS roadmaps_touch_updated ON public.roadmaps;
CREATE TRIGGER roadmaps_touch_updated
  BEFORE UPDATE ON public.roadmaps
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS roadmaps_bump_version ON public.roadmaps;
CREATE TRIGGER roadmaps_bump_version
  BEFORE UPDATE ON public.roadmaps
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

CREATE TABLE IF NOT EXISTS public.roadmap_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  roadmap_id uuid NOT NULL REFERENCES public.roadmaps(id) ON DELETE CASCADE,
  chapter_id uuid REFERENCES public.chapters(id) ON DELETE SET NULL,
  title text NOT NULL,
  description text,
  target_date date NOT NULL,
  priority int NOT NULL DEFAULT 1 CHECK (priority BETWEEN 1 AND 3),
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'skipped')),
  completed_at timestamptz,
  sort_order int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.roadmap_items IS 'Individual tasks/chapters within a study roadmap.';

CREATE INDEX IF NOT EXISTS roadmap_items_roadmap_live_idx ON public.roadmap_items(roadmap_id, sort_order)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS roadmap_items_target_date_live_idx ON public.roadmap_items(roadmap_id, target_date)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS roadmap_items_touch_updated ON public.roadmap_items;
CREATE TRIGGER roadmap_items_touch_updated
  BEFORE UPDATE ON public.roadmap_items
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS roadmap_items_bump_version ON public.roadmap_items;
CREATE TRIGGER roadmap_items_bump_version
  BEFORE UPDATE ON public.roadmap_items
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

-- RLS
ALTER TABLE public.roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.roadmap_items ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own roadmaps" ON public.roadmaps;
CREATE POLICY "Users can manage own roadmaps" ON public.roadmaps
  FOR ALL USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can manage own roadmap items" ON public.roadmap_items;
CREATE POLICY "Users can manage own roadmap items" ON public.roadmap_items
  FOR ALL USING (
    EXISTS (SELECT 1 FROM public.roadmaps WHERE roadmaps.id = roadmap_items.roadmap_id AND roadmaps.profile_id = auth.uid())
  );
