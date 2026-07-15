# StudyOS — Phase 8: Enterprise Feature Implementation Plan

**Date:** 2026-05-18
**Scope:** Take 7 partially-implemented features from basic to enterprise-grade
**Architecture:** Next.js 16 + FastAPI + PostgreSQL + Redis + pgvector

---

## Feature 1: AI Roadmap Engine (Basic → Enterprise)

### Current State
- Basic roadmap generation via AI prompt
- Static weekly plan
- No ML prediction or adaptive learning

### Target State
- ML-based performance prediction
- Dynamic priority scoring
- Auto-revision planning
- Exam countdown optimization
- Intelligent backlog management

### Architecture

```
┌─────────────────────────────────────────────────┐
│                 AI Roadmap Engine                │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js 16)                          │
│  ├── features/roadmap/components/               │
│  │   ├── roadmap-timeline.tsx (Gantt-style)     │
│  │   ├── roadmap-card.tsx                       │
│  │   ├── priority-score-badge.tsx               │
│  │   ├── recovery-plan-viewer.tsx               │
│  │   └── exam-countdown-widget.tsx              │
│  ├── features/roadmap/hooks/                    │
│  │   ├── use-roadmap.ts (React Query)           │
│  │   ├── use-roadmap-regenerate.ts              │
│  │   └── use-priority-scoring.ts                │
│  └── features/roadmap/api.ts                    │
│                                                  │
│  Backend (FastAPI)                               │
│  ├── services/roadmap_generator.py              │
│  ├── services/priority_scorer.py                │
│  ├── services/performance_predictor.py          │
│  ├── services/recovery_planner.py               │
│  ├── services/exam_optimizer.py                 │
│  └── api/v1/routes/roadmap.py                   │
│                                                  │
│  Database                                        │
│  ├── roadmaps (existing)                        │
│  ├── roadmap_items (existing)                   │
│  ├── priority_scores (NEW)                      │
│  ├── performance_predictions (NEW)              │
│  └── recovery_plans (NEW)                       │
└─────────────────────────────────────────────────┘
```

### Database Migrations

```sql
-- 021_roadmap_engine.sql

-- Priority scoring per chapter
CREATE TABLE priority_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL DEFAULT 0,
    weightage_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    time_remaining_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    weak_area_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    exam_proximity_factor DECIMAL(3,2) NOT NULL DEFAULT 1,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, chapter_id)
);

-- ML-based performance predictions
CREATE TABLE performance_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    predicted_score DECIMAL(5,2) NOT NULL,
    confidence_interval_lower DECIMAL(5,2),
    confidence_interval_upper DECIMAL(5,2),
    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    model_version VARCHAR(32) DEFAULT 'v1',
    features_used JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Recovery plans for struggling students
CREATE TABLE recovery_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    roadmap_id UUID REFERENCES roadmaps(id) ON DELETE CASCADE,
    trigger_reason VARCHAR(64) NOT NULL,
    original_completion_date DATE,
    revised_completion_date DATE,
    accelerated_chapters JSONB NOT NULL DEFAULT '[]',
    skipped_chapters JSONB NOT NULL DEFAULT '[]',
    daily_hours_target DECIMAL(3,1) NOT NULL DEFAULT 6,
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_priority_scores_user ON priority_scores(user_id, score DESC);
CREATE INDEX idx_performance_predictions_user ON performance_predictions(user_id, prediction_date DESC);
CREATE INDEX idx_recovery_plans_user ON recovery_plans(user_id, status);
```

### Backend Services

**`services/priority_scorer.py`**
- Computes dynamic priority score per chapter
- Factors: weightage %, time remaining, weak area detection, exam proximity, user progress
- Updates scores daily via cron job
- Returns ranked chapter list for roadmap

**`services/performance_predictor.py`**
- Linear regression model on completion rate + quiz scores
- Predicts final NEET score with confidence interval
- Retrains weekly with new data
- Stores predictions for trend analysis

**`services/recovery_planner.py`**
- Detects when student is behind schedule
- Generates accelerated plan (focus on Tier 1 chapters)
- Suggests chapters to skip (Tier 3, low weightage)
- Updates roadmap with revised timeline

**`services/exam_optimizer.py`**
- Optimizes study plan based on exam date
- Adjusts daily hours target
- Balances subjects based on weak areas
- Generates last-30-days crash plan

### Frontend Components

