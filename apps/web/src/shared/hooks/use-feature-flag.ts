"use client";

/* eslint-disable react-hooks/set-state-in-effect -- required for external state subscription */
import { useState, useEffect, useRef, useCallback } from "react";
import { posthog } from "@/shared/lib/posthog";

interface UseFeatureFlagOptions {
  flagKey: string;
  defaultValue?: boolean;
}

/**
 * React hook for evaluating PostHog feature flags.
 *
 * Usage:
 *   const { enabled, loading } = useFeatureFlag("new-quiz-ui");
 *   if (enabled) return <NewQuizUI />;
 *   return <LegacyQuizUI />;
 */
export function useFeatureFlag({ flagKey, defaultValue = false }: UseFeatureFlagOptions) {
  const [enabled, setEnabled] = useState(() => {
    try {
      return posthog.isFeatureEnabled(flagKey) ?? defaultValue;
    } catch {
      return defaultValue;
    }
  });
  const [loading] = useState(false);
  const isMounted = useRef(true);

  const updateFlag = useCallback(() => {
    try {
      const value = posthog.isFeatureEnabled(flagKey);
      if (isMounted.current) {
        setEnabled(value ?? defaultValue);
      }
    } catch {
      if (isMounted.current) {
        setEnabled(defaultValue);
      }
    }
  }, [flagKey, defaultValue]);

  useEffect(() => {
    isMounted.current = true;
    updateFlag();

    const unsubscribe = posthog.onFeatureFlags(() => {
      updateFlag();
    });

    return () => {
      isMounted.current = false;
      unsubscribe();
    };
  }, [updateFlag]);

  return { enabled, loading };
}
