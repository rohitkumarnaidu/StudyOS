"use client";

import { useState, useCallback } from "react";
import type { QuizQuestion } from "@/features/quiz/api";
import { submitAnswer } from "@/features/quiz/api";
import { Button } from "@/shared/components/ui/button";
import { TimerBar } from "@/features/quiz/components/timer-bar";
import { OMRSheet } from "@/features/quiz/components/omr-sheet";
import { ChevronLeft, ChevronRight, Flag } from "lucide-react";
import { cn } from "@/shared/lib";
import { notifyError } from "@/shared/lib";

interface MockTestProps {
  sessionId: string;
  questions: QuizQuestion[];
  timeLimitSeconds: number;
  onFinish: () => void;
}

export function MockTest({ sessionId, questions, timeLimitSeconds, onFinish }: MockTestProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [marked, setMarked] = useState<Set<string>>(new Set());

  const question = questions[currentIndex];
  const options = [
    { key: "A", value: question.option_a },
    { key: "B", value: question.option_b },
    { key: "C", value: question.option_c },
    { key: "D", value: question.option_d },
  ].filter((o) => o.value);

  const handleSelect = useCallback(
    async (optionKey: string) => {
      const qId = question.id;
      setAnswers((prev) => ({ ...prev, [qId]: optionKey }));
      try {
        await submitAnswer(sessionId, qId, optionKey);
      } catch {
        notifyError("Failed to submit answer");
      }
    },
    [question.id, sessionId],
  );

  const handleMark = useCallback(() => {
    setMarked((prev) => {
      const next = new Set(prev);
      const qId = question.id;
      if (next.has(qId)) next.delete(qId);
      else next.add(qId);
      return next;
    });
  }, [question.id]);

  const handleFinish = useCallback(() => {
    onFinish();
  }, [onFinish]);

  const answeredCount = Object.keys(answers).length;

  return (
    <div className="flex h-full">
      <div className="flex-1 flex flex-col">
        <div className="border-b border-border bg-muted/20 px-4 py-3">
          <TimerBar totalSeconds={timeLimitSeconds} onTimeUp={handleFinish} />
        </div>

        <div className="flex-1 overflow-auto px-4 py-6">
          <div className="mx-auto max-w-2xl space-y-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                Question {currentIndex + 1} of {questions.length}
              </span>
              <span className="text-xs text-muted-foreground">
                {answeredCount}/{questions.length} answered
              </span>
            </div>

            <div className="rounded-lg border border-border bg-card p-6">
              <div className="flex items-start gap-2 mb-4">
                <span className="flex-shrink-0 rounded bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  Q{currentIndex + 1}
                </span>
                {marked.has(question.id) && (
                  <Flag className="h-4 w-4 text-amber-500" />
                )}
              </div>

              <p className="text-base font-medium mb-6">{question.question_text}</p>

              <div className="space-y-3">
                {options.map((option) => {
                  const isSelected = answers[question.id] === option.key;
                  return (
                    <button
                      key={option.key}
                      className={cn(
                        "flex w-full items-center gap-3 rounded-lg border px-4 py-3 text-left transition-colors",
                        isSelected
                          ? "border-primary bg-primary/10"
                          : "border-border hover:bg-muted/50",
                      )}
                      onClick={() => handleSelect(option.key)}
                    >
                      <span
                        className={cn(
                          "flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border text-sm font-medium",
                          isSelected
                            ? "border-primary bg-primary text-primary-foreground"
                            : "border-border",
                        )}
                      >
                        {option.key}
                      </span>
                      <span className="text-sm">{option.value}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-border bg-background px-4 py-3">
          <div className="mx-auto flex max-w-2xl items-center justify-between gap-3">
            <Button
              variant="outline"
              onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="mr-1 h-4 w-4" />
              Previous
            </Button>

            <Button variant="ghost" size="sm" onClick={handleMark}>
              <Flag className={cn("mr-1 h-4 w-4", marked.has(question.id) && "text-amber-500")} />
              Mark
            </Button>

            {currentIndex < questions.length - 1 ? (
              <Button onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}>
                Next
                <ChevronRight className="ml-1 h-4 w-4" />
              </Button>
            ) : (
              <Button onClick={handleFinish} variant="default">
                Submit Test
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="w-72 border-l border-border overflow-auto p-4">
        <OMRSheet
          totalQuestions={questions.length}
          answers={answers}
          currentQuestion={currentIndex + 1}
          onNavigate={setCurrentIndex}
          markedQuestions={marked}
        />
      </div>
    </div>
  );
}
