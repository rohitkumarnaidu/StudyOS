"""Semantic clusterer — groups similar mistakes using semantic similarity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class MistakeCluster:
    """A cluster of semantically similar mistakes."""

    cluster_id: str
    theme: str
    mistakes: list[dict[str, Any]] = field(default_factory=list)
    common_concepts: list[str] = field(default_factory=list)
    size: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "theme": self.theme,
            "mistake_count": self.size,
            "common_concepts": self.common_concepts,
            "mistakes": self.mistakes[:5],  # Sample of mistakes
        }


class SemanticClusterer:
    """Groups mistakes into clusters based on semantic similarity using TF-IDF-like approach."""

    def __init__(self) -> None:
        self._mistakes: list[dict[str, Any]] = []
        self._clusters: list[MistakeCluster] = []
        self._cluster_counter = 0

    def add_mistake(
        self,
        mistake_id: str,
        concept_tags: list[str],
        description: str = "",
        mistake_type: str = "",
        profile_id: str = "",
    ) -> None:
        """Add a mistake to be clustered."""
        self._mistakes.append(
            {
                "mistake_id": mistake_id,
                "concept_tags": concept_tags,
                "description": description,
                "mistake_type": mistake_type,
                "profile_id": profile_id,
            }
        )

    def cluster(self, min_cluster_size: int = 2) -> list[MistakeCluster]:
        """Cluster mistakes by concept overlap and semantic similarity."""
        if not self._mistakes:
            return []

        # Build concept-based similarity matrix
        concept_sets = [set(m["concept_tags"]) for m in self._mistakes]
        n = len(self._mistakes)

        # Simple agglomerative clustering based on Jaccard similarity
        visited = [False] * n
        clusters = []

        for i in range(n):
            if visited[i]:
                continue

            cluster_members = [i]
            visited[i] = True

            for j in range(i + 1, n):
                if visited[j]:
                    continue

                similarity = self._jaccard_similarity(concept_sets[i], concept_sets[j])
                if similarity >= 0.3:  # Threshold for clustering
                    cluster_members.append(j)
                    visited[j] = True

            if len(cluster_members) >= min_cluster_size:
                self._cluster_counter += 1
                cluster = self._build_cluster(cluster_members)
                clusters.append(cluster)

        self._clusters = clusters
        return clusters

    def get_cluster_for_mistake(self, mistake_id: str) -> MistakeCluster | None:
        """Find which cluster a specific mistake belongs to."""
        for cluster in self._clusters:
            for m in cluster.mistakes:
                if m["mistake_id"] == mistake_id:
                    return cluster
        return None

    def get_cluster_themes(self) -> list[str]:
        """Get all cluster themes."""
        return [c.theme for c in self._clusters]

    def get_cluster_stats(self) -> dict[str, Any]:
        """Get statistics about clustering results."""
        if not self._clusters:
            return {"total_clusters": 0, "total_mistakes_clustered": 0}

        sizes = [c.size for c in self._clusters]
        return {
            "total_clusters": len(self._clusters),
            "total_mistakes_clustered": sum(sizes),
            "avg_cluster_size": round(sum(sizes) / len(sizes), 2),
            "largest_cluster": max(sizes),
            "smallest_cluster": min(sizes),
        }

    def reset(self) -> None:
        """Clear all mistakes and clusters."""
        self._mistakes.clear()
        self._clusters.clear()
        self._cluster_counter = 0

    @staticmethod
    def _jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set_a and not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0

    def _build_cluster(self, member_indices: list[int]) -> MistakeCluster:
        """Build a cluster from member indices."""
        mistakes = [self._mistakes[i] for i in member_indices]

        # Find common concepts across cluster members
        all_concepts: dict[str, int] = {}
        for m in mistakes:
            for tag in m["concept_tags"]:
                all_concepts[tag] = all_concepts.get(tag, 0) + 1

        # Common concepts appear in >50% of cluster members
        threshold = len(mistakes) * 0.5
        common = [c for c, count in all_concepts.items() if count > threshold]

        # Generate theme from most common concept
        theme = max(all_concepts, key=all_concepts.get) if all_concepts else "mixed"

        return MistakeCluster(
            cluster_id=f"cluster_{self._cluster_counter}",
            theme=theme,
            mistakes=mistakes,
            common_concepts=sorted(common),
            size=len(mistakes),
        )
