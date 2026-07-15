-- Phase 0.7: Feature Flag System
-- Local flag definitions, sync logs, and rollout tracking

-- Feature flag definitions
CREATE TABLE IF NOT EXISTS feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    enabled BOOLEAN DEFAULT false,
    rollout_percentage NUMERIC(5, 2) DEFAULT 100.0,
    conditions JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Flag sync log (tracks PostHog syncs)
CREATE TABLE IF NOT EXISTS flag_sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT DEFAULT 'posthog',
    flags_synced INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    synced_at TIMESTAMPTZ DEFAULT NOW()
);

-- Flag evaluation log (for analytics)
CREATE TABLE IF NOT EXISTS flag_evaluation_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_key TEXT NOT NULL,
    user_id UUID,
    result BOOLEAN NOT NULL,
    context JSONB DEFAULT '{}',
    evaluated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_feature_flags_key ON feature_flags(key);
CREATE INDEX IF NOT EXISTS idx_flag_sync_log_synced ON flag_sync_log(synced_at);
CREATE INDEX IF NOT EXISTS idx_flag_eval_flag ON flag_evaluation_log(flag_key);
CREATE INDEX IF NOT EXISTS idx_flag_eval_user ON flag_evaluation_log(user_id);
CREATE INDEX IF NOT EXISTS idx_flag_eval_time ON flag_evaluation_log(evaluated_at);

-- RLS
ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE flag_sync_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE flag_evaluation_log ENABLE ROW LEVEL SECURITY;

-- Only admins can manage flags (placeholder policy)
CREATE POLICY "Admins can manage feature flags"
    ON feature_flags FOR ALL
    USING (auth.jwt() ->> 'role' = 'admin');

-- Users can view active flags
CREATE POLICY "Users can view active flags"
    ON feature_flags FOR SELECT
    USING (enabled = true);

-- System logs are read-only
CREATE POLICY "System logs are read-only"
    ON flag_sync_log FOR SELECT
    USING (true);

CREATE POLICY "System logs are read-only"
    ON flag_evaluation_log FOR SELECT
    USING (true);

-- Auto-update trigger
CREATE TRIGGER update_feature_flags_updated_at
    BEFORE UPDATE ON feature_flags
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Seed default flags
INSERT INTO feature_flags (key, enabled, rollout_percentage, metadata) VALUES
    ('smart_revision', true, 100.0, '{"description": "AI-powered spaced revision engine"}'),
    ('mistake_intelligence', true, 100.0, '{"description": "AI mistake pattern detection"}'),
    ('ai_mock_test', true, 80.0, '{"description": "AI-generated mock tests"}'),
    ('knowledge_graph', false, 0.0, '{"description": "Interactive knowledge graph visualization"}'),
    ('notebooklm', false, 0.0, '{"description": "AI NotebookLM-style Q&A"}'),
    ('voice_tutor', false, 0.0, '{"description": "AI voice-based tutoring"}'),
    ('battle_arena', false, 0.0, '{"description": "1v1 quiz battle mode"}'),
    ('offline_mode', true, 100.0, '{"description": "Offline-first PWA support"}')
ON CONFLICT (key) DO NOTHING;
