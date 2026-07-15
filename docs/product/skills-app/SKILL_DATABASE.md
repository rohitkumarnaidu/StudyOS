# SKILL_DATABASE.md
# StudyOS — Database Design, Migrations & RLS Patterns
# Read before writing any SQL, migration, or RLS policy

---

## 1. SUPABASE SETUP & CONNECTION

### Environment variables
```bash
# .env.local (never commit)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxx... # Server-side only

# Verify in @studyos/config/env.ts
export const env = z.object({
  NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
  NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string(),
  SUPABASE_SERVICE_ROLE_KEY: z.string().optional(),
}).parse(process.env);
```

### Link to project
```bash
cd supabase/
supabase login
supabase link --project-ref=xxxxx
supabase db push  # Apply migrations
```

---

## 2. MIGRATION STRUCTURE (9 groups)

### Naming convention
```
20250613120000_extensions.sql
20250613120001_audit_and_row_versioning.sql
20250613120002_core_tenancy.sql
20250613120003_syllabus.sql
20250613120004_progress.sql
...
```

**Format:** `YYYYMMDDHHMMSS_<description>.sql`  
**Storage:** `supabase/migrations/`  
**Execution:** `supabase db push` (in CI: dry-run first)

### Group 001 — Extensions & audit
```sql
-- supabase/migrations/20250613120000_extensions.sql
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS uuid-ossp;
CREATE EXTENSION IF NOT EXISTS moddatetime;

-- Audit table (immutable event log)
CREATE TABLE audit_log (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  table_name TEXT NOT NULL,
  operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
  user_id UUID,
  old_data JSONB,
  new_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- System can write, users can only read their own changes
CREATE POLICY audit_insert ON audit_log FOR INSERT WITH CHECK (TRUE);
CREATE POLICY audit_select ON audit_log FOR SELECT USING (user_id = auth.uid() OR auth.role() = 'service_role');
```

### Group 002 — Core tenancy & profiles
```sql
-- supabase/migrations/20250613120002_core_tenancy.sql
CREATE TABLE institutes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,  -- subdomain: slug.studyos.app
  logo_url TEXT,
  color_primary TEXT DEFAULT '#6366F1',
  seats_max INT DEFAULT 100,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE,
  role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'institute_admin', 'platform_admin')) DEFAULT 'student',
  institute_id UUID REFERENCES institutes(id) ON DELETE SET NULL,
  exam_profile_id TEXT,  -- 'NEET_2026' etc
  full_name TEXT,
  avatar_url TEXT,
  tier TEXT DEFAULT 'bronze' CHECK (tier IN ('bronze', 'silver', 'gold')),
  language TEXT DEFAULT 'en',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit trigger for profiles
CREATE TRIGGER set_updated_at BEFORE UPDATE ON profiles
  FOR EACH ROW
  EXECUTE FUNCTION moddatetime(updated_at);

-- Signup trigger: auto-create profile on user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, username, full_name)
  VALUES (new.id, new.email, new.raw_user_meta_data->>'full_name');
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- RLS: users can only see/edit own profile
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY profiles_select ON profiles FOR SELECT USING (
  auth.uid() = id OR
  auth.role() = 'service_role'
);
CREATE POLICY profiles_update ON profiles FOR UPDATE USING (
  auth.uid() = id
) WITH CHECK (auth.uid() = id);

-- Indexes
CREATE INDEX ix_profiles_institute_id ON profiles(institute_id);
CREATE INDEX ix_profiles_role ON profiles(role);
```

### Group 003 — Syllabus tree
```sql
-- supabase/migrations/20250613120003_syllabus.sql
CREATE TABLE exam_profiles (
  id TEXT PRIMARY KEY,  -- 'NEET_2026'
  name TEXT NOT NULL,
  year INT,
  total_marks INT,
  duration_minutes INT,
  versions INT DEFAULT 1,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE chapters (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  exam_profile_id TEXT REFERENCES exam_profiles(id) ON DELETE CASCADE,
  number INT NOT NULL,
  name TEXT NOT NULL,
  subject TEXT NOT NULL CHECK (subject IN ('Physics', 'Chemistry', 'Biology', 'English')),
  description TEXT,
  ordering INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  chapter_id UUID NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  ordering INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE subtopics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  weight SMALLINT DEFAULT 1,  -- importance: 1-5
  ordering INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Public read, no RLS needed (syllabus is public knowledge)
CREATE INDEX ix_chapters_exam ON chapters(exam_profile_id);
CREATE INDEX ix_topics_chapter ON topics(chapter_id);
CREATE INDEX ix_subtopics_topic ON subtopics(topic_id);
```

