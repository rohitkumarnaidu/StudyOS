"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { useGenerateRevisionPack } from "@/features/revision/hooks/use-revision";
import type { RevisionPack } from "@/features/revision/api";

const PACK_MODES = [
  { value: "due", label: "Due Items", description: "Items scheduled for review today" },
  { value: "weak", label: "Weak Areas", description: "Items with lowest retention" },
  { value: "mixed", label: "Mixed Review", description: "Blend of due and weak items" },
  { value: "cram", label: "Cram Session", description: "Maximum items for quick review" },
] as const;

export function RevisionPackGenerator() {
  const [generatedPack, setGeneratedPack] = useState<RevisionPack | null>(null);
  const generateMutation = useGenerateRevisionPack();

  const handleGenerate = (mode: "due" | "weak" | "mixed" | "cram") => {
    generateMutation.mutate({ mode, maxItems: 20 }, {
      onSuccess: (data) => setGeneratedPack(data),
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate Revision Pack</CardTitle>
        <CardDescription>Choose a review strategy</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          {PACK_MODES.map((mode) => (
            <Button
              key={mode.value}
              variant="outline"
              className="h-auto flex-col items-start p-4 space-y-1"
              disabled={generateMutation.isPending}
              onClick={() => handleGenerate(mode.value)}
            >
              <span className="font-medium">{mode.label}</span>
              <span className="text-xs text-muted-foreground">{mode.description}</span>
            </Button>
          ))}
        </div>

        {generateMutation.isPending && (
          <p className="text-center text-sm text-muted-foreground">Generating pack...</p>
        )}

        {generatedPack && (
          <div className="mt-4 p-4 bg-muted rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <Badge>{generatedPack.mode}</Badge>
              <span className="text-sm text-muted-foreground">
                {generatedPack.items.length} items
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              Created: {new Date(generatedPack.created_at).toLocaleDateString()}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