**`roadmap-timeline.tsx`** — Gantt-style timeline with color-coded priority
**`priority-score-badge.tsx`** — Shows dynamic priority score per chapter
**`recovery-plan-viewer.tsx`** — Displays recovery plan with before/after comparison
**`exam-countdown-widget.tsx`** — Countdown with urgency-based color coding

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/roadmap/generate` | POST | Generate new roadmap with priority scoring |
| `/v1/roadmap/current` | GET | Get current roadmap with priority scores |
| `/v1/roadmap/predict` | GET | Get performance prediction |
| `/v1/roadmap/recovery` | POST | Generate recovery plan |
| `/v1/roadmap/optimize` | POST | Optimize roadmap for exam date |
| `/v1/roadmap/priority-scores` | GET | Get all chapter priority scores |

### Testing Plan
- Unit: priority scorer algorithm (weights, edge cases)
- Unit: performance predictor (regression accuracy)
- Integration: roadmap generation → database → frontend
- E2E: generate roadmap → view timeline → regenerate

---

## Feature 2: AI Mock Test Engine (Quiz → Enterprise)

### Current State
- Basic quiz generation
- Timed mode with countdown
- Simple results display

### Target State
- Adaptive difficulty balancing
- Topic-weight optimization
- AI-generated personalized exams
- Negative marking analytics
- Anti-cheat monitoring
- Distributed test generation

### Architecture

```
┌─────────────────────────────────────────────────┐
│              AI Mock Test Engine                 │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js 16)                          │
│  ├── features/mock-test/components/             │
│  │   ├── mock-test-setup.tsx                    │
│  │   ├── mock-test-player.tsx                   │
│  │   ├── omr-sheet.tsx (180Q grid)              │
│  │   ├── question-navigator.tsx                 │
│  │   ├── mock-test-results.tsx                  │
│  │   ├── difficulty-indicator.tsx               │
│  │   └── anti-cheat-banner.tsx                  │
│  ├── features/mock-test/hooks/                  │
│  │   ├── use-mock-test.ts                       │
│  │   ├── use-adaptive-difficulty.ts             │
│  │   └── use-anti-cheat.ts                      │
│  └── features/mock-test/api.ts                  │
│                                                  │
│  Backend (FastAPI)                               │
│  ├── services/mock_test_generator.py            │
│  ├── services/adaptive_difficulty.py            │
│  ├── services/negative_marking_analyzer.py      │
│  ├── services/anti_cheat_monitor.py             │
│  ├── services/question_bank_manager.py          │
│  └── api/v1/routes/mock_tests.py                │
│                                                  │
│  Database                                        │
│  ├── questions (existing)                       │
│  ├── quiz_sessions (existing)                   │
│  ├── quiz_responses (existing)                  │
│  ├── mock_tests (NEW)                           │
│  ├── mock_test_questions (NEW)                  │
│  ├── anti_cheat_events (NEW)                    │
│  └── difficulty_profiles (NEW)                  │
└─────────────────────────────────────────────────┘
```

### Database Migrations

```sql
-- 022_mock_test_engine.sql

-- Mock test sessions (full 180Q exams)
CREATE TABLE mock_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    test_type VARCHAR(32) NOT NULL DEFAULT 'full_mock',
    difficulty_profile VARCHAR(32) NOT NULL DEFAULT 'adaptive',
    total_questions INT NOT NULL DEFAULT 180,
    duration_minutes INT NOT NULL DEFAULT 180,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    score DECIMAL(5,2),
    negative_marks DECIMAL(5,2) DEFAULT 0,
    time_taken_seconds INT,
    tab_switches INT DEFAULT 0,
    focus_loss_events INT DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Mock test question assignments
CREATE TABLE mock_test_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mock_test_id UUID REFERENCES mock_tests(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    question_order INT NOT NULL,
    difficulty_at_delivery VARCHAR(16),
    time_spent_seconds INT,
    was_flagged BOOLEAN DEFAULT FALSE,
    UNIQUE(mock_test_id, question_order)
);

-- Anti-cheat event tracking
CREATE TABLE anti_cheat_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mock_test_id UUID REFERENCES mock_tests(id) ON DELETE CASCADE,
    event_type VARCHAR(32) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Difficulty profiles for adaptive testing
CREATE TABLE difficulty_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(64) NOT NULL UNIQUE,
    easy_ratio DECIMAL(3,2) NOT NULL DEFAULT 0.3,
    medium_ratio DECIMAL(3,2) NOT NULL DEFAULT 0.5,
    hard_ratio DECIMAL(3,2) NOT NULL DEFAULT 0.2,
    subject_weights JSONB NOT NULL DEFAULT '{"physics": 0.25, "chemistry": 0.25, "biology": 0.5}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_mock_tests_user ON mock_tests(user_id, created_at DESC);
CREATE INDEX idx_mock_test_questions_test ON mock_test_questions(mock_test_id, question_order);
CREATE INDEX idx_anti_cheat_events_test ON anti_cheat_events(mock_test_id, timestamp);
```

### Backend Services

**`services/mock_test_generator.py`**
- Generates 180Q mock tests matching NEET pattern
- Balances subjects (Physics 45, Chemistry 45, Biology 90)
- Respects difficulty profile ratios
- Ensures no duplicate questions across recent tests

**`services/adaptive_difficulty.py`**
- Adjusts question difficulty based on user performance
- Starts at medium, adapts up/down based on accuracy
- Uses item response theory (IRT) for calibration
- Tracks difficulty profile per user over time

**`services/negative_marking_analyzer.py`**
- Analyzes negative marking patterns per user
- Identifies guess-heavy behavior (low accuracy on attempted questions)
- Generates recommendations: "Skip uncertain questions"
- Tracks improvement in negative marking over time

**`services/anti_cheat_monitor.py`**
- Detects tab switches during mock tests
- Tracks focus loss events (window blur)
- Flags suspicious patterns (too-fast answers, perfect scores)
- Generates integrity score per test

### Frontend Components

**`mock-test-setup.tsx`** — Configure test type, duration, difficulty
**`mock-test-player.tsx`** — Full-screen test player with timer
**`omr-sheet.tsx`** — 180Q grid navigation (color-coded by status)
**`question-navigator.tsx`** — Jump to any question, flag for review
**`mock-test-results.tsx`** — Detailed results with section-wise breakdown
**`difficulty-indicator.tsx`** — Shows current difficulty level during test
**`anti-cheat-banner.tsx`** — Warning banner when suspicious activity detected

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/mock-tests/generate` | POST | Generate new mock test |
| `/v1/mock-tests/:id/start` | POST | Start mock test session |
| `/v1/mock-tests/:id/submit` | POST | Submit answers, calculate score |
| `/v1/mock-tests/:id/question/:qid/answer` | POST | Submit single answer |
| `/v1/mock-tests/:id/results` | GET | Get detailed results |
| `/v1/mock-tests/:id/anti-cheat` | GET | Get anti-cheat report |
| `/v1/mock-tests/history` | GET | Get user's mock test history |
| `/v1/mock-tests/adaptive-profile` | GET | Get user's difficulty profile |

