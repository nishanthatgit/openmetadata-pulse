"""Governance summary — aggregates metadata health metrics from OpenMetadata.

Implements P2-03: `/pulse health` upgrade with coverage metrics.
"""

from __future__ import annotations

from typing import Any

import structlog

from pulse.config import settings
from pulse.om_client import search_metadata

logger = structlog.get_logger(__name__)


async def get_governance_summary() -> dict[str, Any]:
    """Query OM and compute governance health metrics.

    Returns a dict with:
        - total_entities: int
        - owned_count / owned_pct: ownership coverage
        - tagged_count / tagged_pct: tag coverage
        - pii_count: entities with PII tags
        - no_description_count: entities missing descriptions
        - unowned_entities: list of unowned entity FQNs (up to 10)
        - om_version: OM server version string (or "unknown")
    """
    logger.info("governance_summary_start")

    try:
        # Fetch a broad set of entities (up to 100)
        entities = await search_metadata("*", limit=100)
    except Exception as exc:
        logger.error("governance_fetch_failed", error=str(exc))
        return {"error": str(exc), "total_entities": 0}

    total = len(entities)
    owned = 0
    tagged = 0
    pii_count = 0
    no_desc = 0
    unowned_list: list[str] = []

    for entity in entities:
        fqn = entity.get("fullyQualifiedName", entity.get("name", "unknown"))

        # Check ownership
        owner = entity.get("owner")
        if owner and isinstance(owner, dict) and owner.get("name"):
            owned += 1
        else:
            if len(unowned_list) < 10:
                unowned_list.append(fqn)

        # Check tags
        tags = entity.get("tags", [])
        if tags:
            tagged += 1
            # Check for PII
            for tag in tags:
                if isinstance(tag, dict):
                    tag_fqn = tag.get("tagFQN", "")
                    if "PII" in tag_fqn or "pii" in tag_fqn or "Sensitive" in tag_fqn:
                        pii_count += 1
                        break

        # Check description
        desc = entity.get("description") or ""
        if not desc.strip():
            no_desc += 1

    summary = {
        "total_entities": total,
        "owned_count": owned,
        "owned_pct": round((owned / total * 100), 1) if total > 0 else 0,
        "unowned_count": total - owned,
        "tagged_count": tagged,
        "tagged_pct": round((tagged / total * 100), 1) if total > 0 else 0,
        "pii_count": pii_count,
        "no_description_count": no_desc,
        "unowned_entities": unowned_list,
        "om_url": settings.om_server_url,
    }

    logger.info("governance_summary_complete", **{k: v for k, v in summary.items() if k != "unowned_entities"})
    return summary


def format_governance_slack(summary: dict[str, Any]) -> str:
    """Format governance summary dict as Slack-readable text.

    Args:
        summary: Dict returned by get_governance_summary().

    Returns:
        Slack-markdown formatted string.
    """
    if "error" in summary:
        return (
            f"❌ Cannot reach OpenMetadata at `{settings.om_server_url}`\n"
            f"_Error: {summary['error']}_"
        )

    total = summary["total_entities"]
    owned = summary["owned_count"]
    owned_pct = summary["owned_pct"]
    tagged = summary["tagged_count"]
    tagged_pct = summary["tagged_pct"]
    pii = summary["pii_count"]
    unowned = summary["unowned_count"]
    no_desc = summary["no_description_count"]

    # Emoji indicators
    own_indicator = "✅" if owned_pct >= 70 else ("⚠️" if owned_pct >= 40 else "🔴")
    tag_indicator = "✅" if tagged_pct >= 70 else ("⚠️" if tagged_pct >= 40 else "🔴")

    lines = [
        f"✅ *Pulse is alive*, connected to OM at `{settings.om_server_url}`\n",
        "📊 *Governance Summary*",
        f"  📋 *Total Entities:* {total}",
        f"  👤 *Ownership:* {owned}/{total} ({owned_pct}%) {own_indicator}",
        f"  🏷️ *Tag Coverage:* {tagged}/{total} ({tagged_pct}%) {tag_indicator}",
        f"  🔒 *PII Tagged:* {pii} entit{'ies' if pii != 1 else 'y'}",
        f"  ❌ *Unowned:* {unowned} entit{'ies' if unowned != 1 else 'y'}",
        f"  📝 *No Description:* {no_desc} entit{'ies' if no_desc != 1 else 'y'}",
    ]

    # Show up to 5 unowned entities
    unowned_list = summary.get("unowned_entities", [])
    if unowned_list:
        lines.append("\n🔎 *Top Unowned Entities:*")
        for fqn in unowned_list[:5]:
            lines.append(f"  • `{fqn}`")

    return "\n".join(lines)
