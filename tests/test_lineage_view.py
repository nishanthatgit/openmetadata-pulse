"""Tests for lineage_view module (P2-02)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from pulse.lineage_view import _build_adjacency, _entity_type_emoji, _render_tree, get_lineage_blocks


# ---------------------------------------------------------------------------
# Unit tests for helpers
# ---------------------------------------------------------------------------


class TestBuildAdjacency:
    """Tests for edge → adjacency conversion."""

    def test_upstream_direction(self):
        edges = [
            {"fromEntity": "child-1", "toEntity": "parent-1"},
            {"fromEntity": "child-2", "toEntity": "parent-1"},
        ]
        adj = _build_adjacency(edges, "upstream")
        assert "parent-1" in adj
        assert set(adj["parent-1"]) == {"child-1", "child-2"}

    def test_downstream_direction(self):
        edges = [
            {"fromEntity": "parent-1", "toEntity": "child-1"},
            {"fromEntity": "parent-1", "toEntity": "child-2"},
        ]
        adj = _build_adjacency(edges, "downstream")
        assert "parent-1" in adj
        assert set(adj["parent-1"]) == {"child-1", "child-2"}

    def test_empty_edges(self):
        adj = _build_adjacency([], "upstream")
        assert adj == {}


class TestRenderTree:
    """Tests for tree rendering."""

    def test_simple_tree(self):
        adj = {"root": ["child-1", "child-2"]}
        node_map = {
            "child-1": {"fullyQualifiedName": "db.raw_table", "entityType": "table"},
            "child-2": {"fullyQualifiedName": "db.staging_table", "entityType": "table"},
        }
        lines = _render_tree("root", adj, node_map)
        assert len(lines) == 2
        assert "db.raw_table" in lines[0]
        assert "db.staging_table" in lines[1]

    def test_nested_tree(self):
        adj = {"root": ["mid"], "mid": ["leaf"]}
        node_map = {
            "mid": {"fullyQualifiedName": "middle", "entityType": "table"},
            "leaf": {"fullyQualifiedName": "leaf_table", "entityType": "table"},
        }
        lines = _render_tree("root", adj, node_map)
        assert len(lines) == 2
        assert "middle" in lines[0]
        assert "leaf_table" in lines[1]

    def test_max_depth(self):
        adj = {"a": ["b"], "b": ["c"], "c": ["d"], "d": ["e"]}
        node_map = {k: {"name": k, "entityType": "table"} for k in "bcde"}
        lines = _render_tree("a", adj, node_map, max_depth=2)
        # Should stop at depth 2 — only b, c, d shown
        assert len(lines) <= 3

    def test_cycle_protection(self):
        adj = {"a": ["b"], "b": ["a"]}
        node_map = {
            "a": {"name": "A", "entityType": "table"},
            "b": {"name": "B", "entityType": "table"},
        }
        lines = _render_tree("a", adj, node_map)
        # Should not loop infinitely
        assert len(lines) == 2


class TestEntityTypeEmoji:
    """Tests for entity type emoji mapping."""

    def test_known_types(self):
        assert _entity_type_emoji("table") == "📋"
        assert _entity_type_emoji("dashboard") == "📊"
        assert _entity_type_emoji("pipeline") == "⚙️"

    def test_unknown_type(self):
        assert _entity_type_emoji("custom_thing") == "📄"


# ---------------------------------------------------------------------------
# Integration tests (mocked OM calls)
# ---------------------------------------------------------------------------


class TestGetLineageBlocks:
    """Tests for the main get_lineage_blocks function."""

    @pytest.mark.asyncio
    @patch("pulse.lineage_view.get_entity_lineage", new_callable=AsyncMock)
    @patch("pulse.lineage_view.search_metadata", new_callable=AsyncMock)
    async def test_successful_lineage(self, mock_search, mock_lineage):
        mock_search.return_value = [
            {"id": "abc-123", "fullyQualifiedName": "db.customers", "entityType": "table", "name": "customers"}
        ]
        mock_lineage.return_value = {
            "entity": {"id": "abc-123", "name": "customers", "fullyQualifiedName": "db.customers"},
            "nodes": [
                {"id": "def-456", "name": "raw_customers", "fullyQualifiedName": "raw.customers", "entityType": "table"},
            ],
            "upstreamEdges": [{"fromEntity": "def-456", "toEntity": "abc-123"}],
            "downstreamEdges": [],
        }

        blocks = await get_lineage_blocks("customers")
        assert len(blocks) > 0
        # Should have header block
        assert blocks[0]["type"] == "header"
        assert "Lineage" in blocks[0]["text"]["text"]

    @pytest.mark.asyncio
    @patch("pulse.lineage_view.search_metadata", new_callable=AsyncMock)
    async def test_entity_not_found(self, mock_search):
        mock_search.return_value = []
        blocks = await get_lineage_blocks("nonexistent")
        assert len(blocks) == 1
        assert "No entity found" in blocks[0]["text"]["text"]

    @pytest.mark.asyncio
    @patch("pulse.lineage_view.get_entity_lineage", new_callable=AsyncMock)
    @patch("pulse.lineage_view.search_metadata", new_callable=AsyncMock)
    async def test_no_lineage(self, mock_search, mock_lineage):
        mock_search.return_value = [
            {"id": "abc-123", "fullyQualifiedName": "db.isolated_table", "entityType": "table", "name": "isolated"}
        ]
        mock_lineage.return_value = {
            "entity": {"id": "abc-123", "name": "isolated", "fullyQualifiedName": "db.isolated_table"},
            "nodes": [],
            "upstreamEdges": [],
            "downstreamEdges": [],
        }

        blocks = await get_lineage_blocks("isolated")
        # Should still render, just with "no dependencies" messages
        text_content = str(blocks)
        assert "No upstream" in text_content or "No downstream" in text_content

    @pytest.mark.asyncio
    @patch("pulse.lineage_view.search_metadata", new_callable=AsyncMock)
    async def test_search_error(self, mock_search):
        mock_search.side_effect = Exception("Connection refused")
        blocks = await get_lineage_blocks("customers")
        assert "Could not search" in blocks[0]["text"]["text"]
