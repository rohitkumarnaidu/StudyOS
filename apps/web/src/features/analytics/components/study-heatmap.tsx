"use client";

import { cn } from "@/shared/lib";

interface StudyHeatmapProps {
  data: Array<{ date: string; count: number }>;
}

const intensityColors = [
  "bg-muted/30",
  "bg-emerald-500/20",
  "bg-emerald-500/40",
  "bg-emerald-500/60",
  "bg-emerald-500",
];

function getIntensity(count: number, max: number): number {
  if (count === 0) return 0;
  const ratio = count / Math.max(max, 1);
  if (ratio <= 0.25) return 1;
  if (ratio <= 0.5) return 2;
  if (ratio <= 0.75) return 3;
  return 4;
}

export function StudyHeatmap({ data }: StudyHeatmapProps) {
  if (data.length === 0) return null;

  const maxCount = Math.max(...data.map((d) => d.count));
  const weeks: Array<Array<{ date: string; count: number }>> = [];
  let currentWeek: Array<{ date: string; count: number }> = [];

  for (const day of data) {
    const date = new Date(day.date);
    if (currentWeek.length === 0 && date.getDay() !== 0) {
      for (let i = 0; i < date.getDay(); i++) {
        currentWeek.push({ date: "", count: 0 });
      }
    }
    currentWeek.push(day);
    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }
  if (currentWeek.length > 0) weeks.push(currentWeek);

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold">Study Activity</h3>
      <div className="flex gap-1 overflow-x-auto">
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-1">
            {week.map((day, di) => (
              <div
                key={di}
                className={cn(
                  "h-3 w-3 rounded-sm",
                  day.date
                    ? intensityColors[getIntensity(day.count, maxCount)]
                    : "bg-transparent",
                )}
                title={day.date ? `${day.date}: ${day.count} subtopics` : ""}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center gap-1 text-xs text-muted-foreground">
        <span>Less</span>
        {intensityColors.map((c, i) => (
          <div key={i} className={cn("h-3 w-3 rounded-sm", c)} />
        ))}
        <span>More</span>
      </div>
    </div>
  );
}
