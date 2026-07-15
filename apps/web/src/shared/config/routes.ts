/**
 * Canonical paths — used by middleware, auth redirects, and links.
 * Keep this module free of React imports so it stays Edge-safe.
 */
export const ROUTES = {
  home: "/",
  login: "/login",
  dashboard: "/dashboard",
  /** Supabase OAuth PKCE return (Google, etc.) — must match Supabase redirect allow-list. */
  authCallback: "/auth/callback",
  syllabus: "/syllabus",
  quiz: "/quiz",
  notes: "/notes",
  revision: "/revision",
  chat: "/chat",
  progress: "/progress",
  analytics: "/analytics",
  roadmap: "/roadmap",
  mistakeIntelligence: "/mistake-intelligence",
  achievements: "/achievements",
  settings: "/settings",
} as const;

/** Path prefixes that require an authenticated session (middleware + client gate). */
export const PROTECTED_ROUTE_PREFIXES: readonly string[] = [ROUTES.dashboard] as const;

export const DEFAULT_LOGIN_REDIRECT = ROUTES.dashboard;
