"""AI query engine — translates natural language to OM MCP tool calls.

Uses LangChain + GPT-4o-mini to interpret user questions and
route them to the appropriate OM API calls.
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


async def process_query(question: str) -> str:
    """Process a natural-language metadata query and return Slack-formatted answer."""
    # TODO P2-01: implement LangChain agent with OM MCP tools
    logger.info("process_query", question=question)
    return f":construction: AI query engine coming soon.\n> {question}"
