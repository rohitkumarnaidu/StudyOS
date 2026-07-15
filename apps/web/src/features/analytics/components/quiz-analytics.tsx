"use client";

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from "recharts";

interface QuizAnalyticsProps {
  data: Array<{ date: string; score: number; question_count: number }>;
}

export function QuizAnalytics({ data }: QuizAnalyticsProps) {
  if (data.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-4">
        <h3 className="mb-4 text-sm font-semibold">Quiz Performance</h3>
        <p className="text-sm text-muted-foreground text-center py-8">
          No quiz data yet. Take a quiz to see your trends.
        </p>
      </div>
    );
  }

  const avgScore = data.reduce((sum, d) => sum + d.score, 0) / data.length;

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold">Quiz Performance</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis dataKey="date" className="text-xs" />
          <YAxis domain={[0, 100]} className="text-xs" />
          <ReferenceLine y={avgScore} stroke="#f59e0b" strokeDasharray="3 3" label={`Avg ${Math.round(avgScore)}%`} />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
            }}
          />
          <Line type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
