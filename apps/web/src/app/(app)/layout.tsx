"use client";

import type { ReactNode } from "react";
import { AppSessionGate } from "@/features/auth/components/app-session-gate";
import { AppShell } from "@/shared/components/layout/app-shell";
import { OfflineBanner } from "@/features/offline/components/offline-banner";
import { PWAInstallPrompt } from "@/features/offline/components/pwa-install-prompt";

export default function AppGroupLayout({ children }: { children: ReactNode }) {
  return (
    <AppShell>
      <OfflineBanner />
      <PWAInstallPrompt />
      <AppSessionGate>{children}</AppSessionGate>
    </AppShell>
  );
}
