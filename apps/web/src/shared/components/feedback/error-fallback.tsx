"use client";

import type { ReactNode } from "react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib";

type ErrorFallbackProps = {
  title: string;
  description?: ReactNode;
  error?: Pick<Error, "message"> & { digest?: string };
  onRetry?: () => void;
  retryLabel?: string;
  className?: string;
};

export function ErrorFallback({
  title,
  description,
  error,
  onRetry,
  retryLabel = "Try again",
  className,
}: ErrorFallbackProps) {
  return (
    <div
      role="alert"
      className={cn(
        "flex flex-col items-start gap-4 rounded-xl border border-border bg-card p-6 text-card-foreground",
        className,
      )}
    >
      <div className="space-y-2">
        <h2 className="text-lg font-semibold tracking-tight">{title}</h2>
        {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
        {error?.message ? <p className="text-sm text-destructive">{error.message}</p> : null}
        {error?.digest ? (
          <p className="text-xs text-muted-foreground">Reference: {error.digest}</p>
        ) : null}
      </div>
      {onRetry ? (
        <Button type="button" onClick={onRetry}>
          {retryLabel}
        </Button>
      ) : null}
    </div>
  );
}