### Group 004 — Progress & streaks
```sql
-- supabase/migrations/20250613120004_progress.sql
CREATE TABLE subtopic_completions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  subtopic_id UUID NOT NULL REFERENCES subtopics(id) ON DELETE CASCADE,
  completed_at TIMESTAMP WITH TIME ZONE,
  is_complete BOOLEAN DEFAULT FALSE,
  revision_count INT DEFAULT 0,
  last_revised_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, subtopic_id)
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  subtopic_id UUID NOT NULL REFERENCES subtopics(id) ON DELETE CASCADE,
  duration_minutes INT,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ended_at TIMESTAMP WITH TIME ZONE
);

-- RLS: users see only their own progress
ALTER TABLE subtopic_completions ENABLE ROW LEVEL SECURITY;
CREATE POLICY subtopic_completions_own ON subtopic_completions
  FOR ALL USING (user_id = auth.uid()) WITH CHECK (user_id = auth.uid());

-- Indexes for hot table
CREATE INDEX ix_completions_user ON subtopic_completions(user_id);
CREATE INDEX ix_completions_subtopic ON subtopic_completions(subtopic_id);
CREATE INDEX ix_completions_complete ON subtopic_completions(user_id, is_complete);
```

### Group 005 — Roadmaps (future)
```sql
-- supabase/migrations/YYYYMMDDHHMMSS_roadmap.sql
CREATE TABLE roadmap_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'completed', 'failed')) DEFAULT 'queued',
  input_data JSONB,  -- user tier, deadline, completed chapters
  output_data JSONB, -- generated roadmap JSON
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE weekly_plans (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  week_start_date DATE NOT NULL,
  plan_json JSONB,  -- { Mon: [...subtopics], Tue: [...], ... }
  generated_by_job_id UUID REFERENCES roadmap_jobs(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, week_start_date)
);

ALTER TABLE roadmap_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE weekly_plans ENABLE ROW LEVEL SECURITY;
CREATE POLICY roadmap_own ON roadmap_jobs FOR ALL USING (user_id = auth.uid());
CREATE POLICY weekly_plans_own ON weekly_plans FOR ALL USING (user_id = auth.uid());
```

### Group 006 — Quiz & assessments (future)
```sql
-- supabase/migrations/YYYYMMDDHHMMSS_quiz.sql
CREATE TABLE quiz_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  chapter_id UUID REFERENCES chapters(id),
  session_type TEXT CHECK (session_type IN ('chapter', 'mock', 'pyq')) DEFAULT 'chapter',
  status TEXT CHECK (status IN ('in_progress', 'completed', 'abandoned')) DEFAULT 'in_progress',
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  ended_at TIMESTAMP WITH TIME ZONE,
  score NUMERIC(5,2),
  total_questions INT,
  time_limit_minutes INT
);

CREATE TABLE quiz_attempts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES quiz_sessions(id) ON DELETE CASCADE,
  question_id TEXT NOT NULL,
  selected_option TEXT,
  is_correct BOOLEAN,
  time_spent_seconds INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE quiz_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
CREATE POLICY quiz_sessions_own ON quiz_sessions FOR ALL USING (user_id = auth.uid());
CREATE POLICY quiz_attempts_own ON quiz_attempts FOR ALL USING (
  EXISTS (SELECT 1 FROM quiz_sessions WHERE id = quiz_attempts.session_id AND user_id = auth.uid())
);
```

