"use client";

import { useState, useEffect } from "react";
import type { MistakeEntry } from "@/features/quiz/api";
import { listMistakes, reviewMistake, deleteMistake } from "@/features/quiz/api";
import { Button } from "@/shared/components/ui/button";
import { Check, Trash2, BookOpen } from "lucide-react";
import { notifySuccess, notifyError } from "@/shared/lib";

export function MistakeLog() {
  const [mistakes, setMistakes] = useState<MistakeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "unreviewed">("all");

  useEffect(() => {
    void listMistakes()
      .then(setMistakes)
      .finally(() => setLoading(false));
  }, []);

  const filtered =
    filter === "unreviewed" ? mistakes.filter((m) => !m.reviewed) : mistakes;

  async function handleReview(id: string) {
    try {
      await reviewMistake(id);
      setMistakes((prev) =>
        prev.map((m) =>
          m.id === id ? { ...m, reviewed: true, review_count: m.review_count + 1 } : m,
        ),
      );
      notifySuccess("Marked as reviewed");
    } catch {
      notifyError("Failed to update mistake");
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteMistake(id);
      setMistakes((prev) => prev.filter((m) => m.id !== id));
      notifySuccess("Removed from mistake log");
    } catch {
      notifyError("Failed to delete mistake");
    }
  }

  if (loading) {
    return <div className="py-8 text-center text-sm text-muted-foreground">Loading mistakes...</div>;
  }

  if (mistakes.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-card/50 px-4 py-12 text-center">
        <BookOpen className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">
          No mistakes logged. Keep practicing!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Mistake Log</h2>
        <div className="flex gap-2">
          <Button
            variant={filter === "all" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter("all")}
          >
            All ({mistakes.length})
          </Button>
          <Button
            variant={filter === "unreviewed" ? "default" : "outline"}
            size="sm"
            onClick={() => setFilter("unreviewed")}
          >
            Unreviewed ({mistakes.filter((m) => !m.reviewed).length})
          </Button>
        </div>
      </div>

      <div className="space-y-3">
        {filtered.map((m) => (
          <div
            key={m.id}
            className="rounded-lg border border-border bg-card p-4"
          >
            <p className="text-sm font-medium mb-2">{m.question_text}</p>
            <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
              <span>
                Your answer: <span className="text-destructive">{m.user_answer ?? "Skipped"}</span>
              </span>
              <span>
                Correct: <span className="text-emerald-600">{m.correct_answer}</span>
              </span>
              <span>Reviewed {m.review_count}x</span>
            </div>
            {m.explanation && (
              <p className="text-xs text-muted-foreground mb-3">{m.explanation}</p>
            )}
            <div className="flex gap-2">
              {!m.reviewed && (
                <Button size="sm" variant="outline" onClick={() => void handleReview(m.id)}>
                  <Check className="mr-1 h-3 w-3" />
                  Mark Reviewed
                </Button>
              )}
              <Button size="sm" variant="ghost" onClick={() => void handleDelete(m.id)}>
                <Trash2 className="mr-1 h-3 w-3" />
                Remove
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
