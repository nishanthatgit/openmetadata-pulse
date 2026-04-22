"""Unit tests for the Slack bot command dispatcher.

Slack-bolt handlers are tested by simulating command payloads
and verifying the respond() output.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_command(text: str = "") -> dict:
    """Build a minimal Slack slash-command payload."""
    return {
        "command": "/pulse",
        "text": text,
        "user_name": "testuser",
        "user_id": "U12345",
        "channel_id": "C12345",
        "team_id": "T12345",
    }


def _dispatch(text: str) -> str:
    """Call the handler and return what respond() received."""
    from pulse.bot import handle_pulse_command

    ack = MagicMock()
    respond = MagicMock()
    handle_pulse_command(ack, _make_command(text), respond)
    ack.assert_called_once()
    respond.assert_called_once()
    return respond.call_args[0][0]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_help_on_empty_command():
    result = _dispatch("")
    assert "OpenMetadata Pulse" in result
    assert "/pulse health" in result


def test_help_subcommand():
    result = _dispatch("help")
    assert "/pulse ask" in result
    assert "/pulse lineage" in result


def test_unknown_subcommand_shows_help():
    result = _dispatch("foobar")
    assert "Unknown command" in result
    assert "foobar" in result
    assert "/pulse health" in result


def test_ask_without_question():
    result = _dispatch("ask")
    assert "provide a question" in result.lower()


def test_ask_with_question():
    result = _dispatch("ask which tables have PII?")
    assert "which tables have PII?" in result
    assert "Phase 2" in result


def test_lineage_without_entity():
    result = _dispatch("lineage")
    assert "provide an entity" in result.lower()


def test_lineage_with_entity():
    result = _dispatch("lineage sample.public.orders")
    assert "sample.public.orders" in result
    assert "Phase 2" in result


@patch("pulse.bot._run_async")
def test_health_success(mock_run_async):
    mock_run_async.return_value = {"version": "1.4.0"}
    result = _dispatch("health")
    assert "Pulse is alive" in result
    assert "1.4.0" in result


@patch("pulse.bot._run_async")
def test_health_connection_failure(mock_run_async):
    from pulse.exceptions import OMConnectionError
    mock_run_async.side_effect = OMConnectionError(
        "Connection refused", url="http://localhost:8585"
    )
    result = _dispatch("health")
    assert "Cannot reach OpenMetadata" in result
    assert "Connection refused" in result


@patch("pulse.bot._run_async")
def test_health_unexpected_error(mock_run_async):
    mock_run_async.side_effect = RuntimeError("kaboom")
    result = _dispatch("health")
    assert "Something went wrong" in result
    assert "kaboom" in result
