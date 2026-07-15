import { loginFormSchema } from "@/features/auth/schema";
import { internalApiBaseUrl } from "@/server/auth/internal-api-base";
import { applyAuthCookies } from "@/server/auth/auth-cookies";
import { NextResponse } from "next/server";

type ApiTokenResponse = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
};

// Simple in-memory rate limiter for login attempts
const loginAttempts = new Map<string, { count: number; resetAt: number }>();
const MAX_ATTEMPTS = 5;
const WINDOW_MS = 15 * 60 * 1000; // 15 minutes

function getRateLimitKey(ip: string): string {
  return `login:${ip}`;
}

function checkRateLimit(key: string): { allowed: boolean; retryAfter?: number } {
  const now = Date.now();
  const entry = loginAttempts.get(key);

  if (!entry || now > entry.resetAt) {
    loginAttempts.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return { allowed: true };
  }

  if (entry.count >= MAX_ATTEMPTS) {
    return { allowed: false, retryAfter: Math.ceil((entry.resetAt - now) / 1000) };
  }

  entry.count += 1;
  return { allowed: true };
}

export async function POST(request: Request) {
  // Rate limit by IP
  const ip = request.headers.get("x-forwarded-for") ?? "unknown";
  const rateLimitKey = getRateLimitKey(ip);
  const limit = checkRateLimit(rateLimitKey);

  if (!limit.allowed) {
    return NextResponse.json(
      { error: `Too many login attempts. Try again in ${limit.retryAfter} seconds.` },
      { status: 429, headers: { "Retry-After": String(limit.retryAfter) } },
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }
  const parsed = loginFormSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Validation failed", fields: parsed.error.flatten().fieldErrors },
      { status: 422 },
    );
  }

  const base = internalApiBaseUrl();
  let upstream: Response;
  try {
    upstream = await fetch(`${base}/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(request.headers.get("user-agent")
          ? { "User-Agent": request.headers.get("user-agent")! }
          : {}),
      },
      body: JSON.stringify({
        email: parsed.data.email,
        password: parsed.data.password,
      }),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ error: "Auth service unavailable" }, { status: 503 });
  }

  if (!upstream.ok) {
    const errText = await upstream.text().catch(() => "");
    let detail = "Invalid credentials";
    try {
      const j = JSON.parse(errText) as { detail?: unknown };
      if (typeof j.detail === "string") detail = j.detail;
    } catch {
      /* ignore */
    }
    return NextResponse.json({ error: detail }, { status: upstream.status === 401 ? 401 : 502 });
  }

  const tokens = (await upstream.json()) as Partial<ApiTokenResponse>;
  if (
    typeof tokens.access_token !== "string" ||
    typeof tokens.refresh_token !== "string" ||
    typeof tokens.expires_in !== "number"
  ) {
    return NextResponse.json({ error: "Invalid auth response" }, { status: 502 });
  }

  const res = NextResponse.json({ ok: true });
  applyAuthCookies(res, {
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    expires_in: tokens.expires_in,
  });
  return res;
}
