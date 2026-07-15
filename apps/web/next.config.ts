import type { NextConfig } from "next";
import path from "node:path";

import bundleAnalyzer from "@next/bundle-analyzer";

/** Monorepo root (`STUDYOS/` repo) when commands run from `apps/web`. */
const repoRoot = path.resolve(process.cwd(), "..", "..");

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const securityHeaders = [
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload" },
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.sentry.io https://*.posthog.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' blob: data: https://*.posthog.com",
      "connect-src 'self' https://*.sentry.io https://*.posthog.com https://us.i.posthog.com",
      "font-src 'self'",
      "media-src 'self'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
    ].join("; "),
  },
];

const nextConfig: NextConfig = {
  reactCompiler: true,
  output: "standalone",
  outputFileTracingRoot: repoRoot,
  transpilePackages: ["@studyos/shared", "@studyos/config"],
  poweredByHeader: false,
  compress: true,
  experimental: {
    optimizePackageImports: [
      "@tanstack/react-query",
      "sonner",
      "react-hook-form",
      "@hookform/resolvers",
      "lucide-react",
      "recharts",
      "framer-motion",
    ],
  },
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
};

export default withBundleAnalyzer(nextConfig);
