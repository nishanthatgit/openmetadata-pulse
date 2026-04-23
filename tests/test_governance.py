"""Tests for governance summary module (P2-03)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from pulse.governance import format_governance_slack, get_governance_summary


# ---------------------------------------------------------------------------
# get_governance_summary tests
# ---------------------------------------------------------------------------


def _make_entity(
    name: str,
    owner: str | None = None,
    tags: list[str] | None = None,
    description: str = "",
) -> dict:
    """Helper to build a fake OM entity dict."""
    entity: dict = {
        "name": name,
        "fullyQualifiedName": f"db.schema.{name}",
        "entityType": "table",
        "description": description,
    }
    if owner:
        entity["owner"] = {"name": owner}
    if tags:
        entity["tags"] = [{"tagFQN": t} for t in tags]
    return entity


class TestGetGovernanceSummary:
    """Tests for governance metric aggregation."""

    @pytest.mark.asyncio
    @patch("pulse.governance.search_metadata", new_callable=AsyncMock)
    async def test_full_coverage(self, mock_search):
        mock_search.return_value = [
            _make_entity("t1", owner="admin", tags=["Tier.Tier1"], description="Table 1"),
            _make_entity("t2", owner="admin", tags=["PII.Sensitive"], description="Table 2"),
            _make_entity("t3", owner="dev", tags=["Classification.Internal"], description="Table 3"),
        ]

        summary = await get_governance_summary()
        assert summary["total_entities"] == 3
        assert summary["owned_count"] == 3
        assert summary["owned_pct"] == 100.0
        assert summary["tagged_count"] == 3
        assert summary["pii_count"] == 1
        assert summary["no_description_count"] == 0
        assert summary["unowned_count"] == 0

    @pytest.mark.asyncio
    @patch("pulse.governance.search_metadata", new_callable=AsyncMock)
    async def test_partial_coverage(self, mock_search):
        mock_search.return_value = [
            _make_entity("t1", owner="admin", tags=["Tier.Tier1"], description="Has desc"),
            _make_entity("t2"),  # no owner, no tags, no desc
            _make_entity("t3", tags=["PII.Email"]),  # has tag but no owner
            _make_entity("t4", owner="dev"),  # has owner but no tags
        ]

        summary = await get_governance_summary()
        assert summary["total_entities"] == 4
        assert summary["owned_count"] == 2
        assert summary["owned_pct"] == 50.0
        assert summary["tagged_count"] == 2
        assert summary["pii_count"] == 1
        assert summary["unowned_count"] == 2
        assert len(summary["unowned_entities"]) == 2

    @pytest.mark.asyncio
    @patch("pulse.governance.search_metadata", new_callable=AsyncMock)
    async def test_empty_catalogue(self, mock_search):
        mock_search.return_value = []

        summary = await get_governance_summary()
        assert summary["total_entities"] == 0
        assert summary["owned_pct"] == 0

    @pytest.mark.asyncio
    @patch("pulse.governance.search_metadata", new_callable=AsyncMock)
    async def test_om_error(self, mock_search):
        mock_search.side_effect = Exception("Connection refused")

        summary = await get_governance_summary()
        assert "error" in summary
        assert summary["total_entities"] == 0


# ---------------------------------------------------------------------------
# format_governance_slack tests
# ---------------------------------------------------------------------------


class TestFormatGovernanceSlack:
    """Tests for Slack formatting of governance summary."""

    def test_healthy_summary(self):
        summary = {
            "total_entities": 50,
            "owned_count": 40,
            "owned_pct": 80.0,
            "unowned_count": 10,
            "tagged_count": 45,
            "tagged_pct": 90.0,
            "pii_count": 5,
            "no_description_count": 3,
            "unowned_entities": ["db.t1", "db.t2"],
            "om_url": "http://localhost:8585",
        }
        text = format_governance_slack(summary)
        assert "Pulse is alive" in text
        assert "50" in text
        assert "80.0%" in text
        assert "✅" in text  # healthy indicators
        assert "db.t1" in text

    def test_unhealthy_summary(self):
        summary = {
            "total_entities": 10,
            "owned_count": 2,
            "owned_pct": 20.0,
            "unowned_count": 8,
            "tagged_count": 1,
            "tagged_pct": 10.0,
            "pii_count": 0,
            "no_description_count": 9,
            "unowned_entities": [],
            "om_url": "http://localhost:8585",
        }
        text = format_governance_slack(summary)
        assert "🔴" in text  # unhealthy indicators

    def test_error_summary(self):
        summary = {"error": "Connection refused", "total_entities": 0}
        text = format_governance_slack(summary)
        assert "Cannot reach" in text
        assert "Connection refused" in text
