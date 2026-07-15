# SKILL_DATABASE.md
# StudyOS — PostgreSQL + pgvector + Supabase Database Patterns
# Read BEFORE writing any SQL, migration, RLS policy, or DB query

---

## 1. COMPLETE DATABASE SCHEMA (9 Migrations)

### Migration 001 — Auth + Users
```sql
-- Enable extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- profiles (extends Supabase auth.users)
create table public.profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  full_name     text not null,
  phone         text,
  city          text,
  state         text,
  exam_type     text not null default 'NEET' check (exam_type in ('NEET','JEE_MAINS','JEE_ADV','CUSTOM')),
  class_level   text not null default 'DROPPER' check (class_level in ('CLASS_11','CLASS_12','DROPPER')),
  exam_date     date,
  study_hours   int not null default 6 check (study_hours between 2 and 16),
  language      text not null default 'en' check (language in ('en','ta','te','hi','kn','ml')),
  streak_count  int not null default 0,
  last_active   timestamptz default now(),
  plan          text not null default 'free' check (plan in ('free','pro','institute')),
  plan_expires  timestamptz,
  institute_id  uuid references public.institutes(id),
  avatar_url    text,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- institutes (for B2B multi-tenant)
create table public.institutes (
  id            uuid primary key default uuid_generate_v4(),
  name          text not null,
  city          text,
  state         text,
  owner_id      uuid references auth.users(id),
  plan          text not null default 'basic' check (plan in ('basic','pro','enterprise')),
  seat_limit    int not null default 50,
  created_at    timestamptz not null default now()
);

-- RLS
alter table public.profiles enable row level security;
create policy "Users can view own profile" on public.profiles for select using (auth.uid() = id);
create policy "Users can update own profile" on public.profiles for update using (auth.uid() = id);
create policy "Institute admins can view members" on public.profiles for select
  using (institute_id in (select id from public.institutes where owner_id = auth.uid()));

-- Trigger: auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, full_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name', 'Student'));
  return new;
end;
$$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute procedure public.handle_new_user();
```

### Migration 002 — Syllabus (Seeded Data)
```sql
-- subjects
create table public.subjects (
  id          uuid primary key default uuid_generate_v4(),
  name        text not null,              -- 'Physics', 'Chemistry', 'Biology'
  code        text not null unique,       -- 'PHY', 'CHE', 'BIO'
  exam_type   text not null default 'NEET',
  total_marks int not null default 180,
  total_qs    int not null default 45,
  color_hex   text not null default '#6366F1'
);

-- chapters (79 for NEET 2026)
create table public.chapters (
  id              uuid primary key default uuid_generate_v4(),
  subject_id      uuid not null references public.subjects(id),
  name            text not null,
  class_level     text not null check (class_level in ('11','12')),
  chapter_number  int not null,
  tier            int not null check (tier between 1 and 3),  -- 1=highest yield
  weightage_pct   numeric(4,1),  -- e.g. 14.0 for Molecular Biology
  avg_questions   numeric(3,1),  -- average questions per NEET paper
  deleted         boolean not null default false,  -- NTA deleted topics flag
  ncert_pages     text,          -- e.g. "111-145" for reference
  display_order   int not null default 0
);

-- topics (subtopics within chapter)
create table public.topics (
  id            uuid primary key default uuid_generate_v4(),
  chapter_id    uuid not null references public.chapters(id) on delete cascade,
  name          text not null,
  description   text,
  is_high_yield boolean not null default false,
  is_deleted    boolean not null default false,  -- NTA deleted
  difficulty    text check (difficulty in ('easy','medium','hard')),
  display_order int not null default 0
);

-- indexes for performance
create index idx_chapters_subject on public.chapters(subject_id);
create index idx_topics_chapter on public.topics(chapter_id);
create index idx_chapters_tier on public.chapters(tier);
```

