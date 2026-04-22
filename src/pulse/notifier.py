"""Smart notification router — formats OM events as Slack Block Kit messages."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from pulse.config import settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Slack client (lazy — only created when a valid token is configured)
# ---------------------------------------------------------------------------

_slack_client: WebClient | None = None


def _get_slack_client() -> WebClient | None:
    """Return a Slack WebClient if a bot token is configured, else None."""
    global _slack_client  # noqa: PLW0603
    if _slack_client is not None:
        return _slack_client
    if settings.slack_bot_token:
        _slack_client = WebClient(token=settings.slack_bot_token)
        return _slack_client
    return None


# ---------------------------------------------------------------------------
# Event type → emoji mapping
# ---------------------------------------------------------------------------

EVENT_EMOJI: dict[str, str] = {
    "entityCreated": ":new:",
    "entityUpdated": ":pencil2:",
    "entityDeleted": ":wastebasket:",
    "entitySoftDeleted": ":ghost:",
    "testCaseResult": ":test_tube:",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _humanize_event_type(event_type: str) -> str:
    """Convert camelCase event type to a human-readable title.

    Example: ``entityCreated`` → ``Entity Created``
    """
    # Insert a space before each uppercase letter, then title-case
    spaced = re.sub(r"([A-Z])", r" \1", event_type).strip()
    return spaced.title()


def _build_om_url(entity_type: str, fqn: str) -> str:
    """Construct a deep-link URL to an entity in the OpenMetadata UI."""
    base = settings.om_server_url.rstrip("/")
    return f"{base}/{entity_type}/{fqn}"


# ---------------------------------------------------------------------------
# Block Kit builder
# ---------------------------------------------------------------------------


def _format_slack_blocks(
    emoji: str, event_type: str, entity_type: str, fqn: str
) -> list[dict[str, Any]]:
    """Build rich Slack Block Kit blocks for a change event.

    Layout:
        1. Header  — emoji + human-readable event title
        2. Section — entity details with clickable OM deep-link
        3. Context — timestamp + event-type badge
        4. Actions — "View in OpenMetadata" button
    """
    human_event = _humanize_event_type(event_type)
    om_url = _build_om_url(entity_type, fqn)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    blocks: list[dict[str, Any]] = [
        # 1. Header
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {human_event}",
                "emoji": True,
            },
        },
        # 2. Section — entity info with deep-link
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Entity Type:* `{entity_type}`\n"
                    f"*FQN:* <{om_url}|{fqn}>"
                ),
            },
        },
        # 3. Context — timestamp + badge
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f":clock1: {now}  |  `{event_type}`",
                },
            ],
        },
        # 4. Actions — View in OM button
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View in OpenMetadata",
                        "emoji": True,
                    },
                    "url": om_url,
                    "action_id": "view_in_om",
                },
            ],
        },
    ]

    return blocks


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------


async def dispatch_event(payload: dict[str, Any]) -> None:
    """Route an OM change event to the configured Slack channel.

    Posts a rich Block Kit message via ``slack_sdk.WebClient``.
    Gracefully handles Slack API failures by logging and continuing.
    """
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

    blocks = _format_slack_blocks(emoji, event_type, entity_type, entity_fqn)
    fallback_text = f"{emoji} {_humanize_event_type(event_type)} on {entity_type}: {entity_fqn}"

    client = _get_slack_client()
    if client is None:
        logger.warning(
            "slack_post_skipped",
            reason="No SLACK_BOT_TOKEN configured — message not sent",
            event_type=event_type,
            fqn=entity_fqn,
        )
        return

    channel = settings.slack_default_channel

    try:
        client.chat_postMessage(
            channel=channel,
            blocks=blocks,
            text=fallback_text,
        )
        logger.info(
            "slack_message_posted",
            channel=channel,
            event_type=event_type,
            fqn=entity_fqn,
        )
    except SlackApiError as exc:
        logger.error(
            "slack_post_failed",
            channel=channel,
            event_type=event_type,
            fqn=entity_fqn,
            error=str(exc),
            response=str(exc.response.data) if exc.response else None,
        )
