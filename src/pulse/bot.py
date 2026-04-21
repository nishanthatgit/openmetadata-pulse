"""Slack bot engine using slack-bolt.

Registers /pulse slash commands and dispatches to handlers.
"""

from __future__ import annotations

import structlog
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from pulse.config import settings

logger = structlog.get_logger(__name__)

app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)


@app.command("/pulse")
def handle_pulse_command(ack, command, respond):
    """Entry point for all /pulse commands."""
    ack()
    text = (command.get("text") or "").strip()
    subcommand, _, args = text.partition(" ")
    subcommand = subcommand.lower()

    if subcommand == "health":
        respond(_health_check())
    elif subcommand == "ask":
        respond(f":hourglass_flowing_sand: Processing your query: _{args}_")
        # TODO: wire to query_engine.py
    elif subcommand == "lineage":
        respond(f":hourglass_flowing_sand: Fetching lineage for `{args}` …")
        # TODO: wire to om_client.py
    else:
        respond(
            ":wave: *OpenMetadata Pulse*\n"
            "`/pulse health`  — Check connectivity\n"
            "`/pulse ask <question>`  — AI-powered metadata query\n"
            "`/pulse lineage <entity>`  — Show entity lineage"
        )


def _health_check() -> str:
    """Return a simple health-check message."""
    return f":white_check_mark: Pulse is alive, connected to OM at `{settings.om_server_url}`"


def main() -> None:
    """Start the Slack bot in Socket Mode."""
    logger.info("starting_pulse_bot", om_url=settings.om_server_url)
    handler = SocketModeHandler(app, settings.slack_app_token)
    handler.start()


if __name__ == "__main__":
    main()
