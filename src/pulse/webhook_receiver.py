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
