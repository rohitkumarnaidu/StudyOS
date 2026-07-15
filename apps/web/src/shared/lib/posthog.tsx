"use client";

import posthog from "posthog-js";
import { PostHogProvider as PHProvider } from "posthog-js/react";
import { useEffect, useRef, useState } from "react";

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  const initialized = useRef(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
    const host = process.env.NEXT_PUBLIC_POSTHOG_HOST ?? "https://us.i.posthog.com";

    if (!key || initialized.current) return;

    initialized.current = true;
    posthog.init(key, {
      api_host: host,
      person_profiles: "identified_only",
      capture_pageview: true,
      capture_pageleave: true,
      autocapture: true,
      disable_session_recording: true,
    });

    setMounted(true);
  }, []);

  if (!mounted) return children;

  return <PHProvider client={posthog}>{children}</PHProvider>;
}

export { posthog };
