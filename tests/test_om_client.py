"""Unit tests for the OM client wrapper.

All external HTTP calls are mocked via respx.
"""

import pytest
import respx
from httpx import Response

from pulse.exceptions import (
    OMAuthError,
    OMClientError,
    OMConnectionError,
    OMNotFoundError,
)
from pulse.om_client import (
    check_health,
    get_entity_details,
    get_entity_lineage,
    search_metadata,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

OM_BASE = "http://localhost:8585"


@pytest.fixture(autouse=True)
def _patch_settings(monkeypatch):
    """Point the client at a local test URL."""
    monkeypatch.setenv("OM_SERVER_URL", OM_BASE)
    monkeypatch.setenv("OM_API_TOKEN", "test-token")
    # Force settings reload
    from pulse.config import Settings
    import pulse.om_client as mod
    import pulse.config
    pulse.config.settings = Settings()
    mod.settings = pulse.config.settings


# ---------------------------------------------------------------------------
# check_health
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_check_health_success():
    respx.get(f"{OM_BASE}/api/v1/system/version").mock(
        return_value=Response(200, json={"version": "1.4.0"})
    )
    result = await check_health()
    assert result["version"] == "1.4.0"


@respx.mock
@pytest.mark.asyncio
async def test_check_health_unreachable():
    import httpx as _httpx
    respx.get(f"{OM_BASE}/api/v1/system/version").mock(
        side_effect=_httpx.ConnectError("refused")
    )
    with pytest.raises(OMConnectionError):
        await check_health()


# ---------------------------------------------------------------------------
# search_metadata
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_search_metadata_returns_hits():
    payload = {
        "hits": {
            "total": {"value": 2},
            "hits": [
                {"_source": {"id": "1", "name": "orders"}},
                {"_source": {"id": "2", "name": "users"}},
            ],
        }
    }
    respx.get(f"{OM_BASE}/api/v1/search/query").mock(
        return_value=Response(200, json=payload)
    )
    hits = await search_metadata("table", limit=5)
    assert len(hits) == 2
    assert hits[0]["name"] == "orders"


@respx.mock
@pytest.mark.asyncio
async def test_search_metadata_empty():
    payload = {"hits": {"total": {"value": 0}, "hits": []}}
    respx.get(f"{OM_BASE}/api/v1/search/query").mock(
        return_value=Response(200, json=payload)
    )
    hits = await search_metadata("nonexistent")
    assert hits == []


@respx.mock
@pytest.mark.asyncio
async def test_search_metadata_auth_error():
    respx.get(f"{OM_BASE}/api/v1/search/query").mock(
        return_value=Response(401, text="Unauthorized")
    )
    with pytest.raises(OMAuthError):
        await search_metadata("table")


# ---------------------------------------------------------------------------
# get_entity_details
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_get_entity_details_success():
    entity = {"id": "abc-123", "name": "orders", "fullyQualifiedName": "sample.public.orders"}
    respx.get(f"{OM_BASE}/api/v1/table/name/sample.public.orders").mock(
        return_value=Response(200, json=entity)
    )
    result = await get_entity_details("table", "sample.public.orders")
    assert result["id"] == "abc-123"
    assert result["fullyQualifiedName"] == "sample.public.orders"


@respx.mock
@pytest.mark.asyncio
async def test_get_entity_details_not_found():
    respx.get(f"{OM_BASE}/api/v1/table/name/does.not.exist").mock(
        return_value=Response(404, text="Not Found")
    )
    with pytest.raises(OMNotFoundError):
        await get_entity_details("table", "does.not.exist")


# ---------------------------------------------------------------------------
# get_entity_lineage
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_get_entity_lineage_success():
    lineage = {
        "entity": {"id": "abc-123"},
        "nodes": [{"id": "n1"}, {"id": "n2"}],
        "downstreamEdges": [{"fromEntity": "abc-123", "toEntity": "n1"}],
        "upstreamEdges": [{"fromEntity": "n2", "toEntity": "abc-123"}],
    }
    respx.get(f"{OM_BASE}/api/v1/lineage/table/abc-123").mock(
        return_value=Response(200, json=lineage)
    )
    result = await get_entity_lineage("table", "abc-123")
    assert len(result["nodes"]) == 2
    assert len(result["downstreamEdges"]) == 1


# ---------------------------------------------------------------------------
# Retry behaviour
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_retry_on_503_then_success(monkeypatch):
    """Client should retry on 503 and succeed on the next attempt."""
    import pulse.om_client as mod
    monkeypatch.setattr(mod, "_RETRY_BACKOFF_BASE", 0.01)  # speed up test

    route = respx.get(f"{OM_BASE}/api/v1/system/version")
    route.side_effect = [
        Response(503, text="Service Unavailable"),
        Response(200, json={"version": "1.4.0"}),
    ]
    result = await check_health()
    assert result["version"] == "1.4.0"
    assert route.call_count == 2


@respx.mock
@pytest.mark.asyncio
async def test_retry_exhausted_raises(monkeypatch):
    """After all retries exhausted, the last error should propagate."""
    import pulse.om_client as mod
    monkeypatch.setattr(mod, "_RETRY_BACKOFF_BASE", 0.01)
    monkeypatch.setattr(mod, "_MAX_RETRIES", 2)

    respx.get(f"{OM_BASE}/api/v1/system/version").mock(
        return_value=Response(503, text="down")
    )
    with pytest.raises(OMClientError):
        await check_health()


# ---------------------------------------------------------------------------
# Auth header injection
# ---------------------------------------------------------------------------


@respx.mock
@pytest.mark.asyncio
async def test_auth_header_sent():
    """Verify the Bearer token is included in requests."""
    route = respx.get(f"{OM_BASE}/api/v1/system/version").mock(
        return_value=Response(200, json={"version": "1.4.0"})
    )
    await check_health()
    request = route.calls[0].request
    assert request.headers["Authorization"] == "Bearer test-token"
