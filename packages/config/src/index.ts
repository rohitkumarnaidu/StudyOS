import { z } from "zod";

const emptyToUndefined = (val: unknown) =>
  val === "" || val === undefined || val === null ? undefined : val;

/**
 * Browser-safe environment (NEXT_PUBLIC_* only). Server secrets must never live here.
 */
export const publicEnvSchema = z
  .object({
    NEXT_PUBLIC_APP_ENV: z.enum(["development", "staging", "production"]).default("development"),
    NEXT_PUBLIC_API_BASE_URL: z
      .string()
      .url()
      .optional()
      .describe("Optional FastAPI base URL for client-side calls (e.g. http://localhost:8000)"),
    NEXT_PUBLIC_SUPABASE_URL: z.preprocess(
      emptyToUndefined,
      z.string().url().optional().describe("Supabase project URL (https://….supabase.co)"),
    ),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: z.preprocess(
      emptyToUndefined,
      z.string().min(1).optional().describe("Supabase anon (public) key — RLS applies"),
    ),
  })
  .superRefine((data, ctx) => {
    const hasUrl = Boolean(data.NEXT_PUBLIC_SUPABASE_URL);
    const hasKey = Boolean(data.NEXT_PUBLIC_SUPABASE_ANON_KEY);
    if (hasUrl && !hasKey) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "NEXT_PUBLIC_SUPABASE_ANON_KEY is required when NEXT_PUBLIC_SUPABASE_URL is set",
        path: ["NEXT_PUBLIC_SUPABASE_ANON_KEY"],
      });
    }
    if (hasKey && !hasUrl) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "NEXT_PUBLIC_SUPABASE_URL is required when NEXT_PUBLIC_SUPABASE_ANON_KEY is set",
        path: ["NEXT_PUBLIC_SUPABASE_URL"],
      });
    }
  });

export type PublicEnv = z.infer<typeof publicEnvSchema>;

export function isSupabaseConfigured(env: PublicEnv): boolean {
  return Boolean(env.NEXT_PUBLIC_SUPABASE_URL && env.NEXT_PUBLIC_SUPABASE_ANON_KEY);
}

export function getPublicEnv(): PublicEnv {
  const parsed = publicEnvSchema.safeParse({
    NEXT_PUBLIC_APP_ENV: process.env["NEXT_PUBLIC_APP_ENV"],
    NEXT_PUBLIC_API_BASE_URL: process.env["NEXT_PUBLIC_API_BASE_URL"],
    NEXT_PUBLIC_SUPABASE_URL: process.env["NEXT_PUBLIC_SUPABASE_URL"],
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env["NEXT_PUBLIC_SUPABASE_ANON_KEY"],
  });
  if (!parsed.success) {
    const formatted = parsed.error.flatten().fieldErrors;
    throw new Error(`Invalid public environment: ${JSON.stringify(formatted)}`);
  }
  return parsed.data;
}

/**
 * Server-side environment validation (private secrets).
 * Must run at startup to catch misconfigurations early.
 */
export const serverEnvSchema = z.object({
  JWT_SECRET: z.string().min(32, "JWT_SECRET must be at least 32 characters").optional(),
  SUPABASE_SERVICE_ROLE_KEY: z.string().optional(),
  DATABASE_URL: z.string().url().optional(),
  REDIS_URL: z.string().url().optional(),
  SENTRY_AUTH_TOKEN: z.string().optional(),
});

export type ServerEnv = z.infer<typeof serverEnvSchema>;

export function validateServerEnv(): ServerEnv {
  const parsed = serverEnvSchema.safeParse({
    JWT_SECRET: process.env["JWT_SECRET"],
    SUPABASE_SERVICE_ROLE_KEY: process.env["SUPABASE_SERVICE_ROLE_KEY"],
    DATABASE_URL: process.env["DATABASE_URL"],
    REDIS_URL: process.env["REDIS_URL"],
    SENTRY_AUTH_TOKEN: process.env["SENTRY_AUTH_TOKEN"],
  });
  if (!parsed.success) {
    const formatted = parsed.error.flatten().fieldErrors;
    throw new Error(`Invalid server environment: ${JSON.stringify(formatted)}`);
  }
  return parsed.data;
}
