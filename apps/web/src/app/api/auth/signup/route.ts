import { signupFormSchema } from "@/features/auth/schema";
import { internalApiBaseUrl } from "@/server/auth/internal-api-base";
import { applyAuthCookies } from "@/server/auth/auth-cookies";
import { NextResponse } from "next/server";

type ApiTokenResponse = {
  access_token: string;
  refresh_token: string;
  expires_in: number;
};

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const parsed = signupFormSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Validation failed", fields: parsed.error.flatten().fieldErrors },
      { status: 422 },
    );
  }

  const base = internalApiBaseUrl();
  let upstream: Response;
  try {
    upstream = await fetch(`${base}/v1/auth/register`, {
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
        display_name: parsed.data.displayName,
      }),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json({ error: "Auth service unavailable" }, { status: 503 });
  }

  if (!upstream.ok) {
    const errText = await upstream.text().catch(() => "");
    let detail = "Signup failed";
    try {
      const j = JSON.parse(errText) as { detail?: unknown };
      if (typeof j.detail === "string") detail = j.detail;
    } catch {
      /* ignore */
    }
    return NextResponse.json(
      { error: detail },
      { status: upstream.status === 409 ? 409 : upstream.status === 422 ? 422 : 502 },
    );
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
