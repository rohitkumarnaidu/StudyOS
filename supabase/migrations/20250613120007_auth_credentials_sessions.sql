-- StudyOS — password hashes (Argon2id) and refresh-session rotation (device / IP tracking).

CREATE TABLE IF NOT EXISTS public.auth_credentials (
  profile_id uuid PRIMARY KEY REFERENCES public.profiles (id) ON DELETE CASCADE,
  password_hash text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.auth_credentials IS 'Password material separate from profile row; Argon2id PHC strings only.';

DROP TRIGGER IF EXISTS auth_credentials_touch_updated ON public.auth_credentials;

CREATE TRIGGER auth_credentials_touch_updated
  BEFORE UPDATE ON public.auth_credentials
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_set_updated_at ();

DROP TRIGGER IF EXISTS auth_credentials_bump_version ON public.auth_credentials;

CREATE TRIGGER auth_credentials_bump_version
  BEFORE UPDATE ON public.auth_credentials
  FOR EACH ROW
  EXECUTE PROCEDURE public.studyos_bump_row_version ();

CREATE TABLE IF NOT EXISTS public.auth_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  profile_id uuid NOT NULL REFERENCES public.profiles (id) ON DELETE CASCADE,
  family_id uuid NOT NULL,
  refresh_token_hash text NOT NULL,
  user_agent text,
  ip inet,
  created_at timestamptz NOT NULL DEFAULT now(),
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  replaced_by uuid REFERENCES public.auth_sessions (id),
  last_used_at timestamptz
);

COMMENT ON TABLE public.auth_sessions IS 'Rotating refresh tokens; reuse of revoked token revokes whole family_id.';

CREATE UNIQUE INDEX IF NOT EXISTS auth_sessions_refresh_hash_uidx ON public.auth_sessions (refresh_token_hash);

CREATE INDEX IF NOT EXISTS auth_sessions_profile_live_idx ON public.auth_sessions (profile_id, created_at DESC)
WHERE
  revoked_at IS NULL;

CREATE INDEX IF NOT EXISTS auth_sessions_family_idx ON public.auth_sessions (family_id);
