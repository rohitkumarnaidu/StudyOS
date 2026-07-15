"use client";

import { DueItemsList } from "@/features/revision/components/due-items-list";
import { RetentionDashboard } from "@/features/revision/components/retention-dashboard";
import { RevisionPackGenerator } from "@/features/revision/components/revision-pack-generator";
import { ActiveRecallSession } from "@/features/revision/components/active-recall-session";

export default function RevisionPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Smart Revision</h1>
        <p className="text-sm text-muted-foreground">
          Spaced repetition, active recall, and personalized revision packs to maximize retention.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <RetentionDashboard />
          <RevisionPackGenerator />
        </div>
        <div className="space-y-6">
          <DueItemsList />
          <ActiveRecallSession />
        </div>
      </div>
    </div>
  );
}
