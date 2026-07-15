"use client";

import { ChevronRight, Lightbulb } from "lucide-react";
import { useState } from "react";

interface ConceptNode {
  id: string;
  title: string;
  content?: string;
  formula?: string;
  children?: ConceptNode[];
}

interface StructuredNotesProps {
  data: ConceptNode[];
}

export function StructuredNotes({ data }: StructuredNotesProps) {
  return (
    <div className="space-y-4 p-4">
      {data.map((node) => (
        <ConceptItem key={node.id} node={node} depth={0} />
      ))}
    </div>
  );
}

function ConceptItem({ node, depth }: { node: ConceptNode; depth: number }) {
  const [expanded, setExpanded] = useState(depth < 2);
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className={depth > 0 ? "ml-6 border-l-2 border-border/30 pl-4" : ""}>
      <button
        className="flex w-full items-start gap-2 rounded-md py-2 text-left hover:bg-muted/50"
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        {hasChildren && (
          <ChevronRight
            className="mt-0.5 h-4 w-4 flex-shrink-0 transition-transform text-muted-foreground"
            style={{ transform: expanded ? "rotate(90deg)" : "rotate(0deg)" }}
          />
        )}
        <div className="flex-1">
          <h4 className="text-sm font-medium">{node.title}</h4>
          {node.content && (
            <p className="mt-1 text-xs text-muted-foreground">{node.content}</p>
          )}
          {node.formula && (
            <div className="mt-2 rounded-md bg-muted px-3 py-2 font-mono text-xs">
              {node.formula}
            </div>
          )}
        </div>
      </button>

      {expanded && hasChildren && (
        <div className="space-y-1">
          {node.children!.map((child) => (
            <ConceptItem key={child.id} node={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function KeyConceptsCard({ concepts }: { concepts: string[] }) {
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="h-4 w-4 text-amber-500" />
        <h3 className="text-sm font-semibold">Key Concepts</h3>
      </div>
      <ul className="space-y-2">
        {concepts.map((concept, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary" />
            {concept}
          </li>
        ))}
      </ul>
    </div>
  );
}
