"use client";

import { usePathname } from "next/navigation";
import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { Button } from "@/shared/components/ui/button";
import { Bell, LogOut, Settings, User } from "lucide-react";
import { useSession } from "@/features/auth/session-provider";
import { notifyFromUnknown } from "@/shared/lib";
import { useEffect, useState } from "react";
import { SyncIndicator } from "@/features/offline/components/sync-indicator";

type SessionData = {
  authenticated: boolean;
  sub?: string;
  roles?: string[];
  authSource?: string;
  supabase?: {
    user?: { id: string; email: string | null } | null;
    profile?: { app_role?: string } | null;
  } | null;
};

const pageTitleMap: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/syllabus": "Syllabus",
  "/practice": "AI Practice",
  "/progress": "Progress",
  "/schedule": "Schedule",
  "/achievements": "Achievements",
  "/settings": "Settings",
};

export function AppHeader() {
  const pathname = usePathname();
  const { refresh } = useSession();
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const title = pageTitleMap[pathname ?? ""] ?? "StudyOS";

  useEffect(() => {
    fetch("/api/auth/session", { credentials: "include", cache: "no-store" })
      .then((res) => res.json())
      .then(setSessionData)
      .catch(() => {});
  }, []);

  async function handleLogout() {
    try {
      const res = await fetch("/api/auth/logout", { method: "POST" });
      if (!res.ok) throw new Error("Logout failed");
      await refresh();
    } catch (e) {
      notifyFromUnknown(e, "Logout error");
    }
  }

  const userEmail = sessionData?.supabase?.user?.email ?? "User";
  const userRoles = sessionData?.roles ?? sessionData?.supabase?.profile?.app_role;
  const userInitial = userEmail.charAt(0).toUpperCase();

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-4 border-b border-border bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60 sm:px-6">
      <h1 className="text-lg font-semibold">{title}</h1>

      <div className="ml-auto flex items-center gap-2">
        <SyncIndicator />

        <Button variant="ghost" size="icon" aria-label="Notifications">
          <Bell className="h-4 w-4" />
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full" aria-label="User menu">
              <Avatar className="h-8 w-8">
                <AvatarFallback>{userInitial}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">{userEmail}</p>
                <p className="text-xs leading-none text-muted-foreground">
                  {userRoles ?? "No roles"}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <a href="/settings" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Profile
              </a>
            </DropdownMenuItem>
            <DropdownMenuItem asChild>
              <a href="/settings" className="flex items-center gap-2">
                <Settings className="h-4 w-4" />
                Settings
              </a>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="flex items-center gap-2 text-destructive">
              <LogOut className="h-4 w-4" />
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
