"""Slack bot engine using slack-bolt.

Registers /pulse slash commands and dispatches to subcommand handlers.
Each subcommand runs the corresponding logic and responds with
formatted Slack messages.

Subcommands:
    health   — verify OM connectivity
    ask      — AI-powered metadata query (Phase 2)
    lineage  — entity lineage view (Phase 2)
    help     — show available commands
"""

from __future__ import annotations

import asyncio
from typing import Any

import structlog
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from pulse.config import settings
from pulse.exceptions import OMClientError, OMConnectionError

logger = structlog.get_logger(__name__)

app = App(token=settings.slack_bot_token, signing_secret=settings.slack_signing_secret)

# ---------------------------------------------------------------------------
# Help text (reused in /pulse help and unknown subcommands)
# ---------------------------------------------------------------------------

_HELP_TEXT = (
    ":zap: *OpenMetadata Pulse* — Commands\n\n"
    "• `/pulse health`  — Check OM connectivity & version\n"
    "• `/pulse ask <question>`  — AI-powered metadata query\n"
    "• `/pulse lineage <entity_fqn>`  — Show entity lineage\n"
    "• `/pulse help`  — Show this help message\n"
)


# ---------------------------------------------------------------------------
# Async bridge — slack-bolt handlers are sync, om_client is async
# ---------------------------------------------------------------------------

def _run_async(coro: Any) -> Any:
    """Run an async coroutine from a sync slack-bolt handler."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result(timeout=30)
    return asyncio.run(coro)


# ---------------------------------------------------------------------------
# /pulse command dispatcher
# ---------------------------------------------------------------------------


@app.command("/pulse")
def handle_pulse_command(ack: Any, command: dict[str, Any], respond: Any) -> None:
    """Entry point for all /pulse slash commands.

    Parses the subcommand from the slash-command text and dispatches
    to the appropriate handler. Unknown subcommands display help.
    """
    ack()
    text = (command.get("text") or "").strip()
    subcommand, _, args = text.partition(" ")
    subcommand = subcommand.lower()
    user = command.get("user_name", "unknown")

    logger.info(
        "pulse_command_received",
        user=user,
        subcommand=subcommand or "(empty)",
        args=args.strip() if args else "",
        channel=command.get("channel_id", "unknown"),
    )

    try:
        if subcommand == "health":
            respond(_handle_health())
        elif subcommand == "ask":
            respond(_handle_ask(args))
        elif subcommand == "lineage":
            respond(_handle_lineage(args))
        elif subcommand == "help" or subcommand == "":
            respond(_HELP_TEXT)
        else:
            logger.info("pulse_unknown_subcommand", subcommand=subcommand)
            respond(
                f":question: Unknown command `{subcommand}`.\n\n{_HELP_TEXT}"
            )
    except Exception as exc:
        logger.error(
            "pulse_command_error",
            error=str(exc),
            error_type=type(exc).__name__,
            subcommand=subcommand,
            user=user,
        )
        respond(
            f":x: Something went wrong processing your request.\n"
            f"> `{type(exc).__name__}: {exc}`\n\n"
            f"Please try again or contact the Pulse team."
        )


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _handle_health() -> str:
    """Check OM connectivity and return a formatted status message.

    Calls ``om_client.check_health()`` which hits ``/api/v1/system/version``.
    Returns a green checkmark on success, or a red X with error details.
    """
    from pulse.om_client import check_health

    try:
        version_info = _run_async(check_health())
        version = version_info.get("version", "unknown")
        logger.info("health_check_ok", version=version)
        return (
            f":white_check_mark: *Pulse is alive!*\n\n"
            f"• Connected to OpenMetadata at `{settings.om_server_url}`\n"
            f"• OM Version: `{version}`"
        )
    except OMConnectionError as exc:
        logger.warning("health_check_failed", error=str(exc))
        return (
            f":x: *Cannot reach OpenMetadata*\n\n"
            f"• URL: `{settings.om_server_url}`\n"
            f"• Error: `{exc.detail}`\n\n"
            f"Check that the OM server is running and accessible."
        )
    except OMClientError as exc:
        logger.warning("health_check_error", error=str(exc), status=exc.status_code)
        return (
            f":warning: *OpenMetadata responded with an error*\n\n"
            f"• Status: `{exc.status_code}`\n"
            f"• Detail: `{exc.detail[:200]}`"
        )


def _handle_ask(question: str) -> str:
    """Handle /pulse ask <question>.

    Validates that a question was provided. Currently returns a Phase 2
    placeholder — will be wired to ``query_engine.py`` in P2-01.
    """
    if not question.strip():
        return (
            ":thinking_face: Please provide a question.\n"
            "Usage: `/pulse ask which tables have PII?`"
        )

    logger.info("pulse_ask", question=question.strip())
    return (
        f":hourglass_flowing_sand: *Processing your query…*\n"
        f"> _{question.strip()}_\n\n"
        f":construction: AI query engine coming in Phase 2."
    )


def _handle_lineage(entity_fqn: str) -> str:
    """Handle /pulse lineage <entity_fqn>.

    Validates that an entity FQN was provided. Currently returns a Phase 2
    placeholder — will be wired to ``om_client.get_entity_lineage`` in P2-02.
    """
    if not entity_fqn.strip():
        return (
            ":thinking_face: Please provide an entity FQN.\n"
            "Usage: `/pulse lineage sample.public.orders`"
        )

    logger.info("pulse_lineage", entity_fqn=entity_fqn.strip())
    return (
        f":hourglass_flowing_sand: *Fetching lineage for* `{entity_fqn.strip()}`…\n\n"
        f":construction: Lineage view coming in Phase 2."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the Slack bot in Socket Mode."""
    logger.info(
        "starting_pulse_bot",
        om_url=settings.om_server_url,
    )
    handler = SocketModeHandler(app, settings.slack_app_token)
    handler.start()


if __name__ == "__main__":
    main()
