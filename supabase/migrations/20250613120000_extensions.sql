-- StudyOS — extensions required by later migrations (idempotent).
-- pgcrypto: legacy UUID helpers; gen_random_uuid() is built-in on PG 13+ but
-- digest/encrypt helpers may still be used by workers.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
