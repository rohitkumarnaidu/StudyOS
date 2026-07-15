/**
 * Web public environment — validated Zod schemas live in `@studyos/config`.
 * Import from `@/shared/config/env` (preferred) or legacy `@/lib/env`.
 */
export { getPublicEnv, isSupabaseConfigured, publicEnvSchema, type PublicEnv } from "@studyos/config";
