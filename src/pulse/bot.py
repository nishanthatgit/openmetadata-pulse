"""Slack bot engine using slack-bolt.

Registers /pulse slash commands and dispatches to handlers.
Subcommands:
  - health  — verify OM connectivity
  - ask     — AI-powered metadata query (Phase 2)
  - lineage — entity lineage lookup (Phase 2)
  - help    — show available commands
"""

from __future__ import annotations

import traceback
from typing import Any

import structlog
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from pulse.config import settings
from pulse.om_client import search_metadata

logger = structlog.get_logger(__name__)

app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)

# ---------------------------------------------------------------------------
# Help text (reused by /pulse help and unknown subcommands)
# ---------------------------------------------------------------------------
HELP_TEXT = (
    ":zap: *OpenMetadata Pulse — Commands*\n\n"
    "`/pulse health`  — Check OM connectivity status\n"
    "`/pulse ask <question>`  — AI-powered metadata query _(coming soon)_\n"
    "`/pulse lineage <entity>`  — Show entity lineage _(coming soon)_\n"
    "`/pulse help`  — Show this help message"
)


# ---------------------------------------------------------------------------
# Slash-command handler
# ---------------------------------------------------------------------------
@app.command("/pulse")
def handle_pulse_command(ack, command, respond):  # noqa: ANN001
    """Entry point for all /pulse commands."""
    ack()

    text: str = (command.get("text") or "").strip()
    subcommand, _, args = text.partition(" ")
    subcommand = subcommand.lower()
    user_id: str = command.get("user_id", "unknown")

    logger.info(
        "pulse_command_received",
        user=user_id,
        subcommand=subcommand or "(empty)",
        args=args,
    )

    try:
        if subcommand == "health":
            respond(_health_check())
        elif subcommand == "ask":
            _handle_ask(respond, args)
        elif subcommand == "lineage":
            _handle_lineage(respond, args)
        elif subcommand == "help":
            respond(HELP_TEXT)
        else:
            # Unknown or empty subcommand → show help
            respond(HELP_TEXT)
    except Exception:
        error_msg = traceback.format_exc()
        logger.error("pulse_command_error", user=user_id, subcommand=subcommand, error=error_msg)
        respond(
            ":x: *Oops!* Something went wrong processing your command.\n"
            "Please try again or contact the Pulse team."
        )


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------
def _health_check() -> str:
    """Verify OM connectivity by attempting a search API call."""
    import asyncio

    logger.info("health_check_start", om_url=settings.om_server_url)

    try:
        # Run the async search_metadata in a sync context
        loop: asyncio.AbstractEventLoop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None  # type: ignore[assignment]

        if loop and loop.is_running():
            # If there's already a running loop, create a new thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                results: list[dict[str, Any]] = pool.submit(
                    asyncio.run, search_metadata("*", limit=1)
                ).result(timeout=10)
        else:
            results = asyncio.run(search_metadata("*", limit=1))

        logger.info("health_check_success", om_url=settings.om_server_url, hits=len(results))
        return (
            f":white_check_mark: *Pulse is healthy!*\n"
            f"• Connected to OpenMetadata at `{settings.om_server_url}`\n"
            f"• Search API responding — {len(results)} result(s) returned"
        )
    except Exception as exc:
        logger.error("health_check_failed", om_url=settings.om_server_url, error=str(exc))
        return (
            f":x: *OM connectivity issue*\n"
            f"• Cannot reach OpenMetadata at `{settings.om_server_url}`\n"
            f"• Error: `{exc!s}`\n"
            f"• Check that OM is running and `OM_SERVER_URL` / `OM_API_TOKEN` are correct."
        )


def _handle_ask(respond, args: str) -> None:  # noqa: ANN001
    """Placeholder for AI-powered metadata query (Phase 2)."""
    if not args.strip():
        respond(":warning: Please provide a question. Usage: `/pulse ask <question>`")
        return
    logger.info("ask_placeholder", question=args)
    respond(
        f":hourglass_flowing_sand: *AI Query — Coming Soon!*\n"
        f"Your question: _{args}_\n\n"
        f"This feature will use GPT-4o-mini + OpenMetadata MCP tools to "
        f"answer natural-language metadata queries."
    )


def _handle_lineage(respond, args: str) -> None:  # noqa: ANN001
    """Placeholder for entity lineage lookup (Phase 2)."""
    if not args.strip():
        respond(":warning: Please provide an entity name. Usage: `/pulse lineage <entity>`")
        return
    logger.info("lineage_placeholder", entity=args)
    respond(
        f":hourglass_flowing_sand: *Lineage — Coming Soon!*\n"
        f"Entity: `{args}`\n\n"
        f"This feature will show the upstream/downstream lineage graph "
        f"for the specified entity."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Start the Slack bot in Socket Mode."""
    logger.info("starting_pulse_bot", om_url=settings.om_server_url)
    handler = SocketModeHandler(app, settings.slack_app_token)
    handler.start()


if __name__ == "__main__":
    main()
