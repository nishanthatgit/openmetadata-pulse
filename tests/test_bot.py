"""Unit tests for the Slack bot command dispatcher.

Slack-bolt handlers are tested by simulating command payloads
and verifying the respond() output.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

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
# Help & unknown commands
# ---------------------------------------------------------------------------


def test_empty_command_shows_help():
    """No subcommand should display the help text."""
    result = _dispatch("")
    assert "OpenMetadata Pulse" in result
    assert "/pulse health" in result
    assert "/pulse ask" in result
    assert "/pulse lineage" in result


def test_help_subcommand():
    """Explicit /pulse help should display help text."""
    result = _dispatch("help")
    assert "/pulse health" in result
    assert "/pulse ask" in result
    assert "/pulse lineage" in result


def test_unknown_subcommand_shows_help():
    """Unknown commands should show error + help text."""
    result = _dispatch("foobar")
    assert "Unknown command" in result
    assert "foobar" in result
    assert "/pulse health" in result  # help text included


# ---------------------------------------------------------------------------
# /pulse ask
# ---------------------------------------------------------------------------


def test_ask_without_question():
    """ask with no question should prompt the user."""
    result = _dispatch("ask")
    assert "provide a question" in result.lower()


def test_ask_empty_whitespace():
    """ask with only whitespace should prompt the user."""
    result = _dispatch("ask   ")
    assert "provide a question" in result.lower()


def test_ask_with_question_shows_placeholder():
    """ask with a question should acknowledge and show Phase 2 placeholder."""
    result = _dispatch("ask which tables have PII?")
    assert "which tables have PII?" in result
    assert "Phase 2" in result


# ---------------------------------------------------------------------------
# /pulse lineage
# ---------------------------------------------------------------------------


def test_lineage_without_entity():
    """lineage with no entity should prompt the user."""
    result = _dispatch("lineage")
    assert "provide an entity" in result.lower()


def test_lineage_empty_whitespace():
    """lineage with only whitespace should prompt the user."""
    result = _dispatch("lineage   ")
    assert "provide an entity" in result.lower()


def test_lineage_with_entity_shows_placeholder():
    """lineage with an entity FQN should acknowledge and show Phase 2 placeholder."""
    result = _dispatch("lineage sample.public.orders")
    assert "sample.public.orders" in result
    assert "Phase 2" in result


# ---------------------------------------------------------------------------
# /pulse health
# ---------------------------------------------------------------------------


@patch("pulse.bot._run_async")
def test_health_success(mock_run_async):
    """health should show success when OM is reachable."""
    mock_run_async.return_value = {"version": "1.4.0"}
    result = _dispatch("health")
    assert "Pulse is alive" in result
    assert "1.4.0" in result


@patch("pulse.bot._run_async")
def test_health_connection_failure(mock_run_async):
    """health should show error when OM is unreachable."""
    from pulse.exceptions import OMConnectionError
    mock_run_async.side_effect = OMConnectionError(
        "Connection refused", url="http://localhost:8585"
    )
    result = _dispatch("health")
    assert "Cannot reach OpenMetadata" in result
    assert "Connection refused" in result


@patch("pulse.bot._run_async")
def test_health_api_error(mock_run_async):
    """health should show warning when OM returns an API error."""
    from pulse.exceptions import OMClientError
    mock_run_async.side_effect = OMClientError(
        "Internal Server Error", status_code=500, url="http://localhost:8585"
    )
    result = _dispatch("health")
    assert "responded with an error" in result
    assert "500" in result


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@patch("pulse.bot._run_async")
def test_unexpected_error_caught_gracefully(mock_run_async):
    """Unexpected exceptions should be caught and shown as friendly messages."""
    mock_run_async.side_effect = RuntimeError("kaboom")
    result = _dispatch("health")
    assert "Something went wrong" in result
    assert "kaboom" in result
    assert "RuntimeError" in result


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------


def test_subcommand_case_insensitive():
    """Subcommands should be case-insensitive."""
    result = _dispatch("HELP")
    assert "/pulse health" in result

    result2 = _dispatch("Health")
    # Should not crash — either shows health result or error, not "unknown"
    assert "Unknown command" not in result2