### Migration 003 — Student Progress
```sql
-- chapter_progress (one row per student per chapter)
create table public.chapter_progress (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  chapter_id      uuid not null references public.chapters(id),
  status          text not null default 'not_started'
                  check (status in ('not_started','in_progress','completed','needs_revision')),
  confidence      int check (confidence between 1 and 5),
  completion_pct  numeric(5,2) not null default 0,
  first_started   timestamptz,
  completed_at    timestamptz,
  last_studied    timestamptz,
  -- spaced repetition
  next_revision   timestamptz,
  revision_count  int not null default 0,
  ease_factor     numeric(4,2) not null default 2.5,  -- SM-2 algorithm
  unique(user_id, chapter_id)
);

-- topic_progress (one row per student per topic)
create table public.topic_progress (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  topic_id      uuid not null references public.topics(id),
  completed     boolean not null default false,
  completed_at  timestamptz,
  time_spent_s  int not null default 0,  -- seconds
  unique(user_id, topic_id)
);

-- study_sessions (for time tracking + streak)
create table public.study_sessions (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  chapter_id    uuid references public.chapters(id),
  started_at    timestamptz not null default now(),
  ended_at      timestamptz,
  duration_s    int,         -- computed on end
  session_type  text check (session_type in ('study','revision','quiz','mock')),
  topics_done   int not null default 0
);

-- RLS
alter table public.chapter_progress enable row level security;
alter table public.topic_progress enable row level security;
alter table public.study_sessions enable row level security;
create policy "Own progress only" on public.chapter_progress
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Own topic progress only" on public.topic_progress
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "Own sessions only" on public.study_sessions
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- indexes
create index idx_chapter_progress_user on public.chapter_progress(user_id);
create index idx_topic_progress_user on public.topic_progress(user_id);
create index idx_study_sessions_user_date on public.study_sessions(user_id, started_at desc);
```

### Migration 004 — Notes
```sql
-- notes
create table public.notes (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  chapter_id      uuid references public.chapters(id),
  title           text,
  content_md      text,         -- processed markdown
  content_raw     text,         -- original OCR / pasted text
  source_type     text check (source_type in ('upload','camera','typed','ai_generated')),
  file_url        text,         -- Supabase Storage URL
  file_type       text,         -- 'pdf','jpg','png','txt'
  ocr_quality     numeric(3,2), -- 0.0–1.0
  extraction_done boolean not null default false,
  is_public       boolean not null default false,
  tags            text[],
  word_count      int,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);

-- note_extractions (AI-extracted topics from note)
create table public.note_extractions (
  id            uuid primary key default uuid_generate_v4(),
  note_id       uuid not null references public.notes(id) on delete cascade,
  topic_id      uuid references public.topics(id),
  chapter_id    uuid references public.chapters(id),
  extracted_text text,
  confidence    numeric(3,2),
  confirmed     boolean not null default false,  -- student confirmed this mapping
  created_at    timestamptz not null default now()
);

-- RLS
alter table public.notes enable row level security;
create policy "Own notes" on public.notes
  using (auth.uid() = user_id or is_public = true)
  with check (auth.uid() = user_id);
alter table public.note_extractions enable row level security;
create policy "Own extractions" on public.note_extractions
  using (note_id in (select id from public.notes where user_id = auth.uid()));
```

### Migration 005 — Roadmap
```sql
-- roadmaps (generated weekly study plans)
create table public.roadmaps (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  generated_at    timestamptz not null default now(),
  exam_date       date not null,
  total_weeks     int not null,
  is_active       boolean not null default true,
  ai_model        text,  -- which model generated this
  generation_ms   int    -- how long it took to generate
);

-- roadmap_weeks
create table public.roadmap_weeks (
  id            uuid primary key default uuid_generate_v4(),
  roadmap_id    uuid not null references public.roadmaps(id) on delete cascade,
  week_number   int not null,
  theme         text,   -- e.g. "Genetics Marathon 🧬"
  ai_tip        text,
  start_date    date,
  end_date      date,
  display_order int not null default 0
);

-- roadmap_items (chapters within a week)
create table public.roadmap_items (
  id            uuid primary key default uuid_generate_v4(),
  week_id       uuid not null references public.roadmap_weeks(id) on delete cascade,
  chapter_id    uuid not null references public.chapters(id),
  day_of_week   int check (day_of_week between 1 and 7),  -- 1=Mon
  hours_planned numeric(3,1),
  item_type     text check (item_type in ('study','revision','quiz','rest')),
  completed     boolean not null default false,
  display_order int not null default 0
);

-- RLS
alter table public.roadmaps enable row level security;
alter table public.roadmap_weeks enable row level security;
alter table public.roadmap_items enable row level security;
create policy "Own roadmaps" on public.roadmaps using (auth.uid() = user_id);
create policy "Own weeks" on public.roadmap_weeks
  using (roadmap_id in (select id from public.roadmaps where user_id = auth.uid()));
create policy "Own items" on public.roadmap_items
  using (week_id in (select id from public.roadmap_weeks
    where roadmap_id in (select id from public.roadmaps where user_id = auth.uid())));
```

