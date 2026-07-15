"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { useIntelligenceReport } from "@/features/mistake-intelligence/hooks/use-mistake-intelligence";

export function IntelligenceReport() {
  const { data, isLoading } = useIntelligenceReport();

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Generating report...</div>;
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">No data available yet. Start tracking mistakes to see insights.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Intelligence Report</CardTitle>
          <CardDescription>Complete overview of your learning patterns</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-2xl font-bold">{data.mistake_stats.total_mistakes}</p>
              <p className="text-sm text-muted-foreground">Total Mistakes</p>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-2xl font-bold">{data.knowledge_gaps.length}</p>
              <p className="text-sm text-muted-foreground">Knowledge Gaps</p>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-2xl font-bold">{data.predictions.length}</p>
              <p className="text-sm text-muted-foreground">Predictions</p>
            </div>
            <div className="text-center p-4 bg-muted rounded-lg">
              <p className="text-2xl font-bold">{data.clusters.length}</p>
              <p className="text-sm text-muted-foreground">Clusters</p>
            </div>
          </div>

          {data.study_plan.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium">Priority Study Plan</h4>
              {data.study_plan.map((item, idx) => (
                <div key={item.concept} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">#{idx + 1}</span>
                    <span>{item.concept}</span>
                    <Badge variant={item.priority === "high" ? "destructive" : item.priority === "medium" ? "default" : "secondary"}>
                      {item.priority}
                    </Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">{Math.round(item.gap_score * 100)}% gap</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
