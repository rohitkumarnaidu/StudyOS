"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import { useSession } from "@/features/auth/session-provider";
import { cn } from "@/shared/lib";
import { ThemeToggle } from "@/shared/components/layout/theme-toggle";

const nav = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/", label: "Home" },
];

async function logout() {
  await fetch("/api/auth/logout", { method: "POST" });
}

export function AppShellHeader() {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const { authenticated, loading } = useSession();

  async function handleLogout() {
    await logout();
    router.push("/");
    router.refresh();
  }

  return (
    <header className="border-b border-border bg-card/80 backdrop-blur supports-backdrop-filter:bg-card/60">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-4 py-3">
        <div className="flex min-w-0 flex-1 items-center gap-3">
          <Link
            href="/dashboard"
            className="truncate text-sm font-semibold tracking-tight text-foreground underline-offset-4 hover:underline"
          >
            StudyOS
          </Link>
          <nav aria-label="Main" className="hidden min-w-0 gap-1 md:flex">
            {nav.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex shrink-0 items-center gap-1">
          <ThemeToggle />
          {!loading && authenticated && (
            <Button
              type="button"
              variant="ghost"
              onClick={handleLogout}
              className="text-sm"
            >
              Sign out
            </Button>
          )}
          <Button
            type="button"
            variant="ghost"
            className="md:hidden"
            aria-expanded={open}
            aria-controls="mobile-nav"
            onClick={() => setOpen((v) => !v)}
          >
            Menu
          </Button>
        </div>
      </div>
      {open ? (
        <nav
          id="mobile-nav"
          aria-label="Mobile main"
          className="border-t border-border bg-card px-4 py-3 md:hidden"
        >
          <ul className="flex flex-col gap-2">
            {nav.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="block rounded-md px-2 py-2 text-sm text-foreground hover:bg-muted"
                  onClick={() => setOpen(false)}
                >
                  {item.label}
                </Link>
              </li>
            ))}
            {!loading && authenticated && (
              <li>
                <button
                  onClick={() => {
                    void handleLogout();
                    setOpen(false);
                  }}
                  className="block w-full rounded-md px-2 py-2 text-left text-sm text-foreground hover:bg-muted"
                >
                  Sign out
                </button>
              </li>
            )}
          </ul>
        </nav>
      ) : null}
    </header>
  );
}
