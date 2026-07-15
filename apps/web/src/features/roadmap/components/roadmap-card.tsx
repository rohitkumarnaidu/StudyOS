"use client";

import { useState } from "react";
import { cn } from "@/shared/lib/utils";
import { Badge } from "@/shared/components/ui/badge";
import { Checkbox } from "@/shared/components/ui/checkbox";
import {
  Calendar,
  Clock,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  AlertCircle,
  Timer,
  BookOpen,
  Target,
} from "lucide-react";

export interface ChapterItem {
  id: string;
  name: string;
  completed: boolean;
  estimatedMinutes: number;
}

export interface SubjectGroup {
  name: string;
  chapters: ChapterItem[];
}

export interface RoadmapCardProps {
  date: string;
  dayNumber: number;
  subjects: SubjectGroup[];
  priorityScore: number;
  status: "completed" | "in-progress" | "upcoming" | "missed";
  onChapterToggle?: (chapterId: string) => void;
}

const statusConfig = {
  completed: {
    icon: CheckCircle2,
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/30",
    label: "Completed",
  },
  "in-progress": {
    icon: AlertCircle,
    color: "text-amber-500",
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    label: "In Progress",
  },
  upcoming: {
    icon: Timer,
    color: "text-blue-500",
    bg: "bg-blue-500/10",
    border: "border-blue-500/30",
    label: "Upcoming",
  },
  missed: {
    icon: AlertCircle,
    color: "text-destructive",
    bg: "bg-destructive/10",
    border: "border-destructive/30",
    label: "Missed",
  },
};

function getPriorityLabel(score: number): { label: string; variant: "default" | "secondary" | "destructive" } {
  if (score >= 80) return { label: "High", variant: "destructive" };
  if (score >= 50) return { label: "Medium", variant: "secondary" };
  return { label: "Low", variant: "default" };
}

function formatMinutes(minutes: number): string {
  if (minutes >= 60) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  }
  return `${minutes}m`;
}

export function RoadmapCard({
  date,
  dayNumber,
  subjects,
  priorityScore,
  status,
  onChapterToggle,
}: RoadmapCardProps) {
  const [expanded, setExpanded] = useState(status === "in-progress");

  const statusCfg = statusConfig[status];
  const StatusIcon = statusCfg.icon;
  const priority = getPriorityLabel(priorityScore);

  const totalChapters = subjects.reduce((sum, s) => sum + s.chapters.length, 0);
  const completedChapters = subjects.reduce(
    (sum, s) => sum + s.chapters.filter((c) => c.completed).length,
    0,
  );
  const totalMinutes = subjects.reduce(
    (sum, s) => sum + s.chapters.reduce((s2, c) => s2 + c.estimatedMinutes, 0),
    0,
  );

  const progressPct = totalChapters > 0 ? (completedChapters / totalChapters) * 100 : 0;

  const formattedDate = new Date(date).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card transition-all duration-200",
        statusCfg.border,
        status === "completed" && "opacity-70",
      )}
    >
      {/* Header */}
      <button
        className="flex w-full items-center justify-between p-4 text-left hover:bg-muted/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-3">
          <div className={cn("flex h-8 w-8 items-center justify-center rounded-full", statusCfg.bg)}>
            <StatusIcon className={cn("h-4 w-4", statusCfg.color)} />
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">Day {dayNumber}</span>
              <Badge variant={priority.variant} className="text-[10px] px-1.5 py-0">
                {priority.label}
              </Badge>
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {formattedDate}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatMinutes(totalMinutes)}
              </span>
              <span className="flex items-center gap-1">
                <BookOpen className="h-3 w-3" />
                {completedChapters}/{totalChapters}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Progress bar */}
          <div className="hidden sm:block h-1.5 w-20 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full rounded-full bg-primary transition-all duration-300"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="border-t border-border px-4 pb-4">
          {subjects.map((subject) => (
            <div key={subject.name} className="mt-3">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-3.5 w-3.5 text-muted-foreground" />
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  {subject.name}
                </span>
              </div>
              <div className="space-y-1.5 ml-5">
                {subject.chapters.map((chapter) => (
                  <div
                    key={chapter.id}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-2 py-1.5 text-sm transition-colors",
                      chapter.completed && "opacity-60",
                    )}
                  >
                    <Checkbox
                      checked={chapter.completed}
                      onCheckedChange={() => onChapterToggle?.(chapter.id)}
                      disabled={status === "completed" || status === "missed"}
                      className="h-4 w-4"
                    />
                    <span
                      className={cn(
                        "flex-1",
                        chapter.completed && "line-through text-muted-foreground",
                      )}
                    >
                      {chapter.name}
                    </span>
                    <span className="text-xs text-muted-foreground tabular-nums">
                      {chapter.estimatedMinutes}m
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Summary footer */}
          <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground pt-3 border-t border-border">
            <span>
              {progressPct === 100
                ? "All done!"
                : `${totalChapters - completedChapters} chapters remaining`}
            </span>
            <span>{formatMinutes(totalMinutes)} total</span>
          </div>
        </div>
      )}
    </div>
  );
}
