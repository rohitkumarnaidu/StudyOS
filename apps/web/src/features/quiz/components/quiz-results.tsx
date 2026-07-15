"use client";

import type { QuizResult } from "@/features/quiz/api";
import { Button } from "@/shared/components/ui/button";
import { CheckCircle2, XCircle, Minus, Clock, Trophy, Target } from "lucide-react";
import { cn } from "@/shared/lib";
import Link from "next/link";

interface QuizResultsProps {
  result: QuizResult;
  onRetry?: () => void;
}

export function QuizResults({ result, onRetry }: QuizResultsProps) {
  const scoreColor =
    result.score_percent >= 80
      ? "text-emerald-500"
      : result.score_percent >= 50
        ? "text-amber-500"
        : "text-destructive";

  const timeMin = Math.floor(result.time_taken_seconds / 60);
  const timeSec = result.time_taken_seconds % 60;

  return (
    <div className="mx-auto max-w-2xl space-y-6 py-6">
      <div className="rounded-lg border border-border bg-card p-6 text-center">
        <Trophy className={cn("mx-auto mb-3 h-12 w-12", scoreColor)} />
        <h2 className="text-2xl font-bold">{result.score_percent}%</h2>
        <p className="text-sm text-muted-foreground">
          {result.correct} correct out of {result.total_questions}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard icon={CheckCircle2} label="Correct" value={result.correct} color="text-emerald-500" />
        <StatCard icon={XCircle} label="Incorrect" value={result.incorrect} color="text-destructive" />
        <StatCard icon={Minus} label="Skipped" value={result.skipped} color="text-muted-foreground" />
        <StatCard icon={Clock} label="Time" value={`${timeMin}m ${timeSec}s`} color="text-blue-500" />
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-semibold">Question Review</h3>
        {result.responses.map((r, i) => (
          <div
            key={r.question_id}
            className={cn(
              "rounded-lg border p-4",
              r.is_correct
                ? "border-emerald-500/30 bg-emerald-500/5"
                : "border-destructive/30 bg-destructive/5",
            )}
          >
            <div className="flex items-start gap-2">
              {r.is_correct ? (
                <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-500" />
              ) : (
                <XCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-destructive" />
              )}
              <div className="flex-1">
                <p className="text-sm font-medium">
                  Q{i + 1}. {r.question_text}
                </p>
                {!r.is_correct && (
                  <div className="mt-2 space-y-1 text-xs">
                    <p>
                      Your answer: <span className="text-destructive">{r.user_answer ?? "Skipped"}</span>
                    </p>
                    <p>
                      Correct answer: <span className="text-emerald-600">{r.correct_answer}</span>
                    </p>
                    {r.explanation && (
                      <p className="text-muted-foreground">{r.explanation}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        {onRetry && (
          <Button variant="outline" onClick={onRetry} className="flex-1">
            <Target className="mr-2 h-4 w-4" />
            Retry
          </Button>
        )}
        <Button asChild variant="default" className="flex-1">
          <Link href="/quiz">Back to Quiz Hub</Link>
        </Button>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  color: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 text-center">
      <Icon className={cn("mx-auto mb-2 h-5 w-5", color)} />
      <p className="text-lg font-bold">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  );
}
