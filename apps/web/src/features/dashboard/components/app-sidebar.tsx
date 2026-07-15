"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/shared/lib/utils";
import type { NavItem } from "@/features/dashboard/config/navigation";
import { useUiStore } from "@/shared/stores/ui-store";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/shared/components/ui/tooltip";
import { Separator } from "@/shared/components/ui/separator";
import { Button } from "@/shared/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface SidebarProps {
  items: NavItem[];
  secondaryItems?: NavItem[];
}

function SidebarNavItem({ item, collapsed }: { item: NavItem; collapsed: boolean }) {
  const pathname = usePathname();
  const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
  const Icon = item.icon;

  const content = (
    <Link
      href={item.href}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all hover:bg-accent hover:text-accent-foreground",
        isActive ? "bg-accent font-medium text-accent-foreground" : "text-muted-foreground",
        collapsed && "justify-center px-2",
      )}
    >
      <Icon className="h-4 w-4 flex-shrink-0" />
      {!collapsed && <span className="truncate">{item.label}</span>}
      {!collapsed && item.badge && (
        <span className="ml-auto rounded bg-primary px-1.5 py-0.5 text-[10px] font-medium text-primary-foreground">
          {item.badge}
        </span>
      )}
    </Link>
  );

  if (collapsed) {
    return (
      <TooltipProvider delayDuration={0}>
        <Tooltip>
          <TooltipTrigger asChild>{content}</TooltipTrigger>
          <TooltipContent side="right">{item.label}</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    );
  }

  return content;
}

export function AppSidebar({ items, secondaryItems }: SidebarProps) {
  const { sidebarOpen, toggleSidebar } = useUiStore();

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-border bg-card transition-all duration-300",
        sidebarOpen ? "w-64" : "w-16",
      )}
    >
      <div className="flex h-14 items-center justify-between border-b border-border px-4">
        {sidebarOpen && (
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
            <span className="text-lg">StudyOS</span>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          className={cn("h-8 w-8", !sidebarOpen && "mx-auto")}
          onClick={toggleSidebar}
          aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
        >
          {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-3">
        {items.map((item) => (
          <SidebarNavItem key={item.id} item={item} collapsed={!sidebarOpen} />
        ))}
      </nav>

      {secondaryItems && secondaryItems.length > 0 && (
        <>
          <Separator className="mx-3" />
          <nav className="space-y-1 p-3">
            {secondaryItems.map((item) => (
              <SidebarNavItem key={item.id} item={item} collapsed={!sidebarOpen} />
            ))}
          </nav>
        </>
      )}
    </aside>
  );
}
