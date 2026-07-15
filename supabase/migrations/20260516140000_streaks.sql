-- StudyOS — Phase 1: Streaks system.
-- Tracks daily study streaks computed from subtopic completions.

-- ---------------------------------------------------------------------------
-- Streaks table
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.streaks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  current_streak int NOT NULL DEFAULT 0,
  longest_streak int NOT NULL DEFAULT 0,
  last_study_date date NOT NULL DEFAULT CURRENT_DATE,
  freeze_used boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.streaks IS 'Daily study streak tracking per user.';

CREATE UNIQUE INDEX IF NOT EXISTS streaks_profile_live_uidx ON public.streaks(profile_id)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS streaks_current_live_idx ON public.streaks(current_streak DESC)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS streaks_touch_updated ON public.streaks;
CREATE TRIGGER streaks_touch_updated
  BEFORE UPDATE ON public.streaks
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS streaks_bump_version ON public.streaks;
CREATE TRIGGER streaks_bump_version
  BEFORE UPDATE ON public.streaks
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

-- ---------------------------------------------------------------------------
-- Function: compute streak from subtopic completions
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.fn_compute_streak(p_profile_id uuid)
RETURNS TABLE(current_streak int, longest_streak int, last_study_date date)
LANGUAGE plpgsql
AS $$
DECLARE
  v_current int := 0;
  v_longest int := 0;
  v_last date := NULL;
  v_check date;
  v_row RECORD;
BEGIN
  -- Get distinct dates when user completed subtopics
  FOR v_row IN
    SELECT DISTINCT DATE(completed_at) AS study_date
    FROM public.subtopic_completions
    WHERE profile_id = p_profile_id AND deleted_at IS NULL
    ORDER BY study_date DESC
  LOOP
    IF v_last IS NULL THEN
      v_last := v_row.study_date;
      v_current := 1;
      v_longest := 1;
    ELSE
      -- Check if consecutive (or within 1 day gap for streak continuity)
      IF v_check - v_row.study_date = 1 THEN
        v_current := v_current + 1;
        v_longest := GREATEST(v_longest, v_current);
      ELSIF v_check - v_row.study_date > 1 THEN
        -- Streak broken
        v_current := 1;
      END IF;
    END IF;
    v_check := v_row.study_date;
  END LOOP;

  -- Upsert streak record
  INSERT INTO public.streaks (profile_id, current_streak, longest_streak, last_study_date)
  VALUES (p_profile_id, v_current, v_longest, COALESCE(v_last, CURRENT_DATE))
  ON CONFLICT (profile_id) WHERE deleted_at IS NULL
  DO UPDATE SET
    current_streak = EXCLUDED.current_streak,
    longest_streak = GREATEST(streaks.longest_streak, EXCLUDED.longest_streak),
    last_study_date = EXCLUDED.last_study_date,
    updated_at = now();

  RETURN QUERY SELECT v_current, v_longest, COALESCE(v_last, CURRENT_DATE);
END;
$$;

COMMENT ON FUNCTION public.fn_compute_streak(uuid) IS 'Computes and updates streak from subtopic completions.';

-- ---------------------------------------------------------------------------
-- Trigger: auto-update streak on subtopic completion change
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.studyos_update_streak_on_completion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  PERFORM public.fn_compute_streak(COALESCE(NEW.profile_id, OLD.profile_id));
  RETURN COALESCE(NEW, OLD);
END;
$$;

COMMENT ON FUNCTION public.studyos_update_streak_on_completion() IS 'Trigger function to update streak when completions change.';

DROP TRIGGER IF EXISTS update_streak_on_completion ON public.subtopic_completions;
CREATE TRIGGER update_streak_on_completion
  AFTER INSERT OR UPDATE OR DELETE ON public.subtopic_completions
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_update_streak_on_completion();

-- ---------------------------------------------------------------------------
-- RLS for streaks
-- ---------------------------------------------------------------------------
ALTER TABLE public.streaks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own streaks" ON public.streaks;
CREATE POLICY "Users can view own streaks" ON public.streaks
  FOR SELECT USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "System can insert streaks" ON public.streaks;
CREATE POLICY "System can insert streaks" ON public.streaks
  FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "System can update streaks" ON public.streaks;
CREATE POLICY "System can update streaks" ON public.streaks
  FOR UPDATE USING (true);
