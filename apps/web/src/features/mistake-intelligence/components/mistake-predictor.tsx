"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Progress } from "@/shared/components/ui/progress";
import { usePredictions, useHighRiskConcepts, useImprovementTrend } from "@/features/mistake-intelligence/hooks/use-mistake-intelligence";
import { useState } from "react";

const RISK_COLORS: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-green-100 text-green-800 border-green-200",
};

const TREND_ICONS: Record<string, string> = {
  improving: "↑",
  declining: "↓",
  stable: "→",
  insufficient_data: "?",
};

export function MistakePredictor() {
  const { data: predictionsData, isLoading } = usePredictions();
  const { data: highRiskData } = useHighRiskConcepts(0.6);
  const [trendConcept, setTrendConcept] = useState<string | null>(null);
  const { data: trendData } = useImprovementTrend(trendConcept);

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Loading predictions...</div>;
  }

  return (
    <div className="space-y-6">
      {highRiskData?.high_risk_concepts && highRiskData.high_risk_concepts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>High Risk Concepts</CardTitle>
            <CardDescription>Likely to make mistakes on these topics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {highRiskData.high_risk_concepts.map((concept) => (
                <Badge key={concept} variant="destructive">
                  {concept}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {predictionsData?.predictions && predictionsData.predictions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Mistake Predictions</CardTitle>
            <CardDescription>Probability of making mistakes by concept</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {predictionsData.predictions.map((pred) => (
              <div key={pred.concept} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{pred.concept}</span>
                    <Badge className={RISK_COLORS[pred.risk_level] || ""}>
                      {pred.risk_level}
                    </Badge>
                  </div>
                  <span className="text-sm font-medium">{Math.round(pred.predicted_probability * 100)}%</span>
                </div>
                <Progress value={pred.predicted_probability * 100} />
                {pred.contributing_factors.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {pred.contributing_factors.map((f) => (
                      <Badge key={f} variant="outline" className="text-xs">
                        {f.replace(/_/g, " ")}
                      </Badge>
                    ))}
                  </div>
                )}
                <p className="text-xs text-muted-foreground">{pred.recommended_prevention}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Improvement Trend</CardTitle>
          <CardDescription>Check if you are improving on a concept</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Enter concept..."
              className="flex-1 px-3 py-2 border rounded-md text-sm"
              value={trendConcept || ""}
              onChange={(e) => setTrendConcept(e.target.value || null)}
            />
          </div>
          {trendData && (
            <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
              <span className="text-lg">{TREND_ICONS[trendData.trend] || "?"}</span>
              <span className="font-medium">{trendData.concept}</span>
              <Badge>{trendData.trend.replace(/_/g, " ")}</Badge>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
