"use client";

import { useState } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Switch } from "@/shared/components/ui/switch";
import { useOfflineToggleSubtopic } from "@/features/offline/hooks/use-offline-toggle";
import { useOfflineCompletedIds } from "@/features/offline/hooks/use-offline-toggle";

export interface TopicData {
  id: string;
  name: string;
  sort_order: number;
  subtopics: Array<{
    id: string;
    name: string;
    sort_order: number;
    estimated_minutes: number | null;
  }>;
}

interface ChapterDetailClientProps {
  chapterName: string;
  topics: TopicData[];
  totalSubtopics: number;
  completedSubtopics?: string[];
}

export function ChapterDetailClient({
  chapterName,
  topics,
  totalSubtopics,
  completedSubtopics = [],
}: ChapterDetailClientProps) {
  const toggleMutation = useOfflineToggleSubtopic();
  const offlineCompletedIds = useOfflineCompletedIds();
  const [expandedTopics, setExpandedTopics] = useState<Set<string>>(new Set(topics.map((t) => t.id)));

  const completedCount = completedSubtopics.length;
  const progressPct = totalSubtopics > 0 ? Math.round((completedCount / totalSubtopics) * 100) : 0;

  function toggleTopic(topicId: string) {
    setExpandedTopics((prev) => {
      const next = new Set(prev);
      if (next.has(topicId)) {
        next.delete(topicId);
      } else {
        next.add(topicId);
      }
      return next;
    });
  }

  function handleToggleSubtopic(subtopicId: string) {
    toggleMutation.mutate(subtopicId);
  }

  function isCompleted(subtopicId: string) {
    return offlineCompletedIds.has(subtopicId) || completedSubtopics.includes(subtopicId);
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">{chapterName}</h1>
        <div className="mt-2 flex items-center gap-3">
          <Badge variant="secondary">
            {completedCount}/{totalSubtopics} completed
          </Badge>
          <span className="text-sm text-muted-foreground">{progressPct}%</span>
        </div>
        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <div className="space-y-3">
        {topics.map((topic) => {
          const isExpanded = expandedTopics.has(topic.id);
          const topicCompleted = topic.subtopics.filter((s) => isCompleted(s.id)).length;

          return (
            <div key={topic.id} className="rounded-lg border bg-card">
              <button
                className="flex w-full items-center justify-between p-4 text-left"
                onClick={() => toggleTopic(topic.id)}
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium">{topic.name}</span>
                  <Badge variant="outline" className="text-xs">
                    {topicCompleted}/{topic.subtopics.length}
                  </Badge>
                </div>
                <span className="text-xs text-muted-foreground">
                  {isExpanded ? "▼" : "▶"}
                </span>
              </button>

              {isExpanded && (
                <div className="border-t px-4 py-2">
                  <ul className="space-y-2">
                    {topic.subtopics.map((sub) => (
                      <li key={sub.id} className="flex items-center gap-3 py-1">
                        <Switch
                          checked={isCompleted(sub.id)}
                          onCheckedChange={() => handleToggleSubtopic(sub.id)}
                          disabled={toggleMutation.isPending}
                        />
                        <span
                          className={`text-sm ${
                            isCompleted(sub.id)
                              ? "text-muted-foreground line-through"
                              : ""
                          }`}
                        >
                          {sub.name}
                        </span>
                        {sub.estimated_minutes && (
                          <span className="ml-auto text-xs text-muted-foreground">
                            {sub.estimated_minutes} min
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
