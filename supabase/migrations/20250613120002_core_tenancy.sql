-- StudyOS — core tenancy: institutes, profiles, memberships, batches (normalized).

DO $$
BEGIN
  CREATE TYPE public.app_role AS ENUM(
    'student',
    'teacher',
    'institute_admin',
    'platform_admin'
  );

EXCEPTION
  WHEN duplicate_object THEN
    NULL;
END
$$;

DO $$
BEGIN
  CREATE TYPE public.member_role AS ENUM(
    'owner',
    'admin',
    'teacher',
    'student'
  );

EXCEPTION
  WHEN duplicate_object THEN
    NULL;
END
$$;

-- ---------------------------------------------------------------------------
-- Institutes (tenant / school / coaching center).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.institutes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  slug text NOT NULL,
  name text NOT NULL,
  settings jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1,
  CONSTRAINT institutes_slug_nonempty CHECK (length(trim(slug)) > 0)
);

COMMENT ON TABLE public.institutes IS 'Tenant root; optional FK targets for profiles and syllabus.';

CREATE UNIQUE INDEX IF NOT EXISTS institutes_slug_live_uidx ON public.institutes (lower(slug))
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS institutes_created_idx ON public.institutes (created_at DESC);

DROP TRIGGER IF EXISTS institutes_touch_updated ON public.institutes;

CREATE TRIGGER institutes_touch_updated
  BEFORE UPDATE ON public.institutes
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS institutes_bump_version ON public.institutes;

CREATE TRIGGER institutes_bump_version
  BEFORE UPDATE ON public.institutes
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

DROP TRIGGER IF EXISTS institutes_audit_row ON public.institutes;

CREATE TRIGGER institutes_audit_row
  AFTER INSERT OR UPDATE OR DELETE ON public.institutes
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_audit_row ();

-- ---------------------------------------------------------------------------
-- Profiles (application user). In Supabase, id matches auth.users(id).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid PRIMARY KEY,
  email text,
  display_name text,
  locale text NOT NULL DEFAULT 'en',
  app_role public.app_role NOT NULL DEFAULT 'student',
  institute_id uuid REFERENCES public.institutes (id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.profiles IS 'One row per login identity; links to institutes for tenancy.';

CREATE INDEX IF NOT EXISTS profiles_institute_live_idx ON public.profiles (institute_id)
WHERE
  deleted_at IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS profiles_email_live_uidx ON public.profiles (lower(email))
WHERE
  deleted_at IS NULL
  AND email IS NOT NULL;

DROP TRIGGER IF EXISTS profiles_touch_updated ON public.profiles;

CREATE TRIGGER profiles_touch_updated
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS profiles_bump_version ON public.profiles;

CREATE TRIGGER profiles_bump_version
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

-- Optional FK to Supabase auth.users when auth schema exists.
DO $$
BEGIN
  IF EXISTS (
    SELECT
      1
    FROM
      information_schema.schemata
    WHERE
      schema_name = 'auth'
  ) AND EXISTS (
    SELECT
      1
    FROM
      information_schema.tables
    WHERE
      table_schema = 'auth'
      AND table_name = 'users'
  ) THEN
    IF NOT EXISTS (
      SELECT
        1
      FROM
        pg_constraint
      WHERE
        conname = 'profiles_id_fk_auth_users'
    ) THEN
      ALTER TABLE public.profiles
        ADD CONSTRAINT profiles_id_fk_auth_users FOREIGN KEY (id) REFERENCES auth.users (id) ON DELETE CASCADE;

    END IF;
  END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- Institute membership (normalized M:N with role).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.institute_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  institute_id uuid NOT NULL REFERENCES public.institutes (id) ON DELETE CASCADE,
  profile_id uuid NOT NULL REFERENCES public.profiles (id) ON DELETE CASCADE,
  member_role public.member_role NOT NULL DEFAULT 'student',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.institute_members IS 'M:N profiles↔institutes with role; partial unique index enforces one live row per pair.';

-- Partial unique: only one live membership per pair
DROP INDEX IF EXISTS institute_members_institute_profile_live_uidx;

CREATE UNIQUE INDEX institute_members_institute_profile_live_uidx ON public.institute_members (institute_id, profile_id)
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS institute_members_profile_live_idx ON public.institute_members (profile_id)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS institute_members_touch_updated ON public.institute_members;

CREATE TRIGGER institute_members_touch_updated
  BEFORE UPDATE ON public.institute_members
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS institute_members_bump_version ON public.institute_members;

CREATE TRIGGER institute_members_bump_version
  BEFORE UPDATE ON public.institute_members
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

-- ---------------------------------------------------------------------------
-- Batches (class cohorts) and enrollments (normalized M:N).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.batches (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  institute_id uuid NOT NULL REFERENCES public.institutes (id) ON DELETE CASCADE,
  name text NOT NULL,
  academic_year int,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS batches_institute_live_idx ON public.batches (institute_id)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS batches_touch_updated ON public.batches;

CREATE TRIGGER batches_touch_updated
  BEFORE UPDATE ON public.batches
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS batches_bump_version ON public.batches;

CREATE TRIGGER batches_bump_version
  BEFORE UPDATE ON public.batches
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

CREATE TABLE IF NOT EXISTS public.batch_enrollments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  batch_id uuid NOT NULL REFERENCES public.batches (id) ON DELETE CASCADE,
  profile_id uuid NOT NULL REFERENCES public.profiles (id) ON DELETE CASCADE,
  enrolled_at timestamptz NOT NULL DEFAULT now(),
  left_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.batch_enrollments IS 'Student (or teacher) association to a batch; soft-delete preserves history.';

CREATE UNIQUE INDEX IF NOT EXISTS batch_enrollments_batch_profile_live_uidx ON public.batch_enrollments (batch_id, profile_id)
WHERE
  deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS batch_enrollments_profile_live_idx ON public.batch_enrollments (profile_id)
WHERE
  deleted_at IS NULL;

DROP TRIGGER IF EXISTS batch_enrollments_touch_updated ON public.batch_enrollments;

CREATE TRIGGER batch_enrollments_touch_updated
  BEFORE UPDATE ON public.batch_enrollments
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS batch_enrollments_bump_version ON public.batch_enrollments;

CREATE TRIGGER batch_enrollments_bump_version
  BEFORE UPDATE ON public.batch_enrollments
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();
