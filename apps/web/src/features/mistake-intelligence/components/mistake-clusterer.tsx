"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { useClusterMistakes } from "@/features/mistake-intelligence/hooks/use-mistake-intelligence";

export function MistakeClusterer() {
  const [clusterResult, setClusterResult] = useState<{ clusters: Array<{ cluster_id: string; theme: string; mistake_count: number; common_concepts: string[] }> } | null>(null);
  const clusterMutation = useClusterMistakes();

  const handleCluster = () => {
    clusterMutation.mutate({ minClusterSize: 2 }, {
      onSuccess: (data) => setClusterResult(data),
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Mistake Clusters</CardTitle>
        <CardDescription>Group similar mistakes to find patterns</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button onClick={handleCluster} disabled={clusterMutation.isPending} className="w-full">
          {clusterMutation.isPending ? "Clustering..." : "Find Clusters"}
        </Button>

        {clusterResult?.clusters && clusterResult.clusters.length > 0 && (
          <div className="space-y-3">
            {clusterResult.clusters.map((cluster) => (
              <div key={cluster.cluster_id} className="p-3 bg-muted rounded-lg space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{cluster.theme}</span>
                  <Badge>{cluster.mistake_count} mistakes</Badge>
                </div>
                {cluster.common_concepts.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {cluster.common_concepts.map((c) => (
                      <Badge key={c} variant="outline" className="text-xs">
                        {c}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {clusterResult?.clusters && clusterResult.clusters.length === 0 && (
          <p className="text-center text-sm text-muted-foreground">No clusters found. Add more mistakes to find patterns.</p>
        )}
      </CardContent>
    </Card>
  );
}
