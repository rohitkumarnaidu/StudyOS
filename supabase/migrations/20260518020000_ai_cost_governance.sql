-- Phase 0.6: AI Cost & Governance (Free-Tier Friendly)
-- Usage tracking, audit trail, soft alerts — no hard limits

-- AI usage log: tracks every AI call for analytics
CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    feature TEXT NOT NULL,
    model TEXT NOT NULL,
    provider TEXT NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd NUMERIC(10, 6) DEFAULT 0.00,
    duration_ms NUMERIC(10, 2) DEFAULT 0,
    status TEXT DEFAULT 'success',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI audit trail: logs prompt/response pairs for compliance
CREATE TABLE IF NOT EXISTS ai_audit_trail (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    feature TEXT NOT NULL,
    model TEXT NOT NULL,
    provider TEXT NOT NULL,
    prompt_preview TEXT,
    response_preview TEXT,
    status TEXT DEFAULT 'success',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Soft budget thresholds (informational only, never blocks)
CREATE TABLE IF NOT EXISTS ai_budget_thresholds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL UNIQUE,
    token_limit INTEGER DEFAULT 1000000,
    request_limit INTEGER DEFAULT 10000,
    alert_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prompt safety log: tracks blocked injection attempts
CREATE TABLE IF NOT EXISTS ai_safety_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID,
    risk_level TEXT NOT NULL,
    blocked BOOLEAN DEFAULT false,
    reasons TEXT[],
    feature TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ai_usage_profile ON ai_usage_logs(profile_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_feature ON ai_usage_logs(feature);
CREATE INDEX IF NOT EXISTS idx_ai_usage_created ON ai_usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_audit_profile ON ai_audit_trail(profile_id);
CREATE INDEX IF NOT EXISTS idx_ai_audit_feature ON ai_audit_trail(feature);
CREATE INDEX IF NOT EXISTS idx_ai_audit_created ON ai_audit_trail(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_safety_profile ON ai_safety_log(profile_id);
CREATE INDEX IF NOT EXISTS idx_ai_safety_risk ON ai_safety_log(risk_level);

-- RLS
ALTER TABLE ai_usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_audit_trail ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_budget_thresholds ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_safety_log ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own usage logs"
    ON ai_usage_logs FOR SELECT
    USING (profile_id = auth.uid());

CREATE POLICY "Users can view own audit trail"
    ON ai_audit_trail FOR SELECT
    USING (profile_id = auth.uid());

CREATE POLICY "Users can manage own budget thresholds"
    ON ai_budget_thresholds FOR ALL
    USING (profile_id = auth.uid());

CREATE POLICY "Users can view own safety log"
    ON ai_safety_log FOR SELECT
    USING (profile_id = auth.uid());

-- Auto-update trigger
CREATE TRIGGER update_ai_budget_thresholds_updated_at
    BEFORE UPDATE ON ai_budget_thresholds
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
