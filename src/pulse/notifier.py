"""Smart notification router — formats OM events as Slack Block Kit messages."""

from __future__ import annotations

from typing import Any

import structlog
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from pulse.config import settings
from pulse.resilience import error_envelope, is_retryable_slack_error, slack_breaker
from pulse.templates import EVENT_EMOJI, _humanize_event_type, route_payload_to_template

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Resilient Helpers
# ---------------------------------------------------------------------------

@slack_breaker
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.5, min=1, max=10),
    retry=retry_if_exception(is_retryable_slack_error),
    reraise=True,
)
def _post_slack_message(
    client: WebClient,
    channel: str,
    blocks: list[dict[str, Any]],
    text: str,
) -> None:
    client.chat_postMessage(channel=channel, blocks=blocks, text=text)


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
# Smart Routing Mapping
# ---------------------------------------------------------------------------

OWNER_SLACK_MAP = {
    # OM User Name -> Slack Channel / User ID
    "nishanthatgit": "#data-engineering",
    "Chellammal-K": "#data-science",
    "admin": "#admin-alerts",
}

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

    blocks = route_payload_to_template(payload)
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
    owner_data = payload.get("entity", {}).get("owner", {})
    
    if owner_data:
        owner_name = owner_data.get("name")
        if owner_name and owner_name in OWNER_SLACK_MAP:
            channel = OWNER_SLACK_MAP[owner_name]
            logger.info("smart_routing", owner=owner_name, channel=channel)

    try:
        _post_slack_message(client, channel, blocks, fallback_text)
        logger.info(
            "slack_message_posted",
            channel=channel,
            event_type=event_type,
            fqn=entity_fqn,
        )
    except SlackApiError as exc:
        error_envelope(
            "slack_dispatch",
            exc,
            channel=channel,
            event_type=event_type,
            fqn=entity_fqn,
            response=str(exc.response.data) if exc.response else None,
        )
    except Exception as exc:
        error_envelope(
            "slack_dispatch",
            exc,
            channel=channel,
            event_type=event_type,
            fqn=entity_fqn,
        )
