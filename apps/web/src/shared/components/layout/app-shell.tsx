"use client";

import type { ReactNode } from "react";
import { AppSidebar } from "@/features/dashboard/components/app-sidebar";
import { AppHeader } from "@/features/dashboard/components/app-header";
import { mainNavItems, secondaryNavItems } from "@/features/dashboard/config/navigation";
import { TooltipProvider } from "@/shared/components/ui/tooltip";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <TooltipProvider>
      <div className="flex min-h-screen">
        <AppSidebar items={mainNavItems} secondaryItems={secondaryNavItems} />
        <div className="flex min-h-screen flex-1 flex-col">
          <AppHeader />
          <main className="flex-1 p-4 sm:p-6">{children}</main>
        </div>
      </div>
    </TooltipProvider>
  );
}