### Testing Plan
- Unit: mock test generator (subject balance, difficulty ratios)
- Unit: adaptive difficulty algorithm (IRT calibration)
- Unit: negative marking analyzer (pattern detection)
- Integration: generate → start → answer → submit → results
- E2E: full 180Q mock test flow with OMR navigation

---

## Feature 3: Smart Revision Engine (Basic → Enterprise)

### Current State
- Spaced repetition logic in skills-claude (Claude prompts only)
- No actual implementation in codebase
- No tracking of revision intervals

### Target State
- SM-2 spaced repetition algorithm
- Dynamic revision intervals
- AI-generated revision packs
- Memory retention tracking
- Forgetting curve optimization
- Active recall sessions

### Architecture

```
┌─────────────────────────────────────────────────┐
│             Smart Revision Engine                │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js 16)                          │
│  ├── features/revision/components/              │
│  │   ├── revision-dashboard.tsx                 │
│  │   ├── revision-card.tsx (flashcard-style)    │
│  │   ├── retention-graph.tsx                    │
│  │   ├── forgetting-curve.tsx                   │
│  │   ├── revision-pack-viewer.tsx               │
│  │   └── active-recall-session.tsx              │
│  ├── features/revision/hooks/                   │
│  │   ├── use-revision-queue.ts                  │
│  │   ├── use-spaced-repetition.ts               │
│  │   └── use-retention-tracking.ts              │
│  └── features/revision/api.ts                   │
│                                                  │
│  Backend (FastAPI)                               │
│  ├── services/spaced_repetition.py (SM-2)       │
│  ├── services/retention_tracker.py              │
│  ├── services/revision_pack_generator.py        │
│  ├── services/forgetting_curve.py               │
│  ├── services/active_recall.py                  │
│  └── api/v1/routes/revision.py                  │
│                                                  │
│  Database                                        │
│  ├── revision_items (NEW)                       │
│  ├── revision_sessions (NEW)                    │
│  ├── retention_records (NEW)                    │
│  └── revision_packs (NEW)                       │
└─────────────────────────────────────────────────┘
```

### Database Migrations

```sql
-- 023_smart_revision.sql

-- Individual revision items (subtopics, flashcards, notes)
CREATE TABLE revision_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    item_type VARCHAR(32) NOT NULL, -- 'subtopic', 'flashcard', 'note', 'formula'
    item_id UUID NOT NULL, -- FK to subtopics, flashcards, etc.
    ease_factor DECIMAL(3,2) NOT NULL DEFAULT 2.5,
    interval_days INT NOT NULL DEFAULT 1,
    repetitions INT NOT NULL DEFAULT 0,
    next_review_date DATE NOT NULL,
    last_review_date DATE,
    last_quality_score INT, -- 0-5 SM-2 quality rating
    retention_probability DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, item_type, item_id)
);

-- Revision session tracking
CREATE TABLE revision_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    session_type VARCHAR(32) NOT NULL DEFAULT 'spaced_repetition',
    items_reviewed INT NOT NULL DEFAULT 0,
    items_retained INT NOT NULL DEFAULT 0,
    retention_rate DECIMAL(3,2),
    duration_seconds INT,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Retention probability records (for forgetting curve)
CREATE TABLE retention_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    revision_item_id UUID REFERENCES revision_items(id) ON DELETE CASCADE,
    review_date DATE NOT NULL,
    quality_score INT NOT NULL, -- 0-5
    predicted_retention DECIMAL(3,2),
    actual_retention BOOLEAN, -- Did they remember?
    days_since_last_review INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Pre-generated revision packs
CREATE TABLE revision_packs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    name VARCHAR(128) NOT NULL,
    pack_type VARCHAR(32) NOT NULL, -- 'weak_areas', 'upcoming_review', 'exam_prep'
    items JSONB NOT NULL DEFAULT '[]',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_completed BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_revision_items_due ON revision_items(user_id, next_review_date) WHERE next_review_date <= CURRENT_DATE;
CREATE INDEX idx_revision_sessions_user ON revision_sessions(user_id, started_at DESC);
CREATE INDEX idx_retention_records_item ON retention_records(revision_item_id, review_date DESC);
CREATE INDEX idx_revision_packs_user ON revision_packs(user_id, generated_at DESC);
```

### Backend Services

**`services/spaced_repetition.py`** — SM-2 algorithm implementation
- Calculates next review date based on quality score
- Adjusts ease factor based on performance
- Handles interval escalation (1 → 3 → 7 → 16 → 35 → ...)
- Returns daily revision queue sorted by priority

**`services/retention_tracker.py`**
- Tracks retention probability per item
- Computes forgetting curve per user
- Identifies items at risk of being forgotten
- Generates retention analytics

**`services/revision_pack_generator.py`**
- Generates revision packs based on:
  - Upcoming reviews (due today/tomorrow)
  - Weak areas (low quiz scores)
  - Exam prep (high-weightage chapters)
- AI-curated pack descriptions
- Time-estimated pack duration