### Group 007 — Chat & conversations (future)
```sql
-- supabase/migrations/YYYYMMDDHHMMSS_chat.sql
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  chapter_id UUID REFERENCES chapters(id),
  title TEXT,
  langsmith_trace_id TEXT,  -- for debugging
  model_used TEXT,
  token_count INT DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  tokens_used INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY chat_sessions_own ON chat_sessions FOR ALL USING (user_id = auth.uid());
CREATE POLICY chat_messages_own ON chat_messages FOR ALL USING (
  EXISTS (SELECT 1 FROM chat_sessions WHERE id = chat_messages.session_id AND user_id = auth.uid())
);
```

### Group 008 — Analytics (future)
```sql
-- supabase/migrations/YYYYMMDDHHMMSS_analytics.sql
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
  event_name TEXT NOT NULL,
  properties JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Immutable + efficient for large volume
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
CREATE POLICY events_insert ON events FOR INSERT WITH CHECK (TRUE);

-- Batch table for daily rollups
CREATE TABLE daily_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID,
  metric_date DATE NOT NULL,
  chapters_completed INT,
  quiz_sessions INT,
  chat_messages INT,
  time_studied_minutes INT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, metric_date)
);

CREATE INDEX ix_events_user ON events(user_id);
CREATE INDEX ix_events_name ON events(event_name);
CREATE INDEX ix_daily_metrics_user ON daily_metrics(user_id);
```

### Group 009 — Billing (future)
```sql
-- supabase/migrations/YYYYMMDDHHMMSS_billing.sql
CREATE TABLE plans (
  id TEXT PRIMARY KEY,  -- 'free', 'pro', 'enterprise'
  name TEXT NOT NULL,
  price_inr NUMERIC(10,2),
  billing_period TEXT,
  features JSONB,  -- { "ai_daily_limit": 100, "offline": true, ... }
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- NOTE: Payments are out of scope for StudyOS (free platform).
-- These tables are reserved for future monetization if needed.
-- CREATE TABLE subscriptions (
--   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--   user_id UUID NOT NULL UNIQUE REFERENCES profiles(id) ON DELETE CASCADE,
--   plan_id TEXT NOT NULL REFERENCES plans(id),
--   status TEXT NOT NULL CHECK (status IN ('active', 'cancelled', 'expired')) DEFAULT 'active',
--   current_period_start DATE,
--   current_period_end DATE,
--   cancelled_at TIMESTAMP WITH TIME ZONE,
--   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );
-- 
-- CREATE TABLE invoices (
--   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--   user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
--   amount_inr NUMERIC(10,2),
--   status TEXT CHECK (status IN ('pending', 'paid', 'failed', 'refunded')) DEFAULT 'pending',
--   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--   paid_at TIMESTAMP WITH TIME ZONE
-- );

ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
CREATE POLICY subscriptions_own ON subscriptions FOR SELECT USING (user_id = auth.uid());
CREATE POLICY invoices_own ON invoices FOR SELECT USING (user_id = auth.uid());
```

---

## 3. RLS POLICY PATTERNS

### Template: User-scoped data (read & write own only)
```sql
CREATE POLICY <table>_own ON <table>
  FOR ALL
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
```

### Template: Institute-scoped data (teachers + admins see within institute)
```sql
CREATE POLICY <table>_institute ON <table>
  FOR SELECT
  USING (
    institute_id = (SELECT institute_id FROM profiles WHERE id = auth.uid())
    AND (SELECT role FROM profiles WHERE id = auth.uid()) IN ('teacher', 'institute_admin')
  );
```

### Template: Public data (no RLS needed)
```sql
-- Syllabus, exam profiles, study materials
-- No RLS = world-readable
```

### Testing RLS (critical)
```bash
# In CI: role-switching test matrix
psql -h localhost -p 5432 -U postgres -d studyos <<EOF
-- Test: student_a cannot read student_b's progress
SET request.jwt.claims.sub = 'student_a_uuid';
SELECT * FROM subtopic_completions WHERE user_id != 'student_a_uuid';
-- Should return 0 rows

-- Test: teacher can read students in institute
SET request.jwt.claims.sub = 'teacher_uuid';
SELECT * FROM profiles WHERE institute_id = (SELECT institute_id FROM profiles WHERE id = 'teacher_uuid');
-- Should return multiple student profiles
EOF
```

