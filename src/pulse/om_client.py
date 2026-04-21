"""OpenMetadata MCP client wrapper using data-ai-sdk.

Provides typed helpers around search_metadata, get_entity_details,
and get_entity_lineage.
"""

from __future__ import annotations

from typing import Any

import httpx
import structlog

from pulse.config import settings

logger = structlog.get_logger(__name__)


async def search_metadata(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search OM for entities matching *query*."""
    url = f"{settings.om_server_url}/api/v1/search/query"
    params = {"q": query, "size": limit}
    headers = {"Authorization": f"Bearer {settings.om_api_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    hits = data.get("hits", {}).get("hits", [])
    logger.info("search_metadata", query=query, hits=len(hits))
    return hits


async def get_entity_details(entity_type: str, fqn: str) -> dict[str, Any]:
    """Fetch full details for a single OM entity."""
    url = f"{settings.om_server_url}/api/v1/{entity_type}/name/{fqn}"
    headers = {"Authorization": f"Bearer {settings.om_api_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
    logger.info("get_entity_details", entity_type=entity_type, fqn=fqn)
    return resp.json()


async def get_entity_lineage(entity_type: str, entity_id: str) -> dict[str, Any]:
    """Fetch lineage graph for an entity."""
    url = f"{settings.om_server_url}/api/v1/lineage/{entity_type}/{entity_id}"
    headers = {"Authorization": f"Bearer {settings.om_api_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
    logger.info("get_entity_lineage", entity_type=entity_type, entity_id=entity_id)
    return resp.json()
