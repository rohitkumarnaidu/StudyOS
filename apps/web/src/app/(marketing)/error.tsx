"use client";

import { useEffect } from "react";
import { ErrorFallback } from "@/shared/components/feedback/error-fallback";

export default function MarketingSegmentError({
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
      title="Something went wrong"
      description="This page hit an error. You can retry or return to the home page."
      error={error}
      onRetry={() => reset()}
    />
  );
}
