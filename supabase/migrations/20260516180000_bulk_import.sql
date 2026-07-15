-- StudyOS — Phase 4: Bulk import jobs for processing 400+ PDFs.

CREATE TABLE IF NOT EXISTS public.bulk_import_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  chapter_id uuid REFERENCES public.chapters(id) ON DELETE SET NULL,
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
  total_files int NOT NULL DEFAULT 0,
  processed_files int NOT NULL DEFAULT 0,
  failed_files int NOT NULL DEFAULT 0,
  file_list jsonb,
  error_message text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  deleted_at timestamptz,
  row_version bigint NOT NULL DEFAULT 1
);

COMMENT ON TABLE public.bulk_import_jobs IS 'Tracks bulk PDF import processing jobs.';

CREATE INDEX IF NOT EXISTS bulk_import_jobs_profile_live_idx ON public.bulk_import_jobs(profile_id, created_at DESC)
WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS bulk_import_jobs_status_live_idx ON public.bulk_import_jobs(profile_id, status)
WHERE deleted_at IS NULL;

DROP TRIGGER IF EXISTS bulk_import_jobs_touch_updated ON public.bulk_import_jobs;
CREATE TRIGGER bulk_import_jobs_touch_updated
  BEFORE UPDATE ON public.bulk_import_jobs
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_set_updated_at();

DROP TRIGGER IF EXISTS bulk_import_jobs_bump_version ON public.bulk_import_jobs;
CREATE TRIGGER bulk_import_jobs_bump_version
  BEFORE UPDATE ON public.bulk_import_jobs
  FOR EACH ROW
  EXECUTE FUNCTION public.studyos_bump_row_version();

-- RLS
ALTER TABLE public.bulk_import_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own bulk import jobs" ON public.bulk_import_jobs;
CREATE POLICY "Users can view own bulk import jobs" ON public.bulk_import_jobs
  FOR SELECT USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can create bulk import jobs" ON public.bulk_import_jobs;
CREATE POLICY "Users can create bulk import jobs" ON public.bulk_import_jobs
  FOR INSERT WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can update own bulk import jobs" ON public.bulk_import_jobs;
CREATE POLICY "Users can update own bulk import jobs" ON public.bulk_import_jobs
  FOR UPDATE USING (auth.uid() = profile_id);
