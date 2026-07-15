"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Progress } from "@/shared/components/ui/progress";
import { useRetentionSummary } from "@/features/revision/hooks/use-revision";

export function RetentionDashboard() {
  const { data, isLoading } = useRetentionSummary();

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Loading retention data...</div>;
  }

  if (!data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">No retention data yet. Start reviewing to build your memory profile.</p>
        </CardContent>
      </Card>
    );
  }

  const retentionPct = Math.round(data.average_retention * 100);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Retention Overview</CardTitle>
        <CardDescription>Your memory strength across all reviewed items</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Average Retention</span>
            <span className="font-medium">{retentionPct}%</span>
          </div>
          <Progress value={retentionPct} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-4 bg-muted rounded-lg">
            <p className="text-2xl font-bold">{data.total_records}</p>
            <p className="text-sm text-muted-foreground">Total Reviews</p>
          </div>
          <div className="text-center p-4 bg-muted rounded-lg">
            <p className="text-2xl font-bold">{Math.round(data.model_accuracy * 100)}%</p>
            <p className="text-sm text-muted-foreground">Model Accuracy</p>
          </div>
        </div>

        {data.weak_items.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Weak Items (needs review)</h4>
            <div className="space-y-2">
              {data.weak_items.slice(0, 5).map((item) => (
                <div key={item.item_id} className="flex items-center justify-between p-2 bg-muted/50 rounded">
                  <span className="text-sm">{item.item_id.slice(0, 8)}...</span>
                  <span className="text-sm text-destructive">{Math.round(item.retention * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