---

## 4. QUERY PATTERNS (TypeScript)

### Type-safe queries with generated types
```typescript
// Regenerate types after migration
// supabase gen types typescript --project-id=xxx > src/types/database.types.ts

import { createClient } from '@supabase/supabase-js';
import type { Database } from '../types/database.types';

const supabase = createClient<Database>(url, key);

// Typed query
async function getChapterCompletions(chapterId: string) {
  const { data, error } = await supabase
    .from('subtopic_completions')
    .select(`
      *,
      subtopic:subtopic_id (
        id,
        name,
        topic:topic_id (chapter_id)
      )
    `)
    .eq('subtopic.topic.chapter_id', chapterId)
    .eq('user_id', userId)
    .eq('is_complete', true);

  if (error) throw new Error(error.message);
  return data; // Fully typed!
}
```

### Server-side use-cases (FastAPI)
```python
# apps/api/studyos_api/use_cases/progress.py
from supabase import create_client

supabase = create_client(url, service_role_key)

def get_chapter_completion_percentage(user_id: str, chapter_id: str) -> float:
    """Server-side: bypasses RLS with service role"""
    response = supabase.table('subtopic_completions').select(
        'id',
        count='exact'
    ).eq('user_id', user_id).filter(
        'subtopic_id.topic_id.chapter_id.eq.' + chapter_id
    ).eq('is_complete', True).execute()
    
    completed = response.count
    total = get_subtopic_count_for_chapter(chapter_id)
    return (completed / total) * 100 if total > 0 else 0
```

---

## 5. PERFORMANCE & INDEXING

### Hot tables (high-traffic)
```sql
-- subtopic_completions: millions of rows at scale
CREATE INDEX ix_completions_user_complete ON subtopic_completions(user_id, is_complete)
  WHERE is_complete = TRUE;

-- Chat messages: frequent inserts/selects
CREATE INDEX ix_messages_session_created ON chat_messages(session_id, created_at DESC);

-- Events: append-only, query by user + event type
CREATE INDEX ix_events_user_name ON events(user_id, event_name, created_at DESC);
```

### Query optimization tips
1. Always use `select()` with only needed columns (not `*`)
2. Use **keyset pagination** on `(created_at, id)` for large result sets
3. Cache syllabus reads in Dexie or Upstash (immutable)
4. Batch operations when possible (bulk inserts)
5. Monitor slow queries: `supabase_logs` table or pg_stat_statements

---

## 6. BACKUP & DISASTER RECOVERY

### Scheduled backups
```bash
# Supabase Pro includes PITR (point-in-time recovery)
# Quarterly restore drill to staging:
supabase db push  # Reset staging schema
supabase db restore --from=<backup-timestamp>
```

### Export sensitive data
```bash
# Weekly export of subscriptions to data warehouse
SELECT * FROM subscriptions WHERE current_period_end >= NOW()
  LIMIT 1000 OFFSET :offset;
# Store in: gs://studyos-exports/subscriptions-2026-05-14.csv
```

---

## 7. COMMON MISTAKES TO AVOID

❌ **Never expose service role key in .env.example**  
✅ Use NEXT_PUBLIC_* only for anon key

❌ **Don't forget to enable RLS**  
✅ Always `ALTER TABLE x ENABLE ROW LEVEL SECURITY`

❌ **Forgetting RLS test in CI**  
✅ Add role-switching matrix test for every sensitive table

❌ **Not indexing hot tables**  
✅ Run `EXPLAIN ANALYZE` on hot queries; add indexes if seq_scan > 0

❌ **Allowing service role to be imported in web app**  
✅ Keep service role key in env vars only; never in import paths

❌ **Writing migrations without backward compatibility**  
✅ Use expand → migrate → contract pattern for schema changes

---

**See also:**
- `FINAL_ARCHITECTURE.md` § Database strategy
- `SYSTEM_DESIGN.md` § Request flows
- `docs/database/` → ERD.md, MIGRATIONS_AND_SEEDS.md, INDEXING_AND_QUERIES.md
