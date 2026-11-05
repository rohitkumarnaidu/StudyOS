"""Mind map parser — converts mind map PDFs to JSON tree structure."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class MindMapNode:
    """A single node in a mind map tree."""

    id: str
    label: str
    children: list[MindMapNode] = field(default_factory=list)
    level: int = 0
    position: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "level": self.level,
            "position": self.position,
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class MindMapTree:
    """Full mind map tree structure."""

    root: MindMapNode
    total_nodes: int = 0
    max_depth: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": self.root.to_dict(),
            "total_nodes": self.total_nodes,
            "max_depth": self.max_depth,
        }


class MindMapParser:
    """Parse mind map PDFs into structured JSON trees."""

    def __init__(self) -> None:
        pass

    def parse(self, pdf_text: str) -> MindMapTree:
        """Parse mind map from extracted text into a tree structure."""
        root = self._build_tree(pdf_text)
        total_nodes = self._count_nodes(root)
        max_depth = self._get_depth(root)
        return MindMapTree(root=root, total_nodes=total_nodes, max_depth=max_depth)

    def _build_tree(self, text: str) -> MindMapNode:
        """Build a tree from hierarchical text (indentation-based)."""
        lines = [line for line in text.split("\n") if line.strip()]
        if not lines:
            return MindMapNode(id="root", label="Empty Mind Map")

        root = MindMapNode(id="root", label=lines[0].strip(), level=0)
        stack: list[tuple[MindMapNode, int]] = [(root, 0)]

        for line in lines[1:]:
            indent = len(line) - len(line.lstrip())
            level = indent // 2
            label = line.strip()
            if not label:
                continue

            node_id = f"node-{len(label)}-{id(line)}"
            node = MindMapNode(id=node_id, label=label, level=level)

            while stack and stack[-1][1] >= level:
                stack.pop()

            if stack:
                stack[-1][0].children.append(node)

            stack.append((node, level))

        return root

    def _count_nodes(self, node: MindMapNode) -> int:
        """Count total nodes in tree."""
        return 1 + sum(self._count_nodes(c) for c in node.children)

    def _get_depth(self, node: MindMapNode) -> int:
        """Get maximum depth of tree."""
        if not node.children:
            return node.level
        return max(self._get_depth(c) for c in node.children)
