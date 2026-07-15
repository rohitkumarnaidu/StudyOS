"use client";

import { useState } from "react";
import type { ChapterData, TopicData, SubtopicData } from "@/server/syllabus/get-chapters";
import { useToggleSubtopic } from "@/features/progress/hooks/use-progress";
import { Check } from "lucide-react";

interface ChapterListProps {
  chapters: ChapterData[];
  completedSubtopicIds?: Set<string>;
}

function SubtopicItem({
  subtopic,
  completed,
  onToggle,
  disabled,
}: {
  subtopic: SubtopicData;
  completed: boolean;
  onToggle: () => void;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      disabled={disabled}
      className="flex w-full items-start gap-3 rounded px-2 py-2 text-left text-xs transition-colors hover:bg-muted/50 disabled:cursor-not-allowed disabled:opacity-50"
      aria-label={`Mark "${subtopic.name}" ${completed ? "incomplete" : "complete"}`}
    >
      <div
        className={`mt-0.5 flex h-4 w-4 flex-shrink-0 items-center justify-center rounded border transition-colors ${
          completed
            ? "border-emerald-500 bg-emerald-500 text-white"
            : "border-input"
        }`}
      >
        {completed && <Check className="h-3 w-3" />}
      </div>
      <div className="flex-1 min-w-0">
        <p
          className={`truncate transition-colors ${
            completed ? "text-muted-foreground line-through" : "text-foreground"
          }`}
        >
          {subtopic.name}
        </p>
        {subtopic.estimated_minutes && (
          <p className="text-xs text-muted-foreground">{subtopic.estimated_minutes} min</p>
        )}
      </div>
    </button>
  );
}

function TopicItem({
  topic,
  completedIds,
  onToggle,
  togglingId,
}: {
  topic: TopicData;
  completedIds: Set<string>;
  onToggle: (id: string) => void;
  togglingId: string | null;
}) {
  const [expanded, setExpanded] = useState(false);
  const completedCount = topic.subtopics.filter((s) => completedIds.has(s.id)).length;
  const totalCount = topic.subtopics.length;
  const isComplete = completedCount === totalCount && totalCount > 0;

  return (
    <div className="border-l border-border">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 rounded px-3 py-2 text-left text-sm hover:bg-muted/50"
      >
        <span
          className="inline-flex h-4 w-4 items-center justify-center text-xs transition-transform flex-shrink-0"
          style={{ transform: expanded ? "rotate(0deg)" : "rotate(-90deg)" }}
        >
          ▼
        </span>
        <span className="flex-1 truncate font-medium text-foreground">{topic.name}</span>
        <span
          className={`flex-shrink-0 text-xs ${
            isComplete ? "text-emerald-500" : "text-muted-foreground"
          }`}
        >
          {completedCount}/{totalCount}
        </span>
      </button>

      {expanded && (
        <div className="space-y-1 bg-muted/30 px-3 py-2">
          {topic.subtopics.map((subtopic) => (
            <SubtopicItem
              key={subtopic.id}
              subtopic={subtopic}
              completed={completedIds.has(subtopic.id)}
              onToggle={() => onToggle(subtopic.id)}
              disabled={togglingId === subtopic.id}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ChapterCard({
  chapter,
  completedIds,
  onToggle,
  togglingId,
}: {
  chapter: ChapterData;
  completedIds: Set<string>;
  onToggle: (id: string) => void;
  togglingId: string | null;
}) {
  const [expanded, setExpanded] = useState(false);
  const topicCount = chapter.topics.length;
  const subtopicCount = chapter.topics.reduce((sum, t) => sum + t.subtopics.length, 0);
  const completedCount = chapter.topics.reduce(
    (sum, t) => sum + t.subtopics.filter((s) => completedIds.has(s.id)).length,
    0,
  );
  const progressPct = subtopicCount > 0 ? (completedCount / subtopicCount) * 100 : 0;

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-card transition-colors hover:border-border/80">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left hover:bg-muted/30"
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="truncate font-semibold text-foreground">{chapter.name}</h3>
            {progressPct >= 100 && (
              <span className="flex-shrink-0 rounded-full bg-emerald-500/10 px-1.5 py-0.5 text-xs text-emerald-600">
                Done
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            {topicCount} topic{topicCount !== 1 ? "s" : ""} • {completedCount}/{subtopicCount} subtopics
          </p>
          <div className="mt-1 h-1 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-300"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
        <span
          className="inline-flex h-5 w-5 items-center justify-center transition-transform flex-shrink-0 text-muted-foreground"
          style={{ transform: expanded ? "rotate(0deg)" : "rotate(-90deg)" }}
        >
          ▼
        </span>
      </button>

      {expanded && (
        <div className="border-t border-border/50 bg-muted/10 px-4 py-3">
          <div className="space-y-1">
            {chapter.topics.map((topic) => (
              <TopicItem
                key={topic.id}
                topic={topic}
                completedIds={completedIds}
                onToggle={onToggle}
                togglingId={togglingId}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function ChapterList({ chapters, completedSubtopicIds }: ChapterListProps) {
  const toggleMutation = useToggleSubtopic();
  const completedIds = completedSubtopicIds ?? new Set<string>();

  function handleToggle(subtopicId: string) {
    toggleMutation.mutate(subtopicId);
  }

  if (chapters.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-card/50 px-4 py-8 text-center">
        <p className="text-sm text-muted-foreground">No chapters available</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {chapters.map((chapter) => (
        <ChapterCard
          key={chapter.id}
          chapter={chapter}
          completedIds={completedIds}
          onToggle={handleToggle}
          togglingId={toggleMutation.variables ?? null}
        />
      ))}
    </div>
  );
}
