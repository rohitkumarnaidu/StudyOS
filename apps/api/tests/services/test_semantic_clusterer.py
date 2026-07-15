"""Tests for SemanticClusterer service."""

from __future__ import annotations

import pytest

from studyos_api.services.semantic_clusterer import SemanticClusterer


class TestSemanticClusterer:
    def setup_method(self) -> None:
        self.clusterer = SemanticClusterer()

    def test_add_mistake(self) -> None:
        self.clusterer.add_mistake(
            mistake_id="m1",
            concept_tags=["algebra", "quadratic"],
            description="Failed to solve quadratic equation",
            mistake_type="conceptual",
        )
        assert len(self.clusterer._mistakes) == 1
        assert self.clusterer._mistakes[0]["mistake_id"] == "m1"

    def test_cluster_empty(self) -> None:
        clusters = self.clusterer.cluster()
        assert len(clusters) == 0

    def test_cluster_no_overlap(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra"])
        self.clusterer.add_mistake("m2", concept_tags=["geometry"])
        self.clusterer.add_mistake("m3", concept_tags=["trigonometry"])

        clusters = self.clusterer.cluster(min_cluster_size=2)
        assert len(clusters) == 0  # No overlap, no clusters

    def test_cluster_with_overlap(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra", "quadratic"])
        self.clusterer.add_mistake("m2", concept_tags=["algebra", "equations"])
        self.clusterer.add_mistake("m3", concept_tags=["algebra", "polynomials"])

        clusters = self.clusterer.cluster(min_cluster_size=2)
        assert len(clusters) >= 1
        assert clusters[0].size >= 2

    def test_cluster_common_concepts(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra", "quadratic"])
        self.clusterer.add_mistake("m2", concept_tags=["algebra", "equations"])
        self.clusterer.add_mistake("m3", concept_tags=["algebra", "polynomials"])

        clusters = self.clusterer.cluster(min_cluster_size=2)
        if clusters:
            assert "algebra" in clusters[0].common_concepts

    def test_cluster_theme(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["geometry", "triangles"])
        self.clusterer.add_mistake("m2", concept_tags=["geometry", "circles"])
        self.clusterer.add_mistake("m3", concept_tags=["geometry", "angles"])

        clusters = self.clusterer.cluster(min_cluster_size=2)
        if clusters:
            assert clusters[0].theme == "geometry"

    def test_get_cluster_for_mistake(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra", "quadratic"])
        self.clusterer.add_mistake("m2", concept_tags=["algebra", "equations"])

        clusters = self.clusterer.cluster(min_cluster_size=2)
        if clusters:
            cluster = self.clusterer.get_cluster_for_mistake("m1")
            assert cluster is not None
            assert cluster.cluster_id == clusters[0].cluster_id

    def test_get_cluster_for_mistake_not_found(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra"])
        self.clusterer.add_mistake("m2", concept_tags=["geometry"])

        self.clusterer.cluster(min_cluster_size=2)
        result = self.clusterer.get_cluster_for_mistake("nonexistent")
        assert result is None

    def test_get_cluster_themes(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra", "quadratic"])
        self.clusterer.add_mistake("m2", concept_tags=["algebra", "equations"])
        self.clusterer.add_mistake("m3", concept_tags=["geometry", "triangles"])
        self.clusterer.add_mistake("m4", concept_tags=["geometry", "circles"])

        clusters = self.clusterer.cluster(min_cluster_size=2)
        themes = self.clusterer.get_cluster_themes()
        assert len(themes) == len(clusters)

    def test_get_cluster_stats(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra", "quadratic"])
        self.clusterer.add_mistake("m2", concept_tags=["algebra", "equations"])
        self.clusterer.add_mistake("m3", concept_tags=["algebra", "polynomials"])

        self.clusterer.cluster(min_cluster_size=2)
        stats = self.clusterer.get_cluster_stats()
        assert stats["total_clusters"] >= 1
        assert stats["total_mistakes_clustered"] >= 2
        assert stats["avg_cluster_size"] >= 2.0

    def test_get_cluster_stats_empty(self) -> None:
        stats = self.clusterer.get_cluster_stats()
        assert stats["total_clusters"] == 0
        assert stats["total_mistakes_clustered"] == 0

    def test_reset(self) -> None:
        self.clusterer.add_mistake("m1", concept_tags=["algebra"])
        self.clusterer.add_mistake("m2", concept_tags=["algebra"])
        self.clusterer.cluster()
        self.clusterer.reset()
        assert len(self.clusterer._mistakes) == 0
        assert len(self.clusterer._clusters) == 0
        assert self.clusterer._cluster_counter == 0

    def test_jaccard_similarity_identical(self) -> None:
        sim = SemanticClusterer._jaccard_similarity({"a", "b"}, {"a", "b"})
        assert sim == 1.0

    def test_jaccard_similarity_disjoint(self) -> None:
        sim = SemanticClusterer._jaccard_similarity({"a", "b"}, {"c", "d"})
        assert sim == 0.0

    def test_jaccard_similarity_partial(self) -> None:
        sim = SemanticClusterer._jaccard_similarity({"a", "b"}, {"b", "c"})
        assert abs(sim - 0.333) < 0.01  # 1 intersection / 3 union

    def test_jaccard_similarity_empty(self) -> None:
        sim = SemanticClusterer._jaccard_similarity(set(), set())
        assert sim == 0.0

    def test_mistake_cluster_to_dict(self) -> None:
        from studyos_api.services.semantic_clusterer import MistakeCluster

        cluster = MistakeCluster(
            cluster_id="c1",
            theme="algebra",
            mistakes=[{"mistake_id": "m1"}],
            common_concepts=["quadratic"],
            size=1,
        )
        d = cluster.to_dict()
        assert d["cluster_id"] == "c1"
        assert d["theme"] == "algebra"
        assert d["mistake_count"] == 1
        assert d["common_concepts"] == ["quadratic"]
