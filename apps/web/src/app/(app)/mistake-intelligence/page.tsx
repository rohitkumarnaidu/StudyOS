"use client";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { MistakeStatsOverview } from "@/features/mistake-intelligence/components/mistake-stats-overview";
import { KnowledgeGapAnalyzer } from "@/features/mistake-intelligence/components/knowledge-gap-analyzer";
import { MistakePredictor } from "@/features/mistake-intelligence/components/mistake-predictor";
import { MistakeClusterer } from "@/features/mistake-intelligence/components/mistake-clusterer";
import { IntelligenceReport } from "@/features/mistake-intelligence/components/intelligence-report";

export default function MistakeIntelligencePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Mistake Intelligence</h1>
        <p className="text-sm text-muted-foreground">
          Track, analyze, and predict mistakes to identify knowledge gaps and optimize your study plan.
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="gaps">Knowledge Gaps</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="clusters">Clusters</TabsTrigger>
          <TabsTrigger value="report">Full Report</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <MistakeStatsOverview />
        </TabsContent>

        <TabsContent value="gaps">
          <KnowledgeGapAnalyzer />
        </TabsContent>

        <TabsContent value="predictions">
          <MistakePredictor />
        </TabsContent>

        <TabsContent value="clusters">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MistakeClusterer />
          </div>
        </TabsContent>

        <TabsContent value="report">
          <IntelligenceReport />
        </TabsContent>
      </Tabs>
    </div>
  );
}
