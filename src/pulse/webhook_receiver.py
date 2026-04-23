"""FastAPI webhook receiver for OpenMetadata change events."""

from __future__ import annotations

from typing import Any, Literal

import structlog
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from pulse.notifier import dispatch_event
from pulse.resilience import error_envelope

logger = structlog.get_logger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Pydantic model for OM change-event payloads
# ---------------------------------------------------------------------------

SUPPORTED_EVENT_TYPES = (
    "entityCreated",
    "entityUpdated",
    "entityDeleted",
    "entitySoftDeleted",
    "testCaseResult",
)


class OMChangeEvent(BaseModel, extra="allow"):
    """Typed model for an OpenMetadata change-event webhook payload.

    ``extra='allow'`` ensures forward-compatibility: any additional
    fields that OM sends in future versions are preserved and passed
    downstream without breaking validation.
    """

    eventType: Literal[
        "entityCreated",
        "entityUpdated",
        "entityDeleted",
        "entitySoftDeleted",
        "testCaseResult",
    ]
    entityType: str
    entityFullyQualifiedName: str = ""


# ---------------------------------------------------------------------------
# Event Filtering Engine
# ---------------------------------------------------------------------------

FILTER_RULES = {
    "tier1_only": False,
    "skip_ingestion_bot": True,
    "skip_passing_dq": True,
}


def should_dispatch(payload: dict[str, Any]) -> bool:
    """Evaluate filtering rules to determine if an event should be dispatched."""
    if FILTER_RULES.get("skip_ingestion_bot"):
        if payload.get("updatedBy") == "ingestion-bot":
            logger.info("event_filtered", reason="ingestion_bot")
            return False

    if FILTER_RULES.get("skip_passing_dq"):
        if payload.get("eventType") == "testCaseResult":
            status = payload.get("testCaseResult", {}).get("testCaseStatus")
            if status == "Success":
                logger.info("event_filtered", reason="passing_dq")
                return False

    if FILTER_RULES.get("tier1_only"):
        tags = payload.get("entity", {}).get("tags", [])
        has_tier1 = any(tag.get("tagFQN", "").startswith("Tier.Tier1") for tag in tags)
        if not has_tier1:
            logger.info("event_filtered", reason="not_tier1")
            return False

    return True


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------


@router.post("/webhook")
async def receive_webhook(request: Request) -> dict[str, str]:
    """Accept an OM change-event webhook payload.

    Returns 200 on success, 400 on malformed / invalid payload.
    """
    body: dict[str, Any] = await request.json()

    try:
        event = OMChangeEvent(**body)
    except ValidationError as exc:
        logger.warning("webhook_validation_error", errors=exc.errors())
        return JSONResponse(  # type: ignore[return-value]
            status_code=400,
            content={"detail": exc.errors()},
        )

    logger.info(
        "webhook_received",
        event_type=event.eventType,
        entity_type=event.entityType,
        fqn=event.entityFullyQualifiedName,
    )

    if not should_dispatch(body):
        return {"status": "ignored"}

    try:
        await dispatch_event(event.model_dump())
    except Exception as exc:
        error_envelope(
            "webhook_processing",
            exc,
            event_type=event.eventType,
            fqn=event.entityFullyQualifiedName,
        )
        return JSONResponse(  # type: ignore[return-value]
            status_code=500,
            content={"detail": "Internal server error during dispatch"},
        )

    return {"status": "ok"}
