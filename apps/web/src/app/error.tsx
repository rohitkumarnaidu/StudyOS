"use client";

import { useEffect } from "react";
import { Button } from "@/shared/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-4 text-foreground">
        <div className="max-w-md text-center">
          <h1 className="text-lg font-semibold">Something went wrong</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            An unexpected error occurred. You can try again or return home.
          </p>
          {error.digest ? (
            <p className="mt-2 text-xs text-muted-foreground">Reference: {error.digest}</p>
          ) : null}
        </div>
        <div className="flex gap-2">
          <Button type="button" onClick={() => reset()}>
            Try again
          </Button>
          <Button type="button" variant="secondary" onClick={() => (window.location.href = "/")}>
            Home
          </Button>
        </div>
      </body>
    </html>
  );
}
