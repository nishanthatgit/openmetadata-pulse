"""Slack bot engine using slack-bolt.

Registers /pulse slash commands and dispatches to handlers.
Subcommands:
  - health  — OM connectivity + governance metrics
  - ask     — AI-powered metadata query (GPT-4o-mini + OM MCP tools)
  - lineage — entity lineage tree view
  - help    — show available commands
"""

from __future__ import annotations

import asyncio
import traceback
from typing import Any

import structlog
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from pulse.config import settings
from pulse.governance import format_governance_slack, get_governance_summary
from pulse.lineage_view import get_lineage_blocks
from pulse.om_client import search_metadata
from pulse.query_engine import process_query

logger = structlog.get_logger(__name__)

app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)

# ---------------------------------------------------------------------------
# Help text (reused by /pulse help and unknown subcommands)
# ---------------------------------------------------------------------------
HELP_TEXT = (
    ":zap: *OpenMetadata Pulse — Commands*\n\n"
    "`/pulse health`  — OM connectivity + governance metrics\n"
    "`/pulse ask <question>`  — AI-powered metadata query\n"
    "`/pulse lineage <entity>`  — Show entity lineage tree\n"
    "`/pulse help`  — Show this help message"
)


# ---------------------------------------------------------------------------
# Async runner helper
# ---------------------------------------------------------------------------
def _run_async(coro):
    """Run an async coroutine from a sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result(timeout=60)
    return asyncio.run(coro)


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
            _handle_ask(respond, args, user_id)
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
    """Check OM connectivity and return governance summary."""
    logger.info("health_check_start", om_url=settings.om_server_url)

    try:
        summary = _run_async(get_governance_summary())
        result = format_governance_slack(summary)
        logger.info("health_check_success", om_url=settings.om_server_url)
        return result
    except Exception as exc:
        logger.error("health_check_failed", om_url=settings.om_server_url, error=str(exc))
        return f"❌ Cannot reach OpenMetadata at `{settings.om_server_url}`"


def _handle_ask(respond, args: str, user_id: str = "unknown") -> None:  # noqa: ANN001
    """Handle AI-powered metadata query using GPT-4o-mini + OM tools."""
    if not args.strip():
        respond(":warning: Please provide a question. Usage: `/pulse ask <question>`")
        return

    logger.info("ask_start", user=user_id, question=args)

    # Show typing indicator
    respond(f":hourglass_flowing_sand: *Thinking…* Processing your question:\n> {args}")

    try:
        answer = _run_async(process_query(args))
        respond(answer)
        logger.info("ask_complete", user=user_id, question=args, answer_len=len(answer))
    except Exception as exc:
        logger.error("ask_error", user=user_id, question=args, error=str(exc), exc_info=True)
        respond(
            ":x: *AI Query Failed*\n"
            "Something went wrong processing your question. Please try again.\n"
            f"_Error: {type(exc).__name__}_"
        )


def _handle_lineage(respond, args: str) -> None:  # noqa: ANN001
    """Handle entity lineage lookup and render as tree in Slack."""
    if not args.strip():
        respond(":warning: Please provide an entity name. Usage: `/pulse lineage <entity>`")
        return

    logger.info("lineage_start", entity=args)

    try:
        blocks = _run_async(get_lineage_blocks(args.strip()))
        # Post as blocks
        respond(blocks=blocks, text=f"Lineage for {args}")
        logger.info("lineage_complete", entity=args)
    except Exception as exc:
        logger.error("lineage_error", entity=args, error=str(exc), exc_info=True)
        respond(
            f":x: *Lineage Lookup Failed*\n"
            f"Could not fetch lineage for `{args}`.\n"
            f"_Error: {type(exc).__name__}_"
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
