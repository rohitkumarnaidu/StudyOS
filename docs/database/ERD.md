# StudyOS — entity–relationship diagram (core v1)

The diagram reflects tables created in `supabase/migrations/20250613120002_*` through `20250613120004_*`.  
`auth.users` exists only on **Supabase**; the optional FK is added conditionally in SQL.

```mermaid
erDiagram
  AUTH_USERS ||--o| PROFILES : "id (Supabase only)"
  INSTITUTES ||--o{ PROFILES : "institute_id"
  INSTITUTES ||--o{ INSTITUTE_MEMBERS : "has"
  PROFILES ||--o{ INSTITUTE_MEMBERS : "belongs"
  INSTITUTES ||--o{ BATCHES : "owns"
  BATCHES ||--o{ BATCH_ENROLLMENTS : "enrolls"
  PROFILES ||--o{ BATCH_ENROLLMENTS : "enrolled_as"
  INSTITUTES ||--o{ EXAM_PROFILES : "scopes_optional"
  EXAM_PROFILES ||--o{ SUBJECTS : "contains"
  SUBJECTS ||--o{ CHAPTERS : "contains"
  CHAPTERS ||--o{ TOPICS : "contains"
  TOPICS ||--o{ SUBTOPICS : "contains"
  PROFILES ||--o{ USER_CHAPTER_PROGRESS : "tracks"
  CHAPTERS ||--o{ USER_CHAPTER_PROGRESS : "measured_by"
  PROFILES ||--o{ SUBTOPIC_COMPLETIONS : "completes"
  SUBTOPICS ||--o{ SUBTOPIC_COMPLETIONS : "completed_entity"
  AUTH_USERS {
    uuid id PK
  }

  PROFILES {
    uuid id PK
    text email
    text display_name
    text app_role
    uuid institute_id FK
    timestamptz deleted_at
    bigint row_version
  }

  INSTITUTES {
    uuid id PK
    text slug UK_live
    text name
    jsonb settings
    timestamptz deleted_at
    bigint row_version
  }

  INSTITUTE_MEMBERS {
    uuid id PK
    uuid institute_id FK
    uuid profile_id FK
    text member_role
    timestamptz deleted_at
  }

  BATCHES {
    uuid id PK
    uuid institute_id FK
    text name
    int academic_year
    timestamptz deleted_at
  }

  BATCH_ENROLLMENTS {
    uuid id PK
    uuid batch_id FK
    uuid profile_id FK
    timestamptz enrolled_at
    timestamptz deleted_at
  }

  EXAM_PROFILES {
    uuid id PK
    uuid institute_id FK
    text code
    text title
    timestamptz deleted_at
  }

  SUBJECTS {
    uuid id PK
    uuid exam_profile_id FK
    text name
    int sort_order
  }

  CHAPTERS {
    uuid id PK
    uuid subject_id FK
    text name
    int sort_order
  }

  TOPICS {
    uuid id PK
    uuid chapter_id FK
    text name
    int sort_order
  }

  SUBTOPICS {
    uuid id PK
    uuid topic_id FK
    text name
    int sort_order
  }

  USER_CHAPTER_PROGRESS {
    uuid id PK
    uuid profile_id FK
    uuid chapter_id FK
    real progress_pct
    timestamptz last_studied_at
  }

  SUBTOPIC_COMPLETIONS {
    uuid id PK
    uuid profile_id FK
    uuid subtopic_id FK
    timestamptz completed_at
    text source
  }

  AUDIT_LOG {
    uuid id PK
    timestamptz occurred_at
    text table_name
    uuid record_id
    text action
    jsonb old_row
    jsonb new_row
  }
```

## Legend

- **Soft delete:** `deleted_at IS NULL` rows are “live”; partial unique indexes enforce business keys on live rows only.
- **Optimistic concurrency:** `row_version` increments on `UPDATE` via `studyos_bump_row_version`.
- **Audit:** `audit_log` + `studyos_audit_row` trigger (enabled on `institutes` as the reference pattern).
