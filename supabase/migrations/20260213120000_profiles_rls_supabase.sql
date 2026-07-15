-- Row Level Security for public.profiles (Supabase Auth). Skipped on plain Postgres without `auth` schema.

DO $$
BEGIN
  IF EXISTS (
    SELECT
      1
    FROM
      information_schema.schemata
    WHERE
      schema_name = 'auth'
  ) THEN
    ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

    DROP POLICY IF EXISTS "profiles_select_own" ON public.profiles;
    CREATE POLICY "profiles_select_own" ON public.profiles FOR SELECT USING (auth.uid () = id);

    DROP POLICY IF EXISTS "profiles_update_own" ON public.profiles;
    CREATE POLICY "profiles_update_own" ON public.profiles FOR UPDATE USING (auth.uid () = id)
    WITH CHECK (auth.uid () = id);

    DROP POLICY IF EXISTS "profiles_insert_own" ON public.profiles;
    CREATE POLICY "profiles_insert_own" ON public.profiles FOR INSERT
    WITH CHECK (auth.uid () = id);
  END IF;
END
$$;
