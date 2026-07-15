"use client";

import { useEffect } from "react";
import { ErrorFallback } from "@/shared/components/feedback/error-fallback";

export default function AppSegmentError({
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
    <ErrorFallback
      title="This section failed to load"
      description="Try again, or go back after the problem is fixed."
      error={error}
      onRetry={() => reset()}
      retryLabel="Retry"
    />
  );
}
