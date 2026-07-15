-- StudyOS — syllabus tree (normalized): exam → subject → chapter → topic → subtopic.

CREATE TABLE IF NOT EXISTS public.exam_profiles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  institute_id uuid REFERENCES public.institutes (id) ON DELETE CASCADE,
  code text NOT NULL,
  title text NOT NULL,
  description text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1,
  CONSTRAINT exam_profiles_code_nonempty CHECK (length(trim(code)) > 0)
);

COMMENT ON TABLE public.exam_profiles IS 'Syllabus edition (e.g. NEET 2026); institute_id NULL = platform-global.';

CREATE UNIQUE INDEX IF NOT EXISTS exam_profiles_code_scope_live_uidx ON public.exam_profiles (lower(code), COALESCE(institute_id, '00000000-0000-0000-0000-000000000000'::uuid))
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS exam_profiles_institute_live_idx ON public.exam_profiles (institute_id)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS exam_profiles_touch_updated ON public.exam_profiles;

CREATE TRIGGER exam_profiles_touch_updated
  BEFORE UPDATE ON public.exam_profiles
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS exam_profiles_bump_version ON public.exam_profiles;

CREATE TRIGGER exam_profiles_bump_version
  BEFORE UPDATE ON public.exam_profiles
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

CREATE TABLE IF NOT EXISTS public.subjects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  exam_profile_id uuid NOT NULL REFERENCES public.exam_profiles (id) ON DELETE CASCADE,
  name text NOT NULL,
  sort_order int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS subjects_exam_live_idx ON public.subjects (exam_profile_id, sort_order)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS subjects_touch_updated ON public.subjects;

CREATE TRIGGER subjects_touch_updated
  BEFORE UPDATE ON public.subjects
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS subjects_bump_version ON public.subjects;

CREATE TRIGGER subjects_bump_version
  BEFORE UPDATE ON public.subjects
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

CREATE TABLE IF NOT EXISTS public.chapters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  subject_id uuid NOT NULL REFERENCES public.subjects (id) ON DELETE CASCADE,
  name text NOT NULL,
  sort_order int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS chapters_subject_live_idx ON public.chapters (subject_id, sort_order)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS chapters_touch_updated ON public.chapters;

CREATE TRIGGER chapters_touch_updated
  BEFORE UPDATE ON public.chapters
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS chapters_bump_version ON public.chapters;

CREATE TRIGGER chapters_bump_version
  BEFORE UPDATE ON public.chapters
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

CREATE TABLE IF NOT EXISTS public.topics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  chapter_id uuid NOT NULL REFERENCES public.chapters (id) ON DELETE CASCADE,
  name text NOT NULL,
  sort_order int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS topics_chapter_live_idx ON public.topics (chapter_id, sort_order)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS topics_touch_updated ON public.topics;

CREATE TRIGGER topics_touch_updated
  BEFORE UPDATE ON public.topics
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS topics_bump_version ON public.topics;

CREATE TRIGGER topics_bump_version
  BEFORE UPDATE ON public.topics
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

CREATE TABLE IF NOT EXISTS public.subtopics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  topic_id uuid NOT NULL REFERENCES public.topics (id) ON DELETE CASCADE,
  name text NOT NULL,
  sort_order int NOT NULL DEFAULT 0,
  estimated_minutes int,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS subtopics_topic_live_idx ON public.subtopics (topic_id, sort_order)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS subtopics_touch_updated ON public.subtopics;

CREATE TRIGGER subtopics_touch_updated
  BEFORE UPDATE ON public.subtopics
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS subtopics_bump_version ON public.subtopics;

CREATE TRIGGER subtopics_bump_version
  BEFORE UPDATE ON public.subtopics
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();
