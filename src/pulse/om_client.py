"""OpenMetadata API client with retry, timeout, and structured error handling.

Provides typed async helpers around the OM REST API:
- ``search_metadata``  — full-text entity search
- ``get_entity_details``  — fetch single entity by FQN
- ``get_entity_lineage``  — fetch lineage graph for an entity
- ``check_health``  — verify OM server connectivity

All functions use *httpx* with configurable timeout and automatic
retry on transient (5xx / timeout) errors.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
import structlog

from pulse.config import settings
from pulse.exceptions import (
    OMAuthError,
    OMClientError,
    OMConnectionError,
    OMNotFoundError,
)

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_TIMEOUT = httpx.Timeout(connect=5.0, read=15.0, write=10.0, pool=5.0)
_MAX_RETRIES = 3
_RETRY_BACKOFF_BASE = 0.5  # seconds
_RETRYABLE_STATUS_CODES = {502, 503, 504}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _base_url() -> str:
    return settings.om_server_url.rstrip("/")


def _auth_headers() -> dict[str, str]:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if settings.om_api_token:
        headers["Authorization"] = f"Bearer {settings.om_api_token}"
    return headers


def _raise_for_status(response: httpx.Response, url: str) -> None:
    """Map HTTP error codes to typed exceptions."""
    code = response.status_code
    if 200 <= code < 300:
        return

    detail = response.text[:500]

    if code in (401, 403):
        raise OMAuthError(detail, status_code=code, url=url)
    if code == 404:
        raise OMNotFoundError(detail, status_code=code, url=url)
    raise OMClientError(detail, status_code=code, url=url)


async def _request_with_retry(
    method: str,
    url: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> httpx.Response:
    """Execute an HTTP request with exponential-backoff retry on transient errors."""
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.request(
                    method,
                    url,
                    headers=_auth_headers(),
                    params=params,
                    json=json_body,
                )

            if response.status_code not in _RETRYABLE_STATUS_CODES:
                _raise_for_status(response, url)
                return response

            last_exc = OMClientError(
                response.text[:500],
                status_code=response.status_code,
                url=url,
            )
            logger.warning(
                "om_request_retryable",
                attempt=attempt,
                status=response.status_code,
                url=url,
            )

        except httpx.ConnectError as exc:
            last_exc = OMConnectionError(
                f"Cannot connect to OpenMetadata at {url}: {exc}",
                url=url,
            )
            logger.warning("om_connect_error", attempt=attempt, url=url, error=str(exc))

        except httpx.TimeoutException as exc:
            last_exc = OMConnectionError(
                f"Timeout connecting to OpenMetadata at {url}: {exc}",
                url=url,
            )
            logger.warning("om_timeout", attempt=attempt, url=url, error=str(exc))

        if attempt < _MAX_RETRIES:
            wait = _RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            await asyncio.sleep(wait)

    # All retries exhausted
    assert last_exc is not None
    raise last_exc


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def check_health() -> dict[str, Any]:
    """Verify connectivity to the OM server.

    Returns the OM version payload on success.
    Raises ``OMConnectionError`` if the server is unreachable.
    """
    url = f"{_base_url()}/api/v1/system/version"
    logger.info("om_health_check", url=url)
    response = await _request_with_retry("GET", url)
    data: dict[str, Any] = response.json()
    logger.info("om_health_ok", version=data.get("version", "unknown"))
    return data


async def search_metadata(
    query: str,
    *,
    limit: int = 10,
    index: str = "table_search_index",
) -> list[dict[str, Any]]:
    """Search OM for entities matching *query*.

    Args:
        query: Free-text search query.
        limit: Maximum number of results.
        index: OM search index to query.

    Returns:
        List of hit source dicts from the OM search response.
    """
    url = f"{_base_url()}/api/v1/search/query"
    params = {"q": query, "size": limit, "index": index}

    logger.info("om_search", query=query, limit=limit, index=index)
    response = await _request_with_retry("GET", url, params=params)
    data = response.json()

    hits_raw = data.get("hits", {}).get("hits", [])
    hits = [h.get("_source", h) for h in hits_raw]
    total = data.get("hits", {}).get("total", {}).get("value", len(hits))

    logger.info("om_search_results", query=query, total=total, returned=len(hits))
    return hits


async def get_entity_details(
    entity_type: str,
    fqn: str,
    *,
    fields: str = "owner,tags,followers,tier",
) -> dict[str, Any]:
    """Fetch full details for a single OM entity by FQN.

    Args:
        entity_type: OM entity type (e.g. ``table``, ``topic``, ``dashboard``).
        fqn: Fully-qualified name of the entity.
        fields: Comma-separated list of fields to include.

    Returns:
        Entity detail dict.

    Raises:
        OMNotFoundError: If the entity does not exist.
    """
    url = f"{_base_url()}/api/v1/{entity_type}/name/{fqn}"
    params = {"fields": fields}

    logger.info("om_get_entity", entity_type=entity_type, fqn=fqn)
    response = await _request_with_retry("GET", url, params=params)
    entity: dict[str, Any] = response.json()

    logger.info(
        "om_entity_fetched",
        entity_type=entity_type,
        fqn=fqn,
        entity_id=entity.get("id", "unknown"),
    )
    return entity


async def get_entity_lineage(
    entity_type: str,
    entity_id: str,
    *,
    upstream_depth: int = 3,
    downstream_depth: int = 3,
) -> dict[str, Any]:
    """Fetch lineage graph for an entity.

    Args:
        entity_type: OM entity type.
        entity_id: UUID of the entity.
        upstream_depth: How many levels upstream to traverse.
        downstream_depth: How many levels downstream to traverse.

    Returns:
        Lineage graph dict with ``nodes`` and ``edges``.
    """
    url = f"{_base_url()}/api/v1/lineage/{entity_type}/{entity_id}"
    params = {
        "upstreamDepth": upstream_depth,
        "downstreamDepth": downstream_depth,
    }

    logger.info("om_get_lineage", entity_type=entity_type, entity_id=entity_id)
    response = await _request_with_retry("GET", url, params=params)
    lineage: dict[str, Any] = response.json()

    node_count = len(lineage.get("nodes", []))
    edge_count = len(lineage.get("downstreamEdges", [])) + len(
        lineage.get("upstreamEdges", [])
    )
    logger.info(
        "om_lineage_fetched",
        entity_id=entity_id,
        nodes=node_count,
        edges=edge_count,
    )
    return lineage
