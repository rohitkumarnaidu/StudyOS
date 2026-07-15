"use client";

import { useTheme } from "next-themes";
import { useMemo } from "react";
import { Button } from "@/shared/components/ui/button";
import { useMounted } from "@/shared/hooks/use-mounted";

export function ThemeToggle() {
  const mounted = useMounted();
  const { resolvedTheme, setTheme } = useTheme();

  const label = useMemo(() => {
    if (!resolvedTheme) return "Toggle color theme";
    return resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode";
  }, [resolvedTheme]);

  if (!mounted) {
    return (
      <Button type="button" variant="ghost" className="h-9 w-9 px-0" disabled aria-hidden>
        <span className="sr-only">Theme</span>
      </Button>
    );
  }

  return (
    <Button
      type="button"
      variant="ghost"
      className="h-9 w-9 px-0"
      aria-label={label}
      title={label}
      onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
    >
      <span aria-hidden className="text-base">
        {resolvedTheme === "dark" ? "☀" : "☾"}
      </span>
    </Button>
  );
}
