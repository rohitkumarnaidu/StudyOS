"use client";

import { BookOpen, Brain, FileText, Target, TrendingUp, Zap } from "lucide-react";
import Link from "next/link";

interface QuickAction {
  label: string;
  description: string;
  href: string;
  icon: React.ReactNode;
  color: string;
}

const ACTIONS: QuickAction[] = [
  {
    label: "Syllabus",
    description: "Browse chapters and topics",
    href: "/syllabus",
    icon: <BookOpen className="h-5 w-5" />,
    color: "bg-blue-500/10 text-blue-600",
  },
  {
    label: "Revision",
    description: "Spaced repetition review",
    href: "/revision",
    icon: <Brain className="h-5 w-5" />,
    color: "bg-purple-500/10 text-purple-600",
  },
  {
    label: "Notes",
    description: "Upload and study PDFs",
    href: "/notes",
    icon: <FileText className="h-5 w-5" />,
    color: "bg-green-500/10 text-green-600",
  },
  {
    label: "Mistakes",
    description: "Track and analyze errors",
    href: "/mistake-intelligence",
    icon: <Target className="h-5 w-5" />,
    color: "bg-red-500/10 text-red-600",
  },
  {
    label: "Analytics",
    description: "View progress charts",
    href: "/analytics",
    icon: <TrendingUp className="h-5 w-5" />,
    color: "bg-orange-500/10 text-orange-600",
  },
  {
    label: "Chat",
    description: "AI tutor assistance",
    href: "/chat",
    icon: <Zap className="h-5 w-5" />,
    color: "bg-yellow-500/10 text-yellow-600",
  },
];

export function QuickActions() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {ACTIONS.map((action) => (
        <Link
          key={action.href}
          href={action.href}
          className="group rounded-lg border bg-card p-4 transition-colors hover:bg-accent/50 hover:border-accent"
        >
          <div className={`inline-flex rounded-md p-2 ${action.color}`}>
            {action.icon}
          </div>
          <h3 className="mt-3 text-sm font-medium group-hover:text-primary">
            {action.label}
          </h3>
          <p className="mt-1 text-xs text-muted-foreground">
            {action.description}
          </p>
        </Link>
      ))}
    </div>
  );
}
