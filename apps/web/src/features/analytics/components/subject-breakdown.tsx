"use client";

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";

interface SubjectBreakdownProps {
  data: Array<{ name: string; completed: number; total: number; percentage: number }>;
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444", "#06b6d4"];

export function SubjectBreakdown({ data }: SubjectBreakdownProps) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <h3 className="mb-4 text-sm font-semibold">Subject Breakdown</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
          <XAxis dataKey="name" className="text-xs" tick={{ fontSize: 11 }} />
          <YAxis className="text-xs" />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Bar dataKey="percentage" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-4 space-y-2">
        {data.map((subject, i) => (
          <div key={subject.name} className="flex items-center gap-3">
            <div className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
            <span className="flex-1 text-sm">{subject.name}</span>
            <span className="text-xs text-muted-foreground">
              {subject.completed}/{subject.total} ({subject.percentage}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
