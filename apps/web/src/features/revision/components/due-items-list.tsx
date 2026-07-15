"use client";

import { useCallback, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Button } from "@/shared/components/ui/button";
import { Badge } from "@/shared/components/ui/badge";
import { useDueItems, useReviewItem } from "@/features/revision/hooks/use-revision";
import type { SpacedRepetitionItem } from "@/features/revision/api";

const QUALITY_LABELS = ["Blackout", "Incorrect", "Hard", "Good", "Easy", "Perfect"];

function formatInterval(days: number): string {
  if (days < 1) return "Today";
  if (days === 1) return "Tomorrow";
  if (days < 30) return `${Math.round(days)} days`;
  if (days < 365) return `${Math.round(days / 30)} months`;
  return `${Math.round(days / 365)} years`;
}

export function DueItemsList() {
  const { data: items, isLoading } = useDueItems();
  const reviewMutation = useReviewItem();
  const [reviewingId, setReviewingId] = useState<string | null>(null);

  const handleReview = useCallback(
    (itemId: string, quality: number) => {
      setReviewingId(itemId);
      reviewMutation.mutate({ itemId, quality }, {
        onSettled: () => {
          setReviewingId(null);
        },
      });
    },
    [reviewMutation],
  );

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Loading due items...</div>;
  }

  if (!items || items.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">No items due for review. Great job!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {items.map((item) => (
        <ReviewCard
          key={item.id}
          item={item}
          isReviewing={reviewingId === item.id}
          onReview={(quality) => handleReview(item.id, quality)}
        />
      ))}
    </div>
  );
}

function ReviewCard({
  item,
  isReviewing,
  onReview,
}: {
  item: SpacedRepetitionItem;
  isReviewing: boolean;
  onReview: (quality: number) => void;
}) {
  const [showQuality, setShowQuality] = useState(false);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{item.content_type}</CardTitle>
          <Badge variant={item.interval < 1 ? "destructive" : item.interval < 7 ? "default" : "secondary"}>
            {formatInterval(item.interval)}
          </Badge>
        </div>
        <CardDescription>
          Ease: {item.ease_factor.toFixed(2)} · Reviews: {item.repetitions}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!showQuality ? (
          <Button onClick={() => setShowQuality(true)} className="w-full">
            Review Now
          </Button>
        ) : (
          <div className="space-y-3">
            <p className="text-sm font-medium">How well did you recall?</p>
            <div className="grid grid-cols-3 gap-2">
              {QUALITY_LABELS.map((label, idx) => (
                <Button
                  key={idx}
                  variant={idx < 3 ? "destructive" : idx < 5 ? "secondary" : "default"}
                  size="sm"
                  disabled={isReviewing}
                  onClick={() => onReview(idx)}
                >
                  {label}
                </Button>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