### Migration 006 — Quiz + Questions
```sql
-- questions (PYQ + AI-generated)
create table public.questions (
  id              uuid primary key default uuid_generate_v4(),
  chapter_id      uuid not null references public.chapters(id),
  topic_id        uuid references public.topics(id),
  stem            text not null,           -- question text
  option_a        text not null,
  option_b        text not null,
  option_c        text not null,
  option_d        text not null,
  correct_option  text not null check (correct_option in ('A','B','C','D')),
  explanation     text,
  difficulty      text check (difficulty in ('easy','medium','hard')),
  source          text check (source in ('pyq','ai_generated','teacher')),
  pyq_year        int,                     -- e.g. 2023 for PYQ
  is_trap         boolean not null default false,
  tags            text[],
  created_at      timestamptz not null default now()
);

-- quiz_sessions
create table public.quiz_sessions (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  chapter_id      uuid references public.chapters(id),
  quiz_type       text check (quiz_type in ('chapter','topic','weak_area','full_mock','pyq')),
  total_qs        int not null,
  attempted       int not null default 0,
  correct         int not null default 0,
  wrong           int not null default 0,
  score           int not null default 0,   -- +4/-1 scoring
  max_score       int not null,
  accuracy_pct    numeric(5,2),
  time_taken_s    int,
  started_at      timestamptz not null default now(),
  completed_at    timestamptz,
  subject_filter  text[]                    -- for multi-subject mocks
);

-- quiz_answers (per-question response)
create table public.quiz_answers (
  id              uuid primary key default uuid_generate_v4(),
  session_id      uuid not null references public.quiz_sessions(id) on delete cascade,
  question_id     uuid not null references public.questions(id),
  chosen_option   text check (chosen_option in ('A','B','C','D')),  -- null = skipped
  is_correct      boolean,
  time_taken_s    int,
  marked_review   boolean not null default false,
  answered_at     timestamptz not null default now()
);

-- mistake_log (wrong answers for revision)
create table public.mistake_log (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  question_id     uuid not null references public.questions(id),
  chapter_id      uuid references public.chapters(id),
  wrong_option    text,
  correct_option  text,
  error_type      text check (error_type in ('concept_gap','silly_mistake','trap','guess','time_pressure')),
  resolved        boolean not null default false,
  resolved_at     timestamptz,
  occurrence_count int not null default 1,
  last_seen       timestamptz not null default now(),
  unique(user_id, question_id)
);

-- RLS
alter table public.quiz_sessions enable row level security;
alter table public.quiz_answers enable row level security;
alter table public.mistake_log enable row level security;
create policy "Own quiz sessions" on public.quiz_sessions using (auth.uid() = user_id);
create policy "Own quiz answers" on public.quiz_answers
  using (session_id in (select id from public.quiz_sessions where user_id = auth.uid()));
create policy "Own mistakes" on public.mistake_log using (auth.uid() = user_id);

-- indexes
create index idx_questions_chapter on public.questions(chapter_id);
create index idx_quiz_sessions_user on public.quiz_sessions(user_id, started_at desc);
create index idx_mistake_log_user on public.mistake_log(user_id, resolved, last_seen desc);
```

### Migration 007 — Chat History
```sql
-- chat_sessions
create table public.chat_sessions (
  id            uuid primary key default uuid_generate_v4(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  chapter_id    uuid references public.chapters(id),
  topic_id      uuid references public.topics(id),
  title         text,       -- auto-generated from first message
  llm_provider  text,
  llm_model     text,
  total_tokens  int not null default 0,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- chat_messages
create table public.chat_messages (
  id            uuid primary key default uuid_generate_v4(),
  session_id    uuid not null references public.chat_sessions(id) on delete cascade,
  role          text not null check (role in ('user','assistant','system')),
  content       text not null,
  tokens_used   int,
  latency_ms    int,
  is_error      boolean not null default false,
  citations     jsonb,       -- [{chapter, page, text}]
  created_at    timestamptz not null default now()
);

-- RLS
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;
create policy "Own chats" on public.chat_sessions using (auth.uid() = user_id);
create policy "Own messages" on public.chat_messages
  using (session_id in (select id from public.chat_sessions where user_id = auth.uid()));
```