**`services/forgetting_curve.py`**
- Implements Ebbinghaus forgetting curve model
- Predicts retention probability over time
- Adjusts intervals based on actual retention data
- Personalizes curve per user

### Frontend Components

**`revision-dashboard.tsx`** — Overview: due items, retention rate, streak
**`revision-card.tsx`** — Flashcard-style review with quality rating (0-5)
**`retention-graph.tsx`** — Line chart showing retention over time
**`forgetting-curve.tsx`** — Visual forgetting curve with predicted vs actual
**`revision-pack-viewer.tsx`** — Browse and start revision packs
**`active-recall-session.tsx`** — Guided active recall with hints

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/revision/queue` | GET | Get today's revision queue |
| `/v1/revision/review` | POST | Submit review (quality score) |
| `/v1/revision/retention` | GET | Get retention analytics |
| `/v1/revision/packs` | GET | List available revision packs |
| `/v1/revision/packs/generate` | POST | Generate new revision pack |
| `/v1/revision/forgetting-curve` | GET | Get forgetting curve data |
| `/v1/revision/stats` | GET | Get revision statistics |

### Testing Plan
- Unit: SM-2 algorithm (interval calculation, ease factor adjustment)
- Unit: forgetting curve model (retention prediction)
- Integration: review item → update interval → queue changes
- E2E: start revision session → review 10 items → view retention graph

---

## Feature 4: Predictive Analytics (Basic → Enterprise)

### Current State
- Basic dashboard with PostHog event tracking
- Simple progress charts
- No ML-based predictions

### Target State
- Rank prediction model
- Score prediction with confidence intervals
- Burnout prediction
- Learning velocity tracking
- Revision efficiency tracking
- ML analytics pipeline

### Architecture

```
┌─────────────────────────────────────────────────┐
│            Predictive Analytics                  │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js 16)                          │
│  ├── features/predictions/components/           │
│  │   ├── rank-predictor.tsx                     │
│  │   ├── score-predictor.tsx                    │
│  │   ├── burnout-warning.tsx                    │
│  │   ├── learning-velocity-chart.tsx            │
│  │   ├── revision-efficiency-chart.tsx          │
│  │   └── prediction-confidence-band.tsx         │
│  ├── features/predictions/hooks/                │
│  │   ├── use-predictions.ts                     │
│  │   └── use-burnout-alert.ts                   │
│  └── features/predictions/api.ts                │
│                                                  │
│  Backend (FastAPI)                               │
│  ├── services/rank_predictor.py                 │
│  ├── services/score_predictor.py                │
│  ├── services/burnout_detector.py               │
│  ├── services/learning_velocity.py              │
│  ├── services/revision_efficiency.py            │
│  └── api/v1/routes/predictions.py               │
│                                                  │
│  Database                                        │
│  ├── predictions (NEW)                          │
│  ├── burnout_alerts (NEW)                       │
│  ├── velocity_records (NEW)                     │
│  └── efficiency_records (NEW)                   │
└─────────────────────────────────────────────────┘
```

### Database Migrations

```sql
-- 024_predictive_analytics.sql

-- Prediction records
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    prediction_type VARCHAR(32) NOT NULL, -- 'score', 'rank', 'completion_date'
    predicted_value DECIMAL(10,2) NOT NULL,
    confidence_lower DECIMAL(10,2),
    confidence_upper DECIMAL(10,2),
    model_version VARCHAR(32) DEFAULT 'v1',
    features_snapshot JSONB NOT NULL DEFAULT '{}',
    prediction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Burnout detection alerts
CREATE TABLE burnout_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    alert_level VARCHAR(16) NOT NULL, -- 'warning', 'critical'
    trigger_factors JSONB NOT NULL DEFAULT '{}',
    recommended_actions JSONB NOT NULL DEFAULT '[]',
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Learning velocity tracking
CREATE TABLE velocity_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    chapters_completed INT NOT NULL DEFAULT 0,
    subtopics_completed INT NOT NULL DEFAULT 0,
    study_minutes INT NOT NULL DEFAULT 0,
    velocity_score DECIMAL(5,2), -- chapters per week normalized
    trend VARCHAR(16), -- 'increasing', 'stable', 'decreasing'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, week_start)
);

-- Revision efficiency tracking
CREATE TABLE efficiency_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    revision_date DATE NOT NULL DEFAULT CURRENT_DATE,
    items_reviewed INT NOT NULL DEFAULT 0,
    items_retained INT NOT NULL DEFAULT 0,
    efficiency_score DECIMAL(5,2), -- retention rate * speed factor
    time_per_item_seconds DECIMAL(5,1),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_predictions_user ON predictions(user_id, prediction_date DESC);
