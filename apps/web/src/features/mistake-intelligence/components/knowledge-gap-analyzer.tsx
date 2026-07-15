"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { useWeakConcepts, useStudyPlan } from "@/features/mistake-intelligence/hooks/use-mistake-intelligence";

export function KnowledgeGapAnalyzer() {
  const { data: weakData, isLoading: weakLoading } = useWeakConcepts(5);
  const { data: planData, isLoading: planLoading } = useStudyPlan(5);

  if (weakLoading || planLoading) {
    return <div className="text-center py-8 text-muted-foreground">Analyzing gaps...</div>;
  }

  return (
    <div className="space-y-6">
      {weakData?.weak_concepts && weakData.weak_concepts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Weak Concepts</CardTitle>
            <CardDescription>Areas needing the most attention</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {weakData.weak_concepts.map((gap) => (
              <div key={gap.concept} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{gap.concept}</span>
                    <Badge variant={gap.gap_score > 0.8 ? "destructive" : gap.gap_score > 0.6 ? "default" : "secondary"}>
                      {Math.round(gap.gap_score * 100)}% gap
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{gap.recommended_action}</p>
                </div>
                <span className="text-sm text-muted-foreground ml-4">{gap.mistake_count} mistakes</span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {planData?.study_plan && planData.study_plan.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recommended Study Plan</CardTitle>
            <CardDescription>Prioritized actions based on your gaps</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {planData.study_plan.map((item, idx) => (
              <div key={item.concept} className="p-3 bg-muted rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">#{idx + 1}</span>
                    <span className="font-medium">{item.concept}</span>
                    <Badge
                      variant={item.priority === "high" ? "destructive" : item.priority === "medium" ? "default" : "secondary"}
                    >
                      {item.priority}
                    </Badge>
                  </div>
                  <span className="text-sm text-muted-foreground">{Math.round(item.gap_score * 100)}% gap</span>
                </div>
                <p className="text-sm text-muted-foreground">{item.action}</p>
                {item.related_concepts.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {item.related_concepts.map((c) => (
                      <Badge key={c} variant="outline" className="text-xs">
                        {c}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
