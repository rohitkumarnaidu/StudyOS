"use client";

import { useEffect } from "react";
import Link from "next/link";
import { ErrorFallback } from "@/shared/components/feedback/error-fallback";
import { ROUTES } from "@/shared/config/routes";

export default function AuthSegmentError({
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
    <div className="space-y-4">
      <ErrorFallback
        title="Authentication page error"
        description="Try again, or start over from the sign-in page."
        error={error}
        onRetry={() => reset()}
      />
      <Link
        href={ROUTES.login}
        className="text-sm font-medium text-primary underline-offset-4 hover:underline"
      >
        Back to sign in
      </Link>
    </div>
  );
}
