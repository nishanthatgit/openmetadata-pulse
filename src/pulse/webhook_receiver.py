"""FastAPI webhook receiver for OpenMetadata change events."""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import APIRouter, Request

from pulse.notifier import dispatch_event

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/webhook")
async def receive_webhook(request: Request) -> dict[str, str]:
    """Accept an OM change-event webhook payload."""
    payload: dict[str, Any] = await request.json()
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    logger.info("webhook_received", event_type=event_type, entity_type=entity_type)

    await dispatch_event(payload)
    return {"status": "ok"}
