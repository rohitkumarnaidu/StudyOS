-- StudyOS — deterministic dev/staging seed (idempotent WHERE NOT EXISTS).
-- Run via: `supabase db reset` (applies migrations + seed) or `psql -f supabase/seed.sql`.
-- Do not put production secrets here.

-- Fixed UUIDs keep FK graphs stable across re-seeds.
INSERT INTO public.institutes (id, slug, name)
SELECT
  '11111111-1111-1111-1111-111111111111'::uuid,
  'studyos-demo',
  'StudyOS Demo Institute'
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.institutes
    WHERE
      id = '11111111-1111-1111-1111-111111111111'::uuid
  );

INSERT INTO public.exam_profiles (id, institute_id, code, title, description)
SELECT
  '22222222-2222-2222-2222-222222222222'::uuid,
  NULL,
  'neet-demo',
  'NEET (demo syllabus)',
  'Minimal tree for local development'
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.exam_profiles
    WHERE
      id = '22222222-2222-2222-2222-222222222222'::uuid
  );

INSERT INTO public.subjects (id, exam_profile_id, name, sort_order)
SELECT
  '33333333-3333-3333-3333-333333333333'::uuid,
  '22222222-2222-2222-2222-222222222222'::uuid,
  'Physics',
  1
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.subjects
    WHERE
      id = '33333333-3333-3333-3333-333333333333'::uuid
  );

INSERT INTO public.chapters (id, subject_id, name, sort_order)
SELECT
  '44444444-4444-4444-4444-444444444444'::uuid,
  '33333333-3333-3333-3333-333333333333'::uuid,
  'Mechanics',
  1
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.chapters
    WHERE
      id = '44444444-4444-4444-4444-444444444444'::uuid
  );

INSERT INTO public.topics (id, chapter_id, name, sort_order)
SELECT
  '55555555-5555-5555-5555-555555555555'::uuid,
  '44444444-4444-4444-4444-444444444444'::uuid,
  'Kinematics',
  1
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.topics
    WHERE
      id = '55555555-5555-5555-5555-555555555555'::uuid
  );

INSERT INTO public.subtopics (id, topic_id, name, sort_order, estimated_minutes)
SELECT
  '66666666-6666-6666-6666-666666666666'::uuid,
  '55555555-5555-5555-5555-555555555555'::uuid,
  'Linear motion',
  1,
  25
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.subtopics
    WHERE
      id = '66666666-6666-6666-6666-666666666666'::uuid
  );

-- Demo learner (password: `demo`) — pairs with API memory-login fallback email.
INSERT INTO public.profiles (id, email, display_name, app_role)
SELECT
  '77777777-7777-4777-8777-777777777777'::uuid,
  'demo@studyos.app',
  'Demo Student',
  'student'::public.app_role
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.profiles
    WHERE
      id = '77777777-7777-4777-8777-777777777777'::uuid
  );

INSERT INTO public.auth_credentials (profile_id, password_hash)
SELECT
  '77777777-7777-4777-8777-777777777777'::uuid,
  $phc$$argon2id$v=19$m=65536,t=3,p=4$ryKpKxCo8Vg4v8L9tA6ksA$hoWXAqDmIYqdNtx+DaVYnLAB8qxginedT2utnPISbHA$phc$
WHERE
  NOT EXISTS (
    SELECT
      1
    FROM
      public.auth_credentials
    WHERE
      profile_id = '77777777-7777-4777-8777-777777777777'::uuid
  );