### Migration 008 — Analytics Events
```sql
-- events (raw analytics stream)
create table public.events (
  id          bigserial primary key,
  user_id     uuid references auth.users(id),
  session_id  text,          -- anonymous before login
  event_type  text not null, -- 'subtopic_completed', 'quiz_attempted', etc.
  properties  jsonb,         -- flexible event properties
  platform    text check (platform in ('web','ios','android','pwa')),
  app_version text,
  created_at  timestamptz not null default now()
);

-- partitioned by month for performance (optional, add after 100k rows)
-- create index idx_events_user_date on public.events(user_id, created_at desc);
-- create index idx_events_type on public.events(event_type, created_at desc);

-- RLS: write-only for users, read for admins
alter table public.events enable row level security;
create policy "Insert own events" on public.events for insert with check (auth.uid() = user_id);
create policy "Admin read events" on public.events for select using (
  auth.uid() in (select id from auth.users where raw_user_meta_data->>'role' = 'admin')
);
```

### Migration 009 — Payments + Flashcards
```sql
-- subscriptions
create table public.subscriptions (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id),
  plan            text not null check (plan in ('pro_monthly','pro_annual','institute')),
  status          text not null check (status in ('active','cancelled','expired','trial')),
  razorpay_sub_id text unique,
  amount_paise    int,             -- amount in paise (₹299 = 29900)
  currency        text default 'INR',
  started_at      timestamptz not null default now(),
  expires_at      timestamptz,
  cancelled_at    timestamptz
);

-- flashcards (spaced repetition)
create table public.flashcards (
  id              uuid primary key default uuid_generate_v4(),
  user_id         uuid not null references auth.users(id) on delete cascade,
  chapter_id      uuid references public.chapters(id),
  topic_id        uuid references public.topics(id),
  front           text not null,   -- question / term
  back            text not null,   -- answer / definition
  source          text check (source in ('ai_generated','user_created','pyq')),
  -- SM-2 spaced repetition fields
  ease_factor     numeric(4,2) not null default 2.5,
  interval_days   int not null default 1,
  repetitions     int not null default 0,
  next_review     timestamptz not null default now(),
  last_reviewed   timestamptz,
  created_at      timestamptz not null default now()
);

-- RLS
alter table public.subscriptions enable row level security;
alter table public.flashcards enable row level security;
create policy "Own subscriptions" on public.subscriptions using (auth.uid() = user_id);
create policy "Own flashcards" on public.flashcards using (auth.uid() = user_id);
```

---

## 2. VECTOR STORE (pgvector)

```sql
-- Enable pgvector
create extension if not exists vector;

-- NCERT content chunks (for RAG)
create table public.ncert_chunks (
  id          bigserial primary key,
  chapter_id  uuid not null references public.chapters(id),
  chunk_text  text not null,
  page_number int,
  chunk_index int,
  embedding   vector(1536),   -- text-embedding-3-small dimensions
  created_at  timestamptz not null default now()
);

-- Note embeddings (for semantic note search)
create table public.note_embeddings (
  id          bigserial primary key,
  note_id     uuid not null references public.notes(id) on delete cascade,
  chunk_text  text not null,
  chunk_index int,
  embedding   vector(1536),
  created_at  timestamptz not null default now()
);

-- Question embeddings (for similar question search)
create table public.question_embeddings (
  id          bigserial primary key,
  question_id uuid not null references public.questions(id) on delete cascade,
  embedding   vector(1536),
  created_at  timestamptz not null default now()
);

-- HNSW index for fast similarity search (much faster than IVFFlat for <1M rows)
create index idx_ncert_chunks_embedding on public.ncert_chunks
  using hnsw (embedding vector_cosine_ops) with (m = 16, ef_construction = 64);
create index idx_note_embeddings_embedding on public.note_embeddings
  using hnsw (embedding vector_cosine_ops) with (m = 16, ef_construction = 64);

-- Similarity search function
create or replace function match_ncert_chunks(
  query_embedding vector(1536),
  chapter_filter  uuid default null,
  match_count     int default 5
)
returns table (
  id          bigint,
  chunk_text  text,
  page_number int,
  chapter_id  uuid,
  similarity  float
) language plpgsql as $$
begin
  return query
  select
    n.id, n.chunk_text, n.page_number, n.chapter_id,
    1 - (n.embedding <=> query_embedding) as similarity
  from public.ncert_chunks n
  where (chapter_filter is null or n.chapter_id = chapter_filter)
  order by n.embedding <=> query_embedding
  limit match_count;
end;
$$;
```