CREATE INDEX idx_burnout_alerts_user ON burnout_alerts(user_id, created_at DESC) WHERE acknowledged = FALSE;
CREATE INDEX idx_velocity_records_user ON velocity_records(user_id, week_start DESC);
CREATE INDEX idx_efficiency_records_user ON efficiency_records(user_id, revision_date DESC);
```

### Backend Services

**`services/score_predictor.py`**
- Multiple linear regression: completion_rate, quiz_avg, study_hours, streak
- Returns predicted score with 95% confidence interval
- Updates prediction weekly
- Tracks prediction accuracy over time

**`services/rank_predictor.py`**
- Maps predicted score to NEET rank using historical cut-off data
- Category-wise predictions (General, OBC, SC, ST)
- State-wise rank predictions
- Updates when new cut-off data available

**`services/burnout_detector.py`**
- Monitors: declining study hours, increasing skip rate, negative sentiment in chat
- Triggers warning at 7-day decline, critical at 14-day decline
- Generates recommended actions (rest day, lighter schedule, motivation boost)
- Stores alerts for tracking

**`services/learning_velocity.py`**
- Computes weekly velocity (chapters completed per week)
- Detects trend (increasing/stable/decreasing)
- Compares against peer benchmarks (anonymized)
- Generates velocity improvement recommendations

**`services/revision_efficiency.py`**
- Computes efficiency score: retention_rate × speed_factor
- Tracks time per revision item
- Identifies inefficient revision patterns
- Recommends optimal revision session length

### Frontend Components

**`rank-predictor.tsx`** — Predicted rank with category/state filters
**`score-predictor.tsx`** — Score prediction with confidence band chart
**`burnout-warning.tsx`** — Alert banner with recommended actions
**`learning-velocity-chart.tsx`** — Weekly velocity trend line
**`revision-efficiency-chart.tsx`** — Efficiency score over time
**`prediction-confidence-band.tsx`** — Reusable confidence interval visualization

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/predictions/score` | GET | Get score prediction |
| `/v1/predictions/rank` | GET | Get rank prediction |
| `/v1/predictions/burnout` | GET | Check burnout risk |
| `/v1/predictions/velocity` | GET | Get learning velocity data |
| `/v1/predictions/efficiency` | GET | Get revision efficiency data |
| `/v1/predictions/acknowledge-burnout` | POST | Acknowledge burnout alert |

### Testing Plan
- Unit: score predictor (regression accuracy, confidence intervals)
- Unit: burnout detector (threshold detection, alert generation)
- Unit: learning velocity (trend detection, normalization)
- Integration: generate prediction → store → retrieve → display
- E2E: view predictions dashboard → acknowledge burnout alert

---

## Feature 5: AI Mistake Intelligence (Basic → Enterprise)

### Current State
- Basic error tracking in quiz responses
- No conceptual gap analysis
- No pattern detection

### Target State
- Repeated mistake tracking
- Conceptual gap identification
- Future mistake prediction
- Targeted recovery plans
- Concept weakness heatmaps
- Knowledge graph integration
- Semantic error clustering
- Cognitive pattern detection

### Architecture

```
┌─────────────────────────────────────────────────┐
│          AI Mistake Intelligence                 │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js 16)                          │
│  ├── features/mistakes/components/              │
│  │   ├── mistake-dashboard.tsx                  │
│  │   ├── mistake-log.tsx                        │
│  │   ├── concept-gap-viewer.tsx                 │
│  │   ├── weakness-heatmap.tsx                   │
│  │   ├── recovery-plan-viewer.tsx               │
│  │   └── pattern-insights.tsx                   │
│  ├── features/mistakes/hooks/                   │
│  │   ├── use-mistake-analysis.ts                │
│  │   └── use-concept-gaps.ts                    │
│  └── features/mistakes/api.ts                   │
│                                                  │
│  Backend (FastAPI)                               │
│  ├── services/mistake_tracker.py                │
│  ├── services/concept_gap_analyzer.py           │
│  ├── services/mistake_predictor.py              │
│  ├── services/semantic_clusterer.py             │
│  ├── services/cognitive_pattern_detector.py     │
│  └── api/v1/routes/mistakes.py                  │
│                                                  │
│  Database                                        │
│  ├── mistake_logs (NEW)                         │
│  ├── concept_gaps (NEW)                         │
│  ├── mistake_patterns (NEW)                     │
│  └── recovery_recommendations (NEW)             │
└─────────────────────────────────────────────────┘
```

### Database Migrations

```sql
-- 025_mistake_intelligence.sql

-- Detailed mistake logging
CREATE TABLE mistake_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id),
    chapter_id UUID REFERENCES chapters(id),
    topic_id UUID REFERENCES topics(id),
    subtopic_id UUID REFERENCES subtopics(id),
    selected_option INT,
    correct_option INT,
    mistake_type VARCHAR(32), -- 'conceptual', 'calculation', 'misread', 'guess'
    concept_tags JSONB NOT NULL DEFAULT '[]',
    time_spent_seconds INT,
    confidence_level INT, -- 1-5 self-reported
    source VARCHAR(32), -- 'quiz', 'mock_test', 'practice'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Identified concept gaps
CREATE TABLE concept_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    concept_name VARCHAR(128) NOT NULL,
    chapter_id UUID REFERENCES chapters(id),
    gap_severity VARCHAR(16) NOT NULL, -- 'mild', 'moderate', 'severe'
    mistake_count INT NOT NULL DEFAULT 1,
    first_detected TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_detected TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    UNIQUE(user_id, concept_name)
);

-- Mistake pattern detection
CREATE TABLE mistake_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    pattern_type VARCHAR(32) NOT NULL, -- 'repeated_concept', 'time_pressure', 'subject_bias'
    pattern_data JSONB NOT NULL DEFAULT '{}',
    confidence DECIMAL(3,2),
    detected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Recovery recommendations
CREATE TABLE recovery_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    concept_gap_id UUID REFERENCES concept_gaps(id),
    recommendation_type VARCHAR(32) NOT NULL, -- 'revise_chapter', 'practice_quiz', 'ai_tutor'
    recommendation_data JSONB NOT NULL DEFAULT '{}',
    priority INT NOT NULL DEFAULT 5,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_mistake_logs_user ON mistake_logs(user_id, created_at DESC);
CREATE INDEX idx_mistake_logs_chapter ON mistake_logs(chapter_id, created_at DESC);
CREATE INDEX idx_concept_gaps_user ON concept_gaps(user_id, gap_severity, is_resolved);
CREATE INDEX idx_mistake_patterns_user ON mistake_patterns(user_id, is_active, detected_at DESC);
```

