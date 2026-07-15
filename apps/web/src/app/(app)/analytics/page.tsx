"use client";

import { AnalyticsDashboard } from "@/features/analytics/components/analytics-dashboard";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Track your study progress, quiz performance, and identify areas to improve.
        </p>
      </div>

      <AnalyticsDashboard />
    </div>
  );
}
