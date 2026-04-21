"""Smart notification router — formats OM events as Slack Block Kit messages."""

from __future__ import annotations

from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Event type → emoji mapping
EVENT_EMOJI: dict[str, str] = {
    "entityCreated": ":new:",
    "entityUpdated": ":pencil2:",
    "entityDeleted": ":wastebasket:",
    "entitySoftDeleted": ":ghost:",
    "testCaseResult": ":test_tube:",
}


async def dispatch_event(payload: dict[str, Any]) -> None:
    """Route an OM change event to the appropriate Slack channel."""
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    entity_fqn = payload.get("entityFullyQualifiedName", "")
    emoji = EVENT_EMOJI.get(event_type, ":bell:")

    logger.info(
        "dispatch_event",
        event_type=event_type,
        entity_type=entity_type,
        fqn=entity_fqn,
    )

    # TODO P1-08: post to Slack via slack_sdk.WebClient
    _ = _format_slack_blocks(emoji, event_type, entity_type, entity_fqn)


def _format_slack_blocks(
    emoji: str, event_type: str, entity_type: str, fqn: str
) -> list[dict[str, Any]]:
    """Build Slack Block Kit blocks for a change event."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{event_type}* on `{entity_type}`: `{fqn}`",
            },
        },
    ]
