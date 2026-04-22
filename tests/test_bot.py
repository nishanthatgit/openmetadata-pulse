"""Tests for pulse.bot — Slack slash command handlers."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pulse.bot import HELP_TEXT, _handle_ask, _handle_lineage, _health_check, handle_pulse_command


class TestHandlePulseCommand:
    """Test the main /pulse command dispatcher."""

    def _make_command(self, text: str = "") -> dict:
        return {"text": text, "user_id": "U12345", "channel_id": "C12345"}

    def test_health_subcommand(self):
        ack = MagicMock()
        respond = MagicMock()
        command = self._make_command("health")

        with patch("pulse.bot._health_check", return_value=":white_check_mark: OK"):
            handle_pulse_command(ack=ack, command=command, respond=respond)

        ack.assert_called_once()
        respond.assert_called_once_with(":white_check_mark: OK")

    def test_help_subcommand(self):
        ack = MagicMock()
        respond = MagicMock()
        command = self._make_command("help")

        handle_pulse_command(ack=ack, command=command, respond=respond)

        ack.assert_called_once()
        respond.assert_called_once_with(HELP_TEXT)

    def test_unknown_subcommand_shows_help(self):
        ack = MagicMock()
        respond = MagicMock()
        command = self._make_command("foobar")

        handle_pulse_command(ack=ack, command=command, respond=respond)

        ack.assert_called_once()
        respond.assert_called_once_with(HELP_TEXT)

    def test_empty_text_shows_help(self):
        ack = MagicMock()
        respond = MagicMock()
        command = self._make_command("")

        handle_pulse_command(ack=ack, command=command, respond=respond)

        ack.assert_called_once()
        respond.assert_called_once_with(HELP_TEXT)

    def test_ask_subcommand(self):
        ack = MagicMock()
        respond = MagicMock()
        command = self._make_command("ask which tables have no owner?")

        handle_pulse_command(ack=ack, command=command, respond=respond)

        ack.assert_called_once()
        call_args = respond.call_args[0][0]
        assert "Coming Soon" in call_args
        assert "which tables have no owner?" in call_args

    def test_lineage_subcommand(self):
        ack = MagicMock()
        respond = MagicMock()
        command = self._make_command("lineage users_table")

        handle_pulse_command(ack=ack, command=command, respond=respond)

        ack.assert_called_once()
        call_args = respond.call_args[0][0]
        assert "Coming Soon" in call_args
        assert "users_table" in call_args

    def test_error_handling(self):
        ack = MagicMock()
        respond = MagicMock()
        command = self._make_command("health")

        with patch("pulse.bot._health_check", side_effect=RuntimeError("boom")):
            handle_pulse_command(ack=ack, command=command, respond=respond)

        ack.assert_called_once()
        call_args = respond.call_args[0][0]
        assert "Oops" in call_args


class TestHealthCheck:
    """Test the health check function."""

    def test_healthy_response(self):
        with patch("pulse.bot.search_metadata", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [{"_source": {"name": "test"}}]
            result = _health_check()

        assert "✅ Pulse is alive" in result

    def test_unhealthy_response(self):
        with patch("pulse.bot.search_metadata", new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = ConnectionError("Connection refused")
            result = _health_check()

        assert "❌ Cannot reach OpenMetadata" in result


class TestAskHandler:
    """Test the ask placeholder handler."""

    def test_ask_with_question(self):
        respond = MagicMock()
        _handle_ask(respond, "which tables have PII?")
        call_args = respond.call_args[0][0]
        assert "Coming Soon" in call_args
        assert "which tables have PII?" in call_args

    def test_ask_without_question(self):
        respond = MagicMock()
        _handle_ask(respond, "")
        call_args = respond.call_args[0][0]
        assert "warning" in call_args.lower() or "provide" in call_args.lower()


class TestLineageHandler:
    """Test the lineage placeholder handler."""

    def test_lineage_with_entity(self):
        respond = MagicMock()
        _handle_lineage(respond, "users_table")
        call_args = respond.call_args[0][0]
        assert "Coming Soon" in call_args
        assert "users_table" in call_args

    def test_lineage_without_entity(self):
        respond = MagicMock()
        _handle_lineage(respond, "")
        call_args = respond.call_args[0][0]
        assert "warning" in call_args.lower() or "provide" in call_args.lower()