---

## 3. QUERY PATTERNS

### Get student dashboard data (single query)
```typescript
async function getDashboardData(userId: string) {
  const { data, error } = await supabase.rpc('get_dashboard_data', {
    p_user_id: userId
  });
  if (error) throw error;
  return data;
}

-- Supabase function for dashboard (reduces roundtrips from 6 to 1)
create or replace function get_dashboard_data(p_user_id uuid)
returns json language plpgsql security definer as $$
declare
  result json;
begin
  select json_build_object(
    'profile', (select row_to_json(p) from public.profiles p where id = p_user_id),
    'subject_progress', (
      select json_agg(json_build_object(
        'subject', s.name,
        'completion_pct', avg(cp.completion_pct)
      ))
      from public.subjects s
      join public.chapters c on c.subject_id = s.id
      left join public.chapter_progress cp on cp.chapter_id = c.id and cp.user_id = p_user_id
      group by s.id, s.name
    ),
    'streak', (select streak_count from public.profiles where id = p_user_id),
    'weak_chapters', (
      select json_agg(row_to_json(wc)) from (
        select c.name, c.id, cp.completion_pct, cp.last_studied
        from public.chapter_progress cp
        join public.chapters c on c.id = cp.chapter_id
        where cp.user_id = p_user_id
        order by cp.completion_pct asc, c.tier asc
        limit 3
      ) wc
    ),
    'today_sessions', (
      select count(*) from public.study_sessions
      where user_id = p_user_id and started_at > current_date
    )
  ) into result;
  return result;
end;
$$;
```

### Spaced repetition due query
```typescript
async function getDueRevisions(userId: string) {
  const { data, error } = await supabase
    .from('chapter_progress')
    .select('*, chapters(name, subject_id, subjects(name, color_hex))')
    .eq('user_id', userId)
    .lte('next_revision', new Date().toISOString())
    .order('next_revision', { ascending: true })
    .limit(10);
  if (error) throw error;
  return data;
}
```

### Update SM-2 spaced repetition after review
```typescript
function calculateNextReview(
  quality: 0 | 1 | 2 | 3 | 4 | 5, // 0-2 = fail, 3-5 = pass
  easeFactor: number,
  intervalDays: number,
  repetitions: number
) {
  if (quality < 3) {
    return { interval: 1, repetitions: 0, easeFactor };
  }
  const newEF = Math.max(1.3, easeFactor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
  const newInterval = repetitions === 0 ? 1
    : repetitions === 1 ? 6
    : Math.round(intervalDays * newEF);
  return { interval: newInterval, repetitions: repetitions + 1, easeFactor: newEF };
}
```

---

## 4. INDEXING STRATEGY

```sql
-- Most important indexes (run these in production)
create index concurrently idx_chapter_progress_user_status
  on public.chapter_progress(user_id, status) where status != 'completed';

create index concurrently idx_study_sessions_streak
  on public.study_sessions(user_id, date_trunc('day', started_at));

create index concurrently idx_mistake_log_unresolved
  on public.mistake_log(user_id, chapter_id) where resolved = false;

create index concurrently idx_questions_chapter_difficulty
  on public.questions(chapter_id, difficulty, source);

create index concurrently idx_flashcards_due
  on public.flashcards(user_id, next_review) where next_review <= now();

-- Full text search on notes
alter table public.notes add column search_vector tsvector
  generated always as (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(content_md,''))) stored;
create index idx_notes_fts on public.notes using gin(search_vector);
```

---

## 5. PERFORMANCE RULES

```
NEVER:
  ❌ select * from large tables — always specify columns
  ❌ N+1 queries — use joins or batch requests
  ❌ Run DB queries in loops — collect ids, run single IN() query
  ❌ Forget indexes on foreign keys — Supabase doesn't auto-create them
  ❌ Store embeddings for every note chunk > 500 tokens — chunk first

ALWAYS:
  ✅ Use .limit() on all list queries
  ✅ Use .range() for pagination (offset-based for student lists)
  ✅ Use Supabase RPC functions for complex multi-table reads (reduce roundtrips)
  ✅ Run EXPLAIN ANALYZE on any query returning >1000 rows
  ✅ Use realtime only for features that need it (don't enable on all tables)
  ✅ Batch inserts (quiz_answers: insert 180 rows in one call, not 180 calls)
```
