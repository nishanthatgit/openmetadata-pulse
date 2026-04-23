"""Tests for the query engine (P2-01 + P2-04)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pulse.query_engine import _tool_search_metadata, _tool_get_entity_details, _tool_get_entity_lineage, process_query


# ---------------------------------------------------------------------------
# Tool wrapper tests
# ---------------------------------------------------------------------------


class TestToolSearchMetadata:
    """Tests for the search_metadata tool wrapper."""

    @patch("pulse.query_engine.search_metadata", new_callable=AsyncMock)
    def test_returns_json(self, mock_search):
        mock_search.return_value = [
            {
                "name": "customers",
                "fullyQualifiedName": "db.schema.customers",
                "entityType": "table",
                "description": "Customer table",
                "id": "abc-123",
                "owner": {"name": "admin"},
                "tags": [{"tagFQN": "PII.Sensitive"}],
                "columns": [{"name": "id"}, {"name": "email"}],
            }
        ]

        result = _tool_search_metadata("customers")
        assert '"customers"' in result
        assert '"db.schema.customers"' in result
        assert '"PII.Sensitive"' in result

    @patch("pulse.query_engine.search_metadata", new_callable=AsyncMock)
    def test_empty_results(self, mock_search):
        mock_search.return_value = []
        result = _tool_search_metadata("nonexistent")
        assert result == "[]"


class TestToolGetEntityDetails:
    """Tests for the get_entity_details tool wrapper."""

    @patch("pulse.query_engine.get_entity_details", new_callable=AsyncMock)
    def test_returns_formatted_json(self, mock_details):
        mock_details.return_value = {
            "id": "abc-123",
            "name": "customers",
            "fullyQualifiedName": "db.schema.customers",
            "description": "Customer data",
            "owner": {"name": "admin"},
            "tags": [{"tagFQN": "PII.Sensitive"}],
            "columns": [{"name": "id", "dataType": "INT", "description": "Primary key", "tags": []}],
            "followers": [{"id": "user-1"}],
        }

        result = _tool_get_entity_details("table", "db.schema.customers")
        assert '"customers"' in result
        assert '"admin"' in result
        assert '"followerCount": 1' in result


class TestToolGetEntityLineage:
    """Tests for the get_entity_lineage tool wrapper."""

    @patch("pulse.query_engine.get_entity_lineage", new_callable=AsyncMock)
    def test_returns_lineage(self, mock_lineage):
        mock_lineage.return_value = {
            "entity": {"id": "abc-123", "name": "customers", "fullyQualifiedName": "db.customers"},
            "nodes": [
                {"id": "def-456", "name": "raw_customers", "fullyQualifiedName": "raw.customers", "entityType": "table"},
            ],
            "upstreamEdges": [{"fromEntity": "def-456", "toEntity": "abc-123"}],
            "downstreamEdges": [],
        }

        result = _tool_get_entity_lineage("table", "abc-123")
        assert '"raw_customers"' in result
        assert '"upstreamEdges"' in result


# ---------------------------------------------------------------------------
# Agent tests
# ---------------------------------------------------------------------------


class TestProcessQuery:
    """Tests for the main process_query function."""

    @pytest.mark.asyncio
    @patch("pulse.query_engine._get_agent")
    async def test_successful_query(self, mock_get_agent):
        mock_agent = MagicMock()
        from langchain_core.messages import AIMessage
        mock_agent.invoke.return_value = {"messages": [AIMessage(content="Found 5 tables with PII tags.")]}
        mock_get_agent.return_value = mock_agent

        result = await process_query("which tables have PII?")
        assert "5 tables" in result

    @pytest.mark.asyncio
    @patch("pulse.query_engine._get_agent")
    async def test_agent_error(self, mock_get_agent):
        mock_get_agent.side_effect = RuntimeError("OPENAI_API_KEY is not configured")

        result = await process_query("test question")
        assert "Configuration Error" in result

    @pytest.mark.asyncio
    @patch("pulse.query_engine._get_agent")
    async def test_general_exception(self, mock_get_agent):
        mock_agent = MagicMock()
        mock_agent.invoke.side_effect = Exception("LLM timeout")
        mock_get_agent.return_value = mock_agent

        result = await process_query("test question")
        assert "AI Query Error" in result
