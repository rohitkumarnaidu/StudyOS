"use client";

import { cn } from "@/shared/lib";

interface OMRSheetProps {
  totalQuestions: number;
  answers: Record<string, string>;
  currentQuestion: number;
  onNavigate: (index: number) => void;
  markedQuestions?: Set<string>;
}

export function OMRSheet({
  totalQuestions,
  answers,
  currentQuestion,
  onNavigate,
  markedQuestions = new Set(),
}: OMRSheetProps) {
  const questions = Array.from({ length: totalQuestions }, (_, i) => i + 1);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-3 text-sm font-semibold">OMR Sheet</h3>
      <div className="grid grid-cols-10 gap-1">
        {questions.map((num) => {
          const qId = `q-${num}`;
          const answered = !!answers[qId];
          const marked = markedQuestions.has(qId);
          const isCurrent = num === currentQuestion;

          return (
            <button
              key={num}
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded text-xs font-medium transition-colors",
                isCurrent
                  ? "bg-primary text-primary-foreground"
                  : answered
                    ? "bg-emerald-500/20 text-emerald-600"
                    : marked
                      ? "bg-amber-500/20 text-amber-600"
                      : "bg-muted text-muted-foreground hover:bg-muted/80",
              )}
              onClick={() => onNavigate(num - 1)}
              aria-label={`Question ${num}`}
            >
              {num}
            </button>
          );
        })}
      </div>
      <div className="mt-3 flex gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-primary" /> Current
        </span>
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-emerald-500/20" /> Answered
        </span>
        <span className="flex items-center gap-1">
          <span className="h-3 w-3 rounded bg-amber-500/20" /> Marked
        </span>
      </div>
    </div>
  );
}
