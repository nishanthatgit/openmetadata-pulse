"""Tests for the notification engine dispatcher."""

from unittest.mock import MagicMock, patch

import pytest
from slack_sdk.errors import SlackApiError

from pulse.notifier import dispatch_event

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
            "owner": {"name": "Test Owner"},
        })

    mock_client.chat_postMessage.assert_called_once()
    call_kwargs = mock_client.chat_postMessage.call_args
    assert call_kwargs.kwargs["channel"] == "#test-channel"
    assert isinstance(call_kwargs.kwargs["blocks"], list)
    assert len(call_kwargs.kwargs["blocks"]) > 0
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
