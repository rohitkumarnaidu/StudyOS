import { internalApiBaseUrl } from "@/server/auth/internal-api-base";
import { NextResponse } from "next/server";

export const runtime = "edge";

export async function POST(request: Request) {
  const base = internalApiBaseUrl();
  const body = await request.json();

  const upstream = await fetch(`${base}/v1/ai/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
    credentials: "include",
  });

  if (!upstream.ok) {
    const errText = await upstream.text().catch(() => "");
    return NextResponse.json({ error: errText || "Stream failed" }, { status: upstream.status });
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
