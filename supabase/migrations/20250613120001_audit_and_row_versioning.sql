-- StudyOS — audit trail, optimistic concurrency (row_version), and updated_at helpers.

-- ---------------------------------------------------------------------------
-- Audit log (append-only). Attach triggers selectively to high-value tables.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid (),
  occurred_at timestamptz NOT NULL DEFAULT now(),
  schema_name text NOT NULL DEFAULT 'public',
  table_name text NOT NULL,
  record_id uuid,
  action text NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
  actor_id uuid,
  request_id text,
  old_row jsonb,
  new_row jsonb
);

COMMENT ON TABLE public.audit_log IS 'Append-only change history; partition by month when volume grows.';

CREATE INDEX IF NOT EXISTS audit_log_table_time_idx ON public.audit_log (table_name, occurred_at DESC);
CREATE INDEX IF NOT EXISTS audit_log_actor_time_idx ON public.audit_log (actor_id, occurred_at DESC)
WHERE
  actor_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS audit_log_record_idx ON public.audit_log (record_id, occurred_at DESC)
WHERE
  record_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- Timestamps + row_version (optimistic locking). Use on mutable domain tables.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.studyos_set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.studyos_bump_row_version()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  IF TG_OP = 'UPDATE' THEN
    NEW.row_version := COALESCE(OLD.row_version, 0) + 1;
  END IF;
  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.studyos_set_updated_at () IS 'BEFORE UPDATE: sets updated_at = now().';
COMMENT ON FUNCTION public.studyos_bump_row_version () IS 'BEFORE UPDATE: increments row_version for optimistic locking.';

-- ---------------------------------------------------------------------------
-- Generic audit writer (AFTER trigger). TG_TABLE_NAME is stable for public.*.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.studyos_audit_row()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_actor uuid;
  v_req text;
BEGIN
  BEGIN
    v_actor := nullif (current_setting('studyos.actor_id', TRUE), '')::uuid;
  EXCEPTION
    WHEN OTHERS THEN
      v_actor := NULL;
  END;

  BEGIN
    v_req := nullif (current_setting('studyos.request_id', TRUE), '');
  EXCEPTION
    WHEN OTHERS THEN
      v_req := NULL;
  END;

  IF TG_OP = 'DELETE' THEN
    INSERT INTO public.audit_log (
      schema_name,
      table_name,
      record_id,
      action,
      actor_id,
      request_id,
      old_row,
      new_row
    )
    VALUES (
      TG_TABLE_SCHEMA,
      TG_TABLE_NAME,
      OLD.id,
      'DELETE',
      v_actor,
      v_req,
      to_jsonb (OLD),
      NULL
    );

    RETURN OLD;
  END IF;

  IF TG_OP = 'UPDATE' THEN
    INSERT INTO public.audit_log (
      schema_name,
      table_name,
      record_id,
      action,
      actor_id,
      request_id,
      old_row,
      new_row
    )
    VALUES (
      TG_TABLE_SCHEMA,
      TG_TABLE_NAME,
      NEW.id,
      'UPDATE',
      v_actor,
      v_req,
      to_jsonb (OLD),
      to_jsonb (NEW)
    );

    RETURN NEW;
  END IF;

  IF TG_OP = 'INSERT' THEN
    INSERT INTO public.audit_log (
      schema_name,
      table_name,
      record_id,
      action,
      actor_id,
      request_id,
      old_row,
      new_row
    )
    VALUES (
      TG_TABLE_SCHEMA,
      TG_TABLE_NAME,
      NEW.id,
      'INSERT',
      v_actor,
      v_req,
      NULL,
      to_jsonb (NEW)
    );

    RETURN NEW;
  END IF;

  RETURN NEW;
END;
$$;

COMMENT ON FUNCTION public.studyos_audit_row () IS 'AFTER INSERT/UPDATE/DELETE: append audit_log row. Expects PK column named id.';
