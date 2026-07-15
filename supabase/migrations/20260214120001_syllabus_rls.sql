-- Row Level Security for syllabus tables (exam_profiles, subjects, chapters, topics, subtopics)
-- All tables allow public SELECT access (unauthenticated users can view syllabus)
-- INSERT/UPDATE/DELETE restricted to admins (not needed by app yet, but secured for safety)

DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.schemata WHERE schema_name = 'auth'
  ) THEN
    -- exam_profiles: public read, admin write
    ALTER TABLE public.exam_profiles ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "exam_profiles_public_read" ON public.exam_profiles;
    CREATE POLICY "exam_profiles_public_read" ON public.exam_profiles FOR SELECT USING (
      deleted_at IS NULL
    );

    -- subjects: public read, admin write
    ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "subjects_public_read" ON public.subjects;
    CREATE POLICY "subjects_public_read" ON public.subjects FOR SELECT USING (
      deleted_at IS NULL
    );

    -- chapters: public read, admin write
    ALTER TABLE public.chapters ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "chapters_public_read" ON public.chapters;
    CREATE POLICY "chapters_public_read" ON public.chapters FOR SELECT USING (
      deleted_at IS NULL
    );

    -- topics: public read, admin write
    ALTER TABLE public.topics ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "topics_public_read" ON public.topics;
    CREATE POLICY "topics_public_read" ON public.topics FOR SELECT USING (
      deleted_at IS NULL
    );

    -- subtopics: public read, admin write
    ALTER TABLE public.subtopics ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "subtopics_public_read" ON public.subtopics;
    CREATE POLICY "subtopics_public_read" ON public.subtopics FOR SELECT USING (
      deleted_at IS NULL
    );
  END IF;
END
$$;
