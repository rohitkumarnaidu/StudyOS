"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Progress } from "@/shared/components/ui/progress";
import { useMistakeStats } from "@/features/mistake-intelligence/hooks/use-mistake-intelligence";

const TYPE_LABELS: Record<string, string> = {
  conceptual: "Conceptual",
  calculation: "Calculation",
  misread: "Misread",
  guess: "Guess",
  time_pressure: "Time Pressure",
  careless: "Careless",
};

const TYPE_COLORS: Record<string, string> = {
  conceptual: "bg-red-100 text-red-800",
  calculation: "bg-orange-100 text-orange-800",
  misread: "bg-yellow-100 text-yellow-800",
  guess: "bg-blue-100 text-blue-800",
  time_pressure: "bg-purple-100 text-purple-800",
  careless: "bg-gray-100 text-gray-800",
};

export function MistakeStatsOverview() {
  const { data, isLoading } = useMistakeStats();

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Loading stats...</div>;
  }

  if (!data || data.total_mistakes === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">No mistakes recorded yet. Keep studying!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mistake Overview</CardTitle>
        <CardDescription>{data.total_mistakes} total mistakes tracked</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-muted rounded-lg">
            <p className="text-2xl font-bold">{Math.round(data.avg_confidence * 100)}%</p>
            <p className="text-xs text-muted-foreground">Avg Confidence</p>
          </div>
          <div className="text-center p-3 bg-muted rounded-lg">
            <p className="text-2xl font-bold">{Math.round(data.avg_time_seconds)}s</p>
            <p className="text-xs text-muted-foreground">Avg Time</p>
          </div>
          <div className="text-center p-3 bg-muted rounded-lg">
            <p className="text-2xl font-bold">{Object.keys(data.type_distribution || {}).length}</p>
            <p className="text-xs text-muted-foreground">Mistake Types</p>
          </div>
        </div>

        {data.type_distribution && Object.keys(data.type_distribution).length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Mistake Distribution</h4>
            <div className="space-y-2">
              {Object.entries(data.type_distribution)
                .sort(([, a], [, b]) => b - a)
                .map(([type, count]) => {
                  const total = data.total_mistakes;
                  const pct = Math.round((count / total) * 100);
                  return (
                    <div key={type} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <Badge className={TYPE_COLORS[type] || ""}>
                          {TYPE_LABELS[type] || type}
                        </Badge>
                        <span className="text-muted-foreground">{count} ({pct}%)</span>
                      </div>
                      <Progress value={pct} />
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {data.top_concepts && data.top_concepts.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Top Problem Concepts</h4>
            <div className="flex flex-wrap gap-2">
              {data.top_concepts.map(([concept, count]) => (
                <Badge key={concept} variant="secondary">
                  {concept} ({count})
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