### Backend Services

**`services/mistake_tracker.py`**
- Logs every mistake with detailed metadata
- Categorizes mistake type (conceptual, calculation, misread, guess)
- Tracks repeated mistakes per concept
- Generates mistake frequency reports

**`services/concept_gap_analyzer.py`**
- Identifies conceptual gaps from mistake patterns
- Maps mistakes to specific concepts/topics
- Calculates gap severity based on frequency and recency
- Tracks gap resolution over time

**`services/mistake_predictor.py`**
- Predicts future mistakes based on historical patterns
- Identifies at-risk concepts before next quiz
- Generates preemptive study recommendations
- Uses collaborative filtering (similar students' mistakes)

**`services/semantic_clusterer.py`**
- Clusters mistakes by semantic similarity
- Identifies related concept gaps
- Groups mistakes that share underlying misconceptions
- Uses pgvector embeddings for semantic matching

**`services/cognitive_pattern_detector.py`**
- Detects cognitive patterns: time pressure errors, subject bias, confidence mismatch
- Identifies when student is guessing vs. genuinely confused
- Tracks improvement in mistake patterns over time
- Generates personalized learning style insights

### Frontend Components

**`mistake-dashboard.tsx`** — Overview: total mistakes, trends, top gaps
**`mistake-log.tsx`** — Detailed mistake history with filters
**`concept-gap-viewer.tsx`** — Visual concept gap map with severity
**`weakness-heatmap.tsx`** — Chapter/topic heatmap colored by mistake frequency
**`recovery-plan-viewer.tsx`** — AI-generated recovery recommendations
**`pattern-insights.tsx`** — Cognitive pattern insights and trends

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/mistakes/log` | POST | Log a new mistake |
| `/v1/mistakes/history` | GET | Get mistake history |
| `/v1/mistakes/concept-gaps` | GET | Get identified concept gaps |
| `/v1/mistakes/predictions` | GET | Get predicted future mistakes |
| `/v1/mistakes/patterns` | GET | Get detected cognitive patterns |
| `/v1/mistakes/recovery` | GET | Get recovery recommendations |
| `/v1/mistakes/heatmap` | GET | Get weakness heatmap data |
| `/v1/mistakes/resolve-gap` | POST | Mark concept gap as resolved |

### Testing Plan
- Unit: mistake categorization algorithm
- Unit: concept gap severity calculation
- Unit: semantic clustering (embedding similarity)
- Integration: log mistake → detect gap → generate recommendation
- E2E: view mistake dashboard → review concept gaps → start recovery plan

---

## Feature 6: Knowledge Graph Engine (Conceptual → Enterprise)

### Current State
- Conceptual knowledge in skills files
- No actual graph database or relationship mapping
- No prerequisite tracking

### Target State
- Concept relationship mapping
- Prerequisite dependency graph
- Learning dependency graph
- Interconnected revision
- AI concept traversal
- Graph database integration
- Semantic relationship engine

### Architecture

```
┌─────────────────────────────────────────────────┐
│            Knowledge Graph Engine                │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js 16)                          │
│  ├── features/knowledge-graph/components/       │
│  │   ├── concept-map.tsx (interactive graph)    │
│  │   ├── prerequisite-chain.tsx                 │
│  │   ├── concept-detail-panel.tsx               │
│  │   ├── learning-path-viewer.tsx               │
│  │   └── relationship-explorer.tsx              │
│  ├── features/knowledge-graph/hooks/            │
│  │   ├── use-concept-graph.ts                   │
│  │   └── use-learning-path.ts                   │
│  └── features/knowledge-graph/api.ts            │
│                                                  │
│  Backend (FastAPI)                               │
│  ├── services/graph_builder.py                  │
│  ├── services/prerequisite_resolver.py          │
│  ├── services/concept_traverser.py              │
│  ├── services/relationship_engine.py            │
│  ├── services/learning_path_generator.py        │
│  └── api/v1/routes/knowledge_graph.py           │
│                                                  │
│  Database                                        │
│  ├── concepts (NEW)                             │
│  ├── concept_relationships (NEW)                │
│  ├── prerequisites (NEW)                        │
│  └── learning_paths (NEW)                       │
└─────────────────────────────────────────────────┘
```

### Database Migrations

```sql
-- 026_knowledge_graph.sql

-- Concept nodes
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    description TEXT,
    subject_id UUID REFERENCES subjects(id),
    chapter_id UUID REFERENCES chapters(id),
    topic_id UUID REFERENCES topics(id),
    subtopic_id UUID REFERENCES subtopics(id),
    concept_type VARCHAR(32) NOT NULL, -- 'definition', 'formula', 'process', 'law', 'theory'
    difficulty_level VARCHAR(16) DEFAULT 'medium',
    embedding_id UUID, -- Reference to pgvector embedding
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(name, subject_id)
);

-- Concept relationships (edges)
CREATE TABLE concept_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    target_concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    relationship_type VARCHAR(32) NOT NULL, -- 'prerequisite', 'related', 'extends', 'contrasts', 'example_of'
    strength DECIMAL(3,2) NOT NULL DEFAULT 1.0,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(source_concept_id, target_concept_id, relationship_type),
    CHECK (source_concept_id != target_concept_id)
);

