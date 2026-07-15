"use client";

import dynamic from "next/dynamic";
import { QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { ThemeProvider } from "next-themes";

import { SessionProvider } from "@/features/auth/session-provider";
import { SupabaseBrowserProvider } from "@/features/auth/supabase-browser-provider";
import { createBrowserQueryClient } from "@/shared/lib/query-client";
import { PostHogProvider } from "@/shared/lib/posthog";
import "@/shared/lib/sentry";

const Toaster = dynamic(() => import("sonner").then((m) => m.Toaster), {
  ssr: false,
  loading: () => null,
});

export function AppProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => createBrowserQueryClient());

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
      storageKey="studyos-theme"
    >
      <PostHogProvider>
        <QueryClientProvider client={queryClient}>
          <SupabaseBrowserProvider>
            <SessionProvider>
              {children}
              <Toaster richColors closeButton position="top-right" visibleToasts={5} />
            </SessionProvider>
          </SupabaseBrowserProvider>
        </QueryClientProvider>
      </PostHogProvider>
    </ThemeProvider>
  );
}
