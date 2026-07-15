-- StudyOS — Phase 8: AI Roadmap Engine (Priority Scoring, Performance Prediction, Recovery Plans)

-- Priority scoring per chapter
CREATE TABLE IF NOT EXISTS public.priority_scores (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    chapter_id uuid NOT NULL REFERENCES public.chapters(id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL DEFAULT 0,
    weightage_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    time_remaining_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    weak_area_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    exam_proximity_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    computed_at timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE(profile_id, chapter_id)
);

COMMENT ON TABLE public.priority_scores IS 'Dynamic priority scores per chapter for roadmap generation.';

CREATE INDEX IF NOT EXISTS idx_priority_scores_profile ON public.priority_scores(profile_id, score DESC);

-- ML-based performance predictions
CREATE TABLE IF NOT EXISTS public.performance_predictions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    predicted_score DECIMAL(5,2) NOT NULL,
    confidence_interval_lower DECIMAL(5,2),
    confidence_interval_upper DECIMAL(5,2),
    prediction_date date NOT NULL DEFAULT CURRENT_DATE,
    model_version VARCHAR(32) DEFAULT 'v1',
    features_used JSONB NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.performance_predictions IS 'ML-based performance predictions with confidence intervals.';

CREATE INDEX IF NOT EXISTS idx_performance_predictions_profile ON public.performance_predictions(profile_id, prediction_date DESC);

-- Recovery plans for struggling students
CREATE TABLE IF NOT EXISTS public.recovery_plans (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    roadmap_id uuid REFERENCES public.roadmaps(id) ON DELETE SET NULL,
    trigger_reason VARCHAR(64) NOT NULL,
    original_completion_date date,
    revised_completion_date date,
    accelerated_chapters JSONB NOT NULL DEFAULT '[]',
    skipped_chapters JSONB NOT NULL DEFAULT '[]',
    daily_hours_target DECIMAL(3,1) NOT NULL DEFAULT 6,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE public.recovery_plans IS 'Accelerated recovery plans for students behind schedule.';

CREATE INDEX IF NOT EXISTS idx_recovery_plans_profile ON public.recovery_plans(profile_id, status);

DROP TRIGGER IF EXISTS recovery_plans_touch_updated ON public.recovery_plans;
CREATE TRIGGER recovery_plans_touch_updated
    BEFORE UPDATE ON public.recovery_plans
    FOR EACH ROW
    EXECUTE FUNCTION public.studyos_set_updated_at();

-- RLS
ALTER TABLE public.priority_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recovery_plans ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own priority scores" ON public.priority_scores;
CREATE POLICY "Users can manage own priority scores" ON public.priority_scores
    FOR ALL USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can manage own performance predictions" ON public.performance_predictions;
CREATE POLICY "Users can manage own performance predictions" ON public.performance_predictions
    FOR ALL USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Users can manage own recovery plans" ON public.recovery_plans;
CREATE POLICY "Users can manage own recovery plans" ON public.recovery_plans
    FOR ALL USING (auth.uid() = profile_id);
