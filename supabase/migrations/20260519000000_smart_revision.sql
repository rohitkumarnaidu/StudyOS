-- Phase 1.1: Smart Revision Engine
-- SM-2 spaced repetition, retention tracking, revision packs, active recall

-- Revision items: tracks SM-2 state for each reviewable item
CREATE TABLE IF NOT EXISTS revision_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    source_type TEXT NOT NULL,
    source_id UUID NOT NULL,
    ease_factor NUMERIC(4, 2) DEFAULT 2.5,
    interval_days INTEGER DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    next_review DATE NOT NULL,
    last_quality NUMERIC(3, 1) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT revision_items_profile_source_unique UNIQUE (profile_id, source_type, source_id)
);

-- Revision sessions: tracks completed revision sessions
CREATE TABLE IF NOT EXISTS revision_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    session_type TEXT NOT NULL DEFAULT 'spaced_repetition',
    items_reviewed INTEGER DEFAULT 0,
    retention_rate NUMERIC(4, 3) DEFAULT 0.0,
    duration_seconds INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

-- Retention records: tracks predicted vs actual retention for model calibration
CREATE TABLE IF NOT EXISTS retention_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    revision_item_id UUID REFERENCES revision_items(id) ON DELETE CASCADE,
    days_since_review INTEGER NOT NULL,
    predicted_retention NUMERIC(4, 3),
    actual_retention NUMERIC(4, 3),
    quality_score NUMERIC(3, 1),
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Revision packs: curated sets of items for focused revision
CREATE TABLE IF NOT EXISTS revision_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    pack_type TEXT NOT NULL,
    items JSONB NOT NULL DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Active recall sessions: self-testing sessions
CREATE TABLE IF NOT EXISTS active_recall_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    session_type TEXT DEFAULT 'free_recall',
    questions JSONB NOT NULL DEFAULT '[]',
    current_index INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    total_answered INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_revision_items_profile ON revision_items(profile_id);
CREATE INDEX IF NOT EXISTS idx_revision_items_next_review ON revision_items(next_review);
CREATE INDEX IF NOT EXISTS idx_revision_items_due ON revision_items(profile_id, next_review);
CREATE INDEX IF NOT EXISTS idx_revision_sessions_profile ON revision_sessions(profile_id);
CREATE INDEX IF NOT EXISTS idx_retention_records_profile ON retention_records(profile_id);
CREATE INDEX IF NOT EXISTS idx_retention_records_item ON retention_records(revision_item_id);
CREATE INDEX IF NOT EXISTS idx_revision_packs_profile ON revision_packs(profile_id);
CREATE INDEX IF NOT EXISTS idx_active_recall_profile ON active_recall_sessions(profile_id);

-- RLS
ALTER TABLE revision_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE revision_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE retention_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE revision_packs ENABLE ROW LEVEL SECURITY;
ALTER TABLE active_recall_sessions ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY "Users can manage own revision items"
    ON revision_items FOR ALL
    USING (profile_id = auth.uid());

CREATE POLICY "Users can manage own revision sessions"
    ON revision_sessions FOR ALL
    USING (profile_id = auth.uid());

CREATE POLICY "Users can manage own retention records"
    ON retention_records FOR ALL
    USING (profile_id = auth.uid());

CREATE POLICY "Users can manage own revision packs"
    ON revision_packs FOR ALL
    USING (profile_id = auth.uid());

CREATE POLICY "Users can manage own active recall sessions"
    ON active_recall_sessions FOR ALL
    USING (profile_id = auth.uid());

-- Auto-update triggers
CREATE TRIGGER update_revision_items_updated_at
    BEFORE UPDATE ON revision_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
