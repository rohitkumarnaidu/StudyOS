"use client";

import { useCallback, useState } from "react";
import { Button } from "@/shared/components/ui/button";
import { ZoomIn, ZoomOut, Maximize } from "lucide-react";

interface MindMapNode {
  id: string;
  label: string;
  children?: MindMapNode[];
  color?: string;
}

interface MindMapViewerProps {
  data: MindMapNode;
}

export function MindMapViewer({ data }: MindMapViewerProps) {
  const [zoom, setZoom] = useState(100);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  }, [pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  }, [dragging, dragStart]);

  const handleMouseUp = useCallback(() => {
    setDragging(false);
  }, []);

  function renderNode(node: MindMapNode, depth: number = 0) {
    const colors = [
      "bg-primary text-primary-foreground",
      "bg-blue-500/10 text-blue-600",
      "bg-emerald-500/10 text-emerald-600",
      "bg-amber-500/10 text-amber-600",
      "bg-purple-500/10 text-purple-600",
    ];
    const colorClass = colors[depth % colors.length];

    return (
      <div key={node.id} className="flex flex-col items-start">
        <div
          className={`rounded-lg px-3 py-2 text-sm font-medium ${colorClass} border border-border/50`}
        >
          {node.label}
        </div>
        {node.children && node.children.length > 0 && (
          <div className="ml-6 mt-2 flex flex-col gap-2 border-l-2 border-border/30 pl-4">
            {node.children.map((child) => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-muted/20">
      <div className="flex items-center justify-end gap-2 border-b border-border bg-background px-4 py-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setZoom((z) => Math.max(50, z - 25))}
          aria-label="Zoom out"
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
        <span className="text-xs tabular-nums w-10 text-center">{zoom}%</span>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setZoom((z) => Math.min(200, z + 25))}
          aria-label="Zoom in"
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" aria-label="Fullscreen">
          <Maximize className="h-4 w-4" />
        </Button>
      </div>

      <div
        className="flex-1 overflow-auto p-8 cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom / 100})`,
            transformOrigin: "top left",
          }}
        >
          {renderNode(data)}
        </div>
      </div>
    </div>
  );
}