-- Prerequisite chains
CREATE TABLE prerequisites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    prerequisite_concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    priority INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(concept_id, prerequisite_concept_id)
);

-- Generated learning paths through the graph
CREATE TABLE learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(user_id) ON DELETE CASCADE,
    target_concept_id UUID REFERENCES concepts(id),
    path_nodes JSONB NOT NULL DEFAULT '[]', -- Ordered list of concept IDs
    total_concepts INT NOT NULL,
    estimated_hours DECIMAL(4,1),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_completed BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_concepts_subject ON concepts(subject_id, chapter_id);
CREATE INDEX idx_concept_relationships_source ON concept_relationships(source_concept_id, relationship_type);
CREATE INDEX idx_concept_relationships_target ON concept_relationships(target_concept_id);
CREATE INDEX idx_prerequisites_concept ON prerequisites(concept_id);
CREATE INDEX idx_learning_paths_user ON learning_paths(user_id, generated_at DESC);
```

### Backend Services

**`services/graph_builder.py`**
- Builds knowledge graph from syllabus data
- Creates concept nodes from chapters/topics/subtopics
- Establishes relationships (prerequisite, related, extends, contrasts)
- Seeds initial graph from NEET curriculum structure

**`services/prerequisite_resolver.py`**
- Resolves prerequisite chains using topological sort
- Identifies missing prerequisites before studying a concept
- Generates prerequisite learning order
- Detects circular dependencies

**`services/concept_traverser.py`**
- Traverses graph from any starting concept
- Finds all related concepts within N hops
- Identifies concept clusters (densely connected groups)
- Supports BFS, DFS, and shortest-path traversal

**`services/relationship_engine.py`**
- Computes relationship strength between concepts
- Uses embedding similarity for semantic relationships
- Updates relationships based on student performance data
- Identifies missing relationships (concepts often studied together)

**`services/learning_path_generator.py`**
- Generates optimal learning path through the graph
- Respects prerequisite ordering
- Adapts path based on student's current knowledge
- Estimates time to complete path

### Frontend Components

**`concept-map.tsx`** — Interactive force-directed graph visualization (@xyflow/react)
**`prerequisite-chain.tsx`** — Linear prerequisite chain viewer
**`concept-detail-panel.tsx`** — Concept details with relationships
**`learning-path-viewer.tsx`** — Step-by-step learning path through graph
**`relationship-explorer.tsx`** — Browse relationships between concepts

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/knowledge-graph/concepts` | GET | List all concepts |
| `/v1/knowledge-graph/concepts/:id` | GET | Get concept details + relationships |
| `/v1/knowledge-graph/concepts/:id/prerequisites` | GET | Get prerequisite chain |
| `/v1/knowledge-graph/concepts/:id/related` | GET | Get related concepts |
| `/v1/knowledge-graph/traverse` | POST | Traverse graph from concept |
| `/v1/knowledge-graph/learning-path` | POST | Generate learning path |
| `/v1/knowledge-graph/clusters` | GET | Get concept clusters |

### Testing Plan
- Unit: topological sort (prerequisite resolution)
- Unit: graph traversal (BFS, DFS, shortest path)
- Unit: relationship strength computation
- Integration: build graph → traverse → generate path
- E2E: view concept map → explore prerequisites → generate learning path

---

## Feature 7: Enterprise Observability (Basic → Enterprise)

### Current State
- Sentry for error tracking
- PostHog for product analytics
- structlog for structured logging
- Basic audit logging middleware

### Target State
- Full OpenTelemetry integration
- Distributed tracing across web + API
- SLO dashboards
- Cost tracking (AI tokens, infrastructure)
- Reliability dashboards
- Operational analytics
- Multi-region deployment support

### Architecture

```
┌─────────────────────────────────────────────────┐
│         Enterprise Observability                 │
├─────────────────────────────────────────────────┤
│  Frontend (Next.js 16)                          │
│  ├── features/observability/components/         │
│  │   ├── slo-dashboard.tsx                      │
│  │   ├── cost-tracker.tsx                       │
│  │   ├── reliability-meter.tsx                  │
│  │   ├── trace-viewer.tsx                       │
│  │   └── operational-alerts.tsx                 │
│  ├── features/observability/hooks/              │
│  │   └── use-telemetry.ts                       │
│  └── features/observability/api.ts              │
│                                                  │
│  Backend (FastAPI)                               │
│  ├── middleware/otel_middleware.py              │
│  ├── services/cost_tracker.py                   │
│  ├── services/slo_monitor.py                    │
│  ├── services/reliability_monitor.py            │
│  ├── services/alert_manager.py                  │
│  └── api/v1/routes/observability.py             │
│                                                  │
│  Infrastructure                                  │
│  ├── OpenTelemetry Collector                    │
│  ├── Prometheus (metrics)                       │
│  ├── Grafana (dashboards)                       │
│  ├── Jaeger (distributed tracing)               │
│  └── AlertManager (notifications)               │
└─────────────────────────────────────────────────┘
```

### Database Migrations

