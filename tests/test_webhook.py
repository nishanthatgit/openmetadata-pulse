"""Tests for the webhook receiver endpoint."""

import httpx
import pytest
from fastapi import FastAPI
from unittest.mock import AsyncMock, patch

from pulse.server import app
from pulse.webhook_receiver import OMChangeEvent

# ---------------------------------------------------------------------------
# Valid payload helpers
# ---------------------------------------------------------------------------

_VALID_PAYLOADS = [
    {
        "eventType": "entityCreated",
        "entityType": "table",
        "entityFullyQualifiedName": "sample.public.orders",
    },
    {
        "eventType": "entityUpdated",
        "entityType": "topic",
        "entityFullyQualifiedName": "kafka.events",
    },
    {
        "eventType": "entityDeleted",
        "entityType": "dashboard",
        "entityFullyQualifiedName": "superset.revenue",
    },
    {
        "eventType": "entitySoftDeleted",
        "entityType": "pipeline",
        "entityFullyQualifiedName": "airflow.etl_daily",
    },
    {
        "eventType": "testCaseResult",
        "entityType": "testCase",
        "entityFullyQualifiedName": "sample.public.orders.row_count",
    },
]


# ---------------------------------------------------------------------------
# Tests — valid payloads (all 5 event types)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", _VALID_PAYLOADS, ids=[
    p["eventType"] for p in _VALID_PAYLOADS
])
async def test_webhook_accepts_all_event_types(payload):
    """POST /webhook returns 200 for every supported OM event type."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Tests — malformed / invalid payloads → 400
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_webhook_rejects_missing_event_type():
    """Missing required `eventType` returns 400."""
    payload = {"entityType": "table", "entityFullyQualifiedName": "x.y.z"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json=payload)
    assert resp.status_code == 400
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_webhook_rejects_invalid_event_type():
    """An unsupported eventType value returns 400."""
    payload = {
        "eventType": "entityMutated",
        "entityType": "table",
        "entityFullyQualifiedName": "x.y.z",
    }
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json=payload)
    assert resp.status_code == 400
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_webhook_rejects_empty_body():
    """An empty JSON object returns 400."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json={})
    assert resp.status_code == 400
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_webhook_rejects_missing_entity_type():
    """Missing required `entityType` returns 400."""
    payload = {"eventType": "entityCreated"}
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhook", json=payload)
    assert resp.status_code == 400
    assert "detail" in resp.json()


# ---------------------------------------------------------------------------
# Tests — notifier integration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_webhook_passes_event_to_notifier():
    """Valid payload is forwarded to notifier.dispatch_event()."""
    mock_dispatch = AsyncMock()
    payload = {
        "eventType": "entityCreated",
        "entityType": "table",
        "entityFullyQualifiedName": "sample.public.orders",
    }
    with patch("pulse.webhook_receiver.dispatch_event", mock_dispatch):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/webhook", json=payload)

    assert resp.status_code == 200
    mock_dispatch.assert_called_once()
    dispatched = mock_dispatch.call_args[0][0]
    assert dispatched["eventType"] == "entityCreated"
    assert dispatched["entityType"] == "table"
    assert dispatched["entityFullyQualifiedName"] == "sample.public.orders"


@pytest.mark.asyncio
async def test_webhook_preserves_extra_fields():
    """Extra fields from OM are preserved and passed to the notifier."""
    mock_dispatch = AsyncMock()
    payload = {
        "eventType": "entityUpdated",
        "entityType": "table",
        "entityFullyQualifiedName": "db.schema.users",
        "previousVersion": 0.1,
        "currentVersion": 0.2,
    }
    with patch("pulse.webhook_receiver.dispatch_event", mock_dispatch):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/webhook", json=payload)

    assert resp.status_code == 200
    dispatched = mock_dispatch.call_args[0][0]
    assert dispatched["previousVersion"] == 0.1
    assert dispatched["currentVersion"] == 0.2


# ---------------------------------------------------------------------------
# Tests — Pydantic model unit tests
# ---------------------------------------------------------------------------


def test_om_change_event_model_valid():
    """OMChangeEvent accepts a valid payload."""
    event = OMChangeEvent(
        eventType="entityCreated",
        entityType="table",
        entityFullyQualifiedName="sample.public.orders",
    )
    assert event.eventType == "entityCreated"
    assert event.entityType == "table"


def test_om_change_event_model_defaults_fqn():
    """entityFullyQualifiedName defaults to empty string."""
    event = OMChangeEvent(eventType="entityDeleted", entityType="topic")
    assert event.entityFullyQualifiedName == ""


# ---------------------------------------------------------------------------
# Tests — root endpoint (pre-existing)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_root_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "openmetadata-pulse"
