"""Lineage tree viewer for Slack — renders entity lineage as indented text.

Implements P2-02: `/pulse lineage <entity>` → upstream/downstream tree in Slack.
"""

from __future__ import annotations

from typing import Any

import structlog

from pulse.config import settings
from pulse.om_client import get_entity_details, get_entity_lineage, search_metadata

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Tree rendering
# ---------------------------------------------------------------------------


def _build_adjacency(edges: list[dict[str, Any]], direction: str) -> dict[str, list[str]]:
    """Build parent→children adjacency map from lineage edges.

    Args:
        edges: List of edge dicts with 'fromEntity' and 'toEntity' UUIDs.
        direction: 'upstream' or 'downstream'.

    Returns:
        Dict mapping entity ID → list of connected entity IDs.
    """
    adj: dict[str, list[str]] = {}
    for edge in edges:
        if direction == "upstream":
            parent = edge.get("toEntity", "")
            child = edge.get("fromEntity", "")
        else:
            parent = edge.get("fromEntity", "")
            child = edge.get("toEntity", "")
        adj.setdefault(parent, []).append(child)
    return adj


def _render_tree(
    node_id: str,
    adj: dict[str, list[str]],
    node_map: dict[str, dict[str, Any]],
    depth: int = 0,
    max_depth: int = 3,
    visited: set[str] | None = None,
) -> list[str]:
    """Recursively render a lineage tree as indented text lines.

    Args:
        node_id: Current node UUID.
        adj: Adjacency map from _build_adjacency.
        node_map: Maps entity ID → entity metadata dict.
        depth: Current recursion depth.
        max_depth: Maximum depth to render.
        visited: Set of already-visited node IDs (prevents cycles).

    Returns:
        List of indented text lines.
    """
    if visited is None:
        visited = set()
    if node_id in visited or depth > max_depth:
        return []
    visited.add(node_id)

    lines: list[str] = []
    children = adj.get(node_id, [])
    for i, child_id in enumerate(children):
        node_info = node_map.get(child_id, {})
        name = node_info.get("fullyQualifiedName") or node_info.get("name", child_id[:8])
        entity_type = node_info.get("entityType", "entity")

        # Use tree characters
        is_last = i == len(children) - 1
        prefix = "  " * depth
        connector = "└─" if is_last else "├─"
        type_emoji = _entity_type_emoji(entity_type)

        lines.append(f"{prefix}{connector} {type_emoji} `{name}`")
        lines.extend(
            _render_tree(child_id, adj, node_map, depth + 1, max_depth, visited)
        )
    return lines


def _entity_type_emoji(entity_type: str) -> str:
    """Map entity type to a suitable emoji."""
    mapping = {
        "table": "📋",
        "topic": "📨",
        "dashboard": "📊",
        "pipeline": "⚙️",
        "mlmodel": "🤖",
        "container": "📦",
        "searchIndex": "🔍",
        "storedProcedure": "🗃️",
        "databaseService": "🗄️",
        "database": "🗄️",
        "databaseSchema": "📂",
    }
    return mapping.get(entity_type, "📄")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def get_lineage_blocks(entity_name: str) -> list[dict[str, Any]]:
    """Search for an entity and render its lineage as Slack Block Kit blocks.

    Args:
        entity_name: Entity name or FQN to look up lineage for.

    Returns:
        List of Slack Block Kit block dicts.
    """
    logger.info("lineage_lookup_start", entity=entity_name)

    # Step 1: Search for the entity
    try:
        results = await search_metadata(entity_name, limit=5)
    except Exception as exc:
        logger.error("lineage_search_failed", entity=entity_name, error=str(exc))
        return _error_blocks(f"Could not search for `{entity_name}`: {type(exc).__name__}")

    if not results:
        return _error_blocks(f"No entity found matching `{entity_name}`.")

    # Pick the best match (first result)
    entity = results[0]
    entity_id = entity.get("id", "")
    entity_fqn = entity.get("fullyQualifiedName", entity.get("name", entity_name))
    entity_type = entity.get("entityType", "table")

    if not entity_id:
        return _error_blocks(f"Entity `{entity_fqn}` has no ID — cannot fetch lineage.")

    # Step 2: Fetch lineage
    try:
        lineage = await get_entity_lineage(entity_type, entity_id)
    except Exception as exc:
        logger.error("lineage_fetch_failed", entity=entity_fqn, error=str(exc))
        return _error_blocks(f"Could not fetch lineage for `{entity_fqn}`: {type(exc).__name__}")

    # Step 3: Build node map
    node_map: dict[str, dict[str, Any]] = {}
    for node in lineage.get("nodes", []):
        nid = node.get("id", "")
        if nid:
            node_map[nid] = node
    # Add the root entity itself
    root_entity = lineage.get("entity", {})
    root_id = root_entity.get("id", entity_id)
    node_map[root_id] = root_entity

    # Step 4: Render upstream tree
    upstream_edges = lineage.get("upstreamEdges", [])
    upstream_adj = _build_adjacency(upstream_edges, "upstream")
    upstream_lines = _render_tree(root_id, upstream_adj, node_map)

    # Step 5: Render downstream tree
    downstream_edges = lineage.get("downstreamEdges", [])
    downstream_adj = _build_adjacency(downstream_edges, "downstream")
    downstream_lines = _render_tree(root_id, downstream_adj, node_map)

    # Step 6: Build Slack blocks
    type_emoji = _entity_type_emoji(entity_type)
    om_url = f"{settings.om_server_url.rstrip('/')}/{entity_type}/{entity_fqn}"

    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🔗 Lineage: {entity_fqn}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{type_emoji} *Entity:* <{om_url}|{entity_fqn}>\n*Type:* `{entity_type}`",
            },
        },
        {"type": "divider"},
    ]

    # Upstream section
    if upstream_lines:
        upstream_text = "\n".join(upstream_lines)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"⬆️ *Upstream* ({len(upstream_edges)} edge{'s' if len(upstream_edges) != 1 else ''})\n{upstream_text}",
            },
        })
    else:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "⬆️ *Upstream*\n_No upstream dependencies found._"},
        })

    blocks.append({"type": "divider"})

    # Downstream section
    if downstream_lines:
        downstream_text = "\n".join(downstream_lines)
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"⬇️ *Downstream* ({len(downstream_edges)} edge{'s' if len(downstream_edges) != 1 else ''})\n{downstream_text}",
            },
        })
    else:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "⬇️ *Downstream*\n_No downstream dependencies found._"},
        })

    # Summary
    total_nodes = len(node_map) - 1  # exclude root
    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": f"📊 {total_nodes} connected entit{'ies' if total_nodes != 1 else 'y'} | ⬆️ {len(upstream_edges)} upstream | ⬇️ {len(downstream_edges)} downstream",
        }],
    })

    logger.info(
        "lineage_lookup_complete",
        entity=entity_fqn,
        upstream=len(upstream_edges),
        downstream=len(downstream_edges),
        nodes=total_nodes,
    )
    return blocks


def _error_blocks(message: str) -> list[dict[str, Any]]:
    """Return a simple error block for Slack."""
    return [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f":warning: {message}"},
        }
    ]
