"""Tests for the notification engine."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from pulse.notifier import (
    EVENT_EMOJI,
    _build_om_url,
    _format_slack_blocks,
    _humanize_event_type,
    dispatch_event,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def test_humanize_entity_created():
    assert _humanize_event_type("entityCreated") == "Entity Created"


def test_humanize_entity_updated():
    assert _humanize_event_type("entityUpdated") == "Entity Updated"


def test_humanize_entity_deleted():
    assert _humanize_event_type("entityDeleted") == "Entity Deleted"


def test_humanize_entity_soft_deleted():
    assert _humanize_event_type("entitySoftDeleted") == "Entity Soft Deleted"


def test_humanize_test_case_result():
    assert _humanize_event_type("testCaseResult") == "Test Case Result"


def test_build_om_url():
    with patch("pulse.notifier.settings") as mock_settings:
        mock_settings.om_server_url = "http://localhost:8585"
        url = _build_om_url("table", "sample.public.orders")
    assert url == "http://localhost:8585/table/sample.public.orders"


def test_build_om_url_strips_trailing_slash():
    with patch("pulse.notifier.settings") as mock_settings:
        mock_settings.om_server_url = "http://localhost:8585/"
        url = _build_om_url("topic", "kafka.events")
    assert url == "http://localhost:8585/topic/kafka.events"


# ---------------------------------------------------------------------------
# Block Kit structure tests
# ---------------------------------------------------------------------------


def _make_blocks(
    event_type: str = "entityCreated",
    entity_type: str = "table",
    fqn: str = "sample.public.orders",
) -> list[dict]:
    emoji = EVENT_EMOJI.get(event_type, ":bell:")
    with patch("pulse.notifier.settings") as mock_settings:
        mock_settings.om_server_url = "http://localhost:8585"
        return _format_slack_blocks(emoji, event_type, entity_type, fqn)


def test_format_blocks_returns_four_blocks():
    """Block Kit output must contain header, section, context, actions."""
    blocks = _make_blocks()
    assert len(blocks) == 4


def test_format_blocks_header_type():
    blocks = _make_blocks()
    assert blocks[0]["type"] == "header"


def test_format_blocks_header_contains_emoji_and_event():
    blocks = _make_blocks(event_type="entityCreated")
    header_text = blocks[0]["text"]["text"]
    assert ":new:" in header_text
    assert "Entity Created" in header_text


def test_format_blocks_section_contains_entity_type():
    blocks = _make_blocks(entity_type="table")
    section_text = blocks[1]["text"]["text"]
    assert "`table`" in section_text


def test_format_blocks_section_contains_fqn_link():
    blocks = _make_blocks(fqn="sample.public.orders")
    section_text = blocks[1]["text"]["text"]
    assert "sample.public.orders" in section_text
    assert "http://localhost:8585/table/sample.public.orders" in section_text


def test_format_blocks_context_contains_timestamp_and_event_type():
    blocks = _make_blocks(event_type="entityUpdated")
    ctx_text = blocks[2]["elements"][0]["text"]
    assert ":clock1:" in ctx_text
    assert "`entityUpdated`" in ctx_text


def test_format_blocks_actions_has_view_button():
    blocks = _make_blocks()
    actions = blocks[3]
    assert actions["type"] == "actions"
    btn = actions["elements"][0]
    assert btn["text"]["text"] == "View in OpenMetadata"
    assert "http://localhost:8585/table/sample.public.orders" in btn["url"]


@pytest.mark.parametrize(
    "event_type,expected_emoji",
    [
        ("entityCreated", ":new:"),
        ("entityUpdated", ":pencil2:"),
        ("entityDeleted", ":wastebasket:"),
        ("entitySoftDeleted", ":ghost:"),
        ("testCaseResult", ":test_tube:"),
    ],
    ids=["created", "updated", "deleted", "soft_deleted", "test_result"],
)
def test_format_blocks_all_event_types_have_correct_emoji(event_type, expected_emoji):
    blocks = _make_blocks(event_type=event_type)
    header_text = blocks[0]["text"]["text"]
    assert expected_emoji in header_text


# ---------------------------------------------------------------------------
# dispatch_event() — Slack posting tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_event_calls_slack_post_message():
    """dispatch_event() posts to Slack when a token is configured."""
    mock_client = MagicMock()
    mock_client.chat_postMessage = MagicMock()

    with patch("pulse.notifier._get_slack_client", return_value=mock_client), \
         patch("pulse.notifier.settings") as mock_settings:
        mock_settings.slack_bot_token = "xoxb-test-token"
        mock_settings.slack_default_channel = "#test-channel"
        mock_settings.om_server_url = "http://localhost:8585"

        await dispatch_event({
            "eventType": "entityCreated",
            "entityType": "table",
            "entityFullyQualifiedName": "sample.public.orders",
        })

    mock_client.chat_postMessage.assert_called_once()
    call_kwargs = mock_client.chat_postMessage.call_args
    assert call_kwargs.kwargs["channel"] == "#test-channel"
    assert isinstance(call_kwargs.kwargs["blocks"], list)
    assert len(call_kwargs.kwargs["blocks"]) == 4
    assert "Entity Created" in call_kwargs.kwargs["text"]


@pytest.mark.asyncio
async def test_dispatch_event_handles_slack_api_error():
    """dispatch_event() logs but does not crash on SlackApiError."""
    mock_client = MagicMock()
    error_response = MagicMock()
    error_response.data = {"ok": False, "error": "channel_not_found"}
    mock_client.chat_postMessage.side_effect = SlackApiError(
        message="channel_not_found", response=error_response
    )

    with patch("pulse.notifier._get_slack_client", return_value=mock_client), \
         patch("pulse.notifier.settings") as mock_settings:
        mock_settings.slack_bot_token = "xoxb-test-token"
        mock_settings.slack_default_channel = "#nonexistent"
        mock_settings.om_server_url = "http://localhost:8585"

        # Should NOT raise — graceful handling
        await dispatch_event({
            "eventType": "entityDeleted",
            "entityType": "dashboard",
            "entityFullyQualifiedName": "superset.revenue",
        })


@pytest.mark.asyncio
async def test_dispatch_event_skips_when_no_token():
    """dispatch_event() warns and skips when no Slack token is set."""
    with patch("pulse.notifier._get_slack_client", return_value=None), \
         patch("pulse.notifier.settings") as mock_settings:
        mock_settings.om_server_url = "http://localhost:8585"

        # Should NOT raise — just log a warning
        await dispatch_event({
            "eventType": "entityUpdated",
            "entityType": "topic",
            "entityFullyQualifiedName": "kafka.events",
        })


@pytest.mark.asyncio
async def test_dispatch_event_uses_correct_emoji_for_event_type():
    """dispatch_event() uses the correct emoji in the fallback text."""
    mock_client = MagicMock()
    mock_client.chat_postMessage = MagicMock()

    with patch("pulse.notifier._get_slack_client", return_value=mock_client), \
         patch("pulse.notifier.settings") as mock_settings:
        mock_settings.slack_bot_token = "xoxb-test"
        mock_settings.slack_default_channel = "#ch"
        mock_settings.om_server_url = "http://localhost:8585"

        await dispatch_event({
            "eventType": "testCaseResult",
            "entityType": "testCase",
            "entityFullyQualifiedName": "db.table.row_count",
        })

    call_kwargs = mock_client.chat_postMessage.call_args
    assert ":test_tube:" in call_kwargs.kwargs["text"]
