import {
  BookOpen,
  LayoutDashboard,
  Settings,
  MessageSquare,
  BarChart3,
  Trophy,
  FileText,
  RotateCw,
  TrendingUp,
  Map,
  Brain,
  Target,
} from "lucide-react";

export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

export const mainNavItems: NavItem[] = [
  { id: "dashboard", label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { id: "syllabus", label: "Syllabus", href: "/syllabus", icon: BookOpen },
  { id: "quiz", label: "Quiz", href: "/quiz", icon: Target },
  { id: "notes", label: "Notes", href: "/notes", icon: FileText },
  { id: "revision", label: "Revision", href: "/revision", icon: RotateCw },
  { id: "chat", label: "AI Chat", href: "/chat", icon: MessageSquare, badge: "AI" },
];

export const secondaryNavItems: NavItem[] = [
  { id: "progress", label: "Progress", href: "/progress", icon: BarChart3 },
  { id: "analytics", label: "Analytics", href: "/analytics", icon: TrendingUp },
  { id: "roadmap", label: "Roadmap", href: "/roadmap", icon: Map },
  { id: "mistake-intelligence", label: "Mistake Intelligence", href: "/mistake-intelligence", icon: Brain },
  { id: "achievements", label: "Achievements", href: "/achievements", icon: Trophy },
  { id: "settings", label: "Settings", href: "/settings", icon: Settings },
];
