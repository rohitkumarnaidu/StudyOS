import { NextResponse } from "next/server";

export const runtime = "edge";

export async function GET() {
  const manifest = {
    name: "StudyOS",
    short_name: "StudyOS",
    description: "AI-first study operating system",
    start_url: "/dashboard",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#0a0a0a",
    orientation: "portrait-primary",
    scope: "/",
    lang: "en",
    categories: ["education", "productivity"],
    icons: [
      { src: "/icons/icon-192.svg", sizes: "192x192", type: "image/svg+xml", purpose: "any maskable" },
      { src: "/icons/icon-512.svg", sizes: "512x512", type: "image/svg+xml", purpose: "any maskable" },
    ],
    shortcuts: [
      {
        name: "Dashboard",
        short_name: "Dashboard",
        description: "Open your study dashboard",
        url: "/dashboard",
        icons: [{ src: "/icons/icon-192.svg", sizes: "192x192" }],
      },
      {
        name: "Revision",
        short_name: "Revision",
        description: "Start a revision session",
        url: "/revision",
        icons: [{ src: "/icons/icon-192.svg", sizes: "192x192" }],
      },
    ],
  };

  return NextResponse.json(manifest, {
    headers: {
      "Cache-Control": "public, max-age=3600",
    },
  });
}