```sql
-- 027_observability.sql

-- Cost tracking for AI tokens and infrastructure
CREATE TABLE cost_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    record_type VARCHAR(32) NOT NULL, -- 'ai_tokens', 'database', 'storage', 'bandwidth'
    provider VARCHAR(64), -- 'openai', 'anthropic', 'supabase', 'vercel'
    amount DECIMAL(10,4) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    user_id UUID REFERENCES profiles(user_id),
    metadata JSONB NOT NULL DEFAULT '{}',
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- SLO (Service Level Objective) records
CREATE TABLE slo_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slo_name VARCHAR(64) NOT NULL,
    target_percentage DECIMAL(5,2) NOT NULL, -- e.g., 99.9
    actual_percentage DECIMAL(5,2),
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    error_budget_remaining DECIMAL(5,2),
    is_breached BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Reliability metrics
CREATE TABLE reliability_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(64) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_unit VARCHAR(16), -- 'ms', '%', 'count'
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Operational alerts
CREATE TABLE operational_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(32) NOT NULL, -- 'slo_breach', 'cost_spike', 'error_rate', 'latency'
    severity VARCHAR(16) NOT NULL, -- 'info', 'warning', 'critical'
    message TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_cost_records_type ON cost_records(record_type, recorded_at DESC);
CREATE INDEX idx_cost_records_user ON cost_records(user_id, recorded_at DESC);
CREATE INDEX idx_slo_records_name ON slo_records(slo_name, window_start DESC);
CREATE INDEX idx_reliability_metrics_name ON reliability_metrics(metric_name, recorded_at DESC);
CREATE INDEX idx_operational_alerts_type ON operational_alerts(alert_type, is_resolved, created_at DESC);
```

### Backend Services

**`middleware/otel_middleware.py`**
- OpenTelemetry instrumentation for all FastAPI requests
- Distributed tracing with trace context propagation
- Custom spans for AI calls, database queries, cache hits
- Exports to Jaeger/OTLP collector

**`services/cost_tracker.py`**
- Tracks AI token costs per user per request
- Monitors database query costs
- Tracks storage and bandwidth usage
- Generates cost reports and alerts on spikes

**`services/slo_monitor.py`**
- Defines SLOs: API latency p95 < 200ms, error rate < 0.1%, uptime > 99.9%
- Computes actual performance against targets
- Tracks error budget consumption
- Alerts when SLO is at risk

**`services/reliability_monitor.py`**
- Monitors system reliability metrics
- Tracks MTTR (mean time to recovery)
- Monitors dependency health (database, Redis, AI providers)
- Generates reliability score

**`services/alert_manager.py`**
- Manages operational alerts
- Routes alerts to appropriate channels (Slack, email)
- Tracks alert resolution time
- Prevents alert fatigue (deduplication, grouping)

### Frontend Components

**`slo-dashboard.tsx`** — SLO compliance dashboard with error budget
**`cost-tracker.tsx`** — AI token cost tracking with per-user breakdown
**`reliability-meter.tsx`** — System reliability score and trends
**`trace-viewer.tsx`** — Distributed trace visualization
**`operational-alerts.tsx` — Active alerts with resolution status

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/observability/costs` | GET | Get cost breakdown |
| `/v1/observability/slos` | GET | Get SLO status |
| `/v1/observability/reliability` | GET | Get reliability metrics |
| `/v1/observability/alerts` | GET | Get active alerts |
| `/v1/observability/alerts/:id/resolve` | POST | Resolve an alert |
| `/v1/observability/traces` | GET | Get recent traces |

### Testing Plan
- Unit: cost calculation (token pricing, aggregation)
- Unit: SLO computation (error budget, breach detection)
- Unit: alert routing (severity, deduplication)
- Integration: generate trace → export → retrieve
- E2E: view observability dashboard → resolve alert

---

## Implementation Priority & Timeline

### Sprint 1-2: Foundation (Weeks 1-4)
| Feature | Deliverables |
|---------|-------------|
| AI Roadmap Engine | Priority scorer, performance predictor, database migration |
| Smart Revision Engine | SM-2 algorithm, revision queue, database migration |

### Sprint 3-4: Analytics (Weeks 5-8)
| Feature | Deliverables |
|---------|-------------|
| Predictive Analytics | Score/rank predictor, burnout detector, velocity tracking |
| AI Mistake Intelligence | Mistake tracker, concept gap analyzer, semantic clusterer |

### Sprint 5-6: Advanced (Weeks 9-12)
| Feature | Deliverables |
|---------|-------------|
| AI Mock Test Engine | Mock test generator, adaptive difficulty, anti-cheat |
| Knowledge Graph Engine | Graph builder, prerequisite resolver, concept map UI |

### Sprint 7-8: Observability (Weeks 13-16)
| Feature | Deliverables |
|---------|-------------|
| Enterprise Observability | OpenTelemetry, cost tracking, SLO monitoring, alerts |

---

## Cross-Cutting Concerns

### Shared Infrastructure
- **Redis**: Used by all features for caching (priority scores, revision queues, prediction cache)
- **pgvector**: Used by mistake intelligence (semantic clustering) and knowledge graph (concept embeddings)
- **PostHog**: Extended with custom events for all new features
- **Sentry**: Extended with custom breadcrumbs for all new features

### Testing Strategy
- **Unit tests**: 80%+ coverage for all new services
- **Integration tests**: All API endpoints tested with test database
- **E2E tests**: Critical user flows for each feature
- **Load tests**: k6 scripts for high-traffic endpoints (mock tests, revision queue)

### Monitoring
- All new endpoints instrumented with OpenTelemetry
- Custom PostHog events for feature adoption tracking
- Sentry error boundaries on all new components
- SLO targets defined for each feature

---

*Phase 8 Implementation Plan — StudyOS Enterprise Features | May 2026*
