"""AI query engine — translates natural language to OM API calls.

Uses LangChain + GPT-4o-mini to interpret user questions and
route them to the appropriate OpenMetadata API calls.

Implements P2-01 (AI Query Engine) and P2-04 (Multi-tool chaining).
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog
from langchain_core.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from pulse.config import settings
from pulse.om_client import get_entity_details, get_entity_lineage, search_metadata

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are **Pulse**, an AI assistant embedded in Slack that answers questions about
an organisation's data catalogue managed by **OpenMetadata**.

You have access to the following tools:
- **search_metadata**: Full-text search across all catalogued entities (tables, topics, dashboards, pipelines, etc.).
- **get_entity_details**: Fetch detailed metadata for a single entity by its type and fully-qualified name (FQN).
- **get_entity_lineage**: Fetch the upstream and downstream lineage graph for an entity by its type and UUID.

### Guidelines
1. Start by searching for relevant entities, then drill into details or lineage as needed.
2. Chain multiple tools when the question requires it (e.g., search → details → lineage).
3. Summarise results clearly using Slack markdown (*bold*, `code`, bullet lists).
4. If no results are found, say so clearly — do NOT hallucinate entity names.
5. Keep responses concise — no more than ~800 words.
6. When showing tables, use aligned columns.
7. For counts and percentages, compute them from actual data.
8. NEVER expose raw JSON to the user — always format it nicely.
"""

# ---------------------------------------------------------------------------
# LangChain tool wrappers (sync wrappers around async OM client)
# ---------------------------------------------------------------------------


def _run_async(coro):
    """Run an async coroutine in a sync context safely."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result(timeout=30)
    return asyncio.run(coro)


def _tool_search_metadata(query: str, limit: int = 10, index: str = "table_search_index") -> str:
    """Search OpenMetadata for entities matching a query.

    Args:
        query: Free-text search query (e.g. 'customers', 'PII', '*').
        limit: Maximum number of results to return (default 10).
        index: Search index to query (default 'table_search_index').
               Options: table_search_index, topic_search_index,
               dashboard_search_index, pipeline_search_index.

    Returns:
        JSON string of matching entities with their key metadata.
    """
    results = _run_async(search_metadata(query, limit=limit, index=index))
    # Extract only the useful fields to keep context window small
    summarised = []
    for hit in results:
        entry: dict[str, Any] = {
            "name": hit.get("name", ""),
            "fullyQualifiedName": hit.get("fullyQualifiedName", ""),
            "entityType": hit.get("entityType", "table"),
            "description": (hit.get("description") or "")[:200],
        }
        # Owner
        owner = hit.get("owner")
        if isinstance(owner, dict):
            entry["owner"] = owner.get("name", "unowned")
        else:
            entry["owner"] = "unowned"
        # Tags
        tags = hit.get("tags", [])
        entry["tags"] = [t.get("tagFQN", "") for t in tags if isinstance(t, dict)][:5]
        # Tier
        tier = hit.get("tier")
        if isinstance(tier, dict):
            entry["tier"] = tier.get("tagFQN", "")
        # Columns (for tables)
        columns = hit.get("columns", [])
        if columns:
            entry["columns"] = [
                c.get("name", "") for c in columns[:10] if isinstance(c, dict)
            ]
        # ID
        entry["id"] = hit.get("id", "")

        summarised.append(entry)
    return json.dumps(summarised, indent=2)


def _tool_get_entity_details(entity_type: str, fqn: str) -> str:
    """Get detailed metadata for a specific entity.

    Args:
        entity_type: The type of entity (e.g. 'table', 'topic', 'dashboard', 'pipeline').
        fqn: The fully-qualified name of the entity (e.g. 'sample_data.ecommerce_db.shopify.customers').

    Returns:
        JSON string with entity details including owner, tags, description, columns.
    """
    entity = _run_async(get_entity_details(entity_type, fqn))
    # Extract useful fields
    result: dict[str, Any] = {
        "id": entity.get("id", ""),
        "name": entity.get("name", ""),
        "fullyQualifiedName": entity.get("fullyQualifiedName", ""),
        "description": (entity.get("description") or "")[:500],
        "entityType": entity_type,
    }
    # Owner
    owner = entity.get("owner")
    if isinstance(owner, dict):
        result["owner"] = owner.get("name", "unowned")
    # Tags
    tags = entity.get("tags", [])
    result["tags"] = [t.get("tagFQN", "") for t in tags if isinstance(t, dict)]
    # Tier
    tier = entity.get("tier")
    if isinstance(tier, dict):
        result["tier"] = tier.get("tagFQN", "")
    # Columns
    columns = entity.get("columns", [])
    if columns:
        result["columns"] = [
            {
                "name": c.get("name", ""),
                "dataType": c.get("dataType", ""),
                "description": (c.get("description") or "")[:100],
                "tags": [t.get("tagFQN", "") for t in c.get("tags", []) if isinstance(t, dict)],
            }
            for c in columns[:20]
        ]
    # Followers
    followers = entity.get("followers", [])
    result["followerCount"] = len(followers)

    return json.dumps(result, indent=2)


def _tool_get_entity_lineage(entity_type: str, entity_id: str) -> str:
    """Get lineage (upstream and downstream dependencies) for an entity.

    Args:
        entity_type: The type of entity (e.g. 'table', 'topic', 'dashboard').
        entity_id: The UUID of the entity (get this from search or entity details).

    Returns:
        JSON string with lineage graph — nodes and edges.
    """
    lineage = _run_async(get_entity_lineage(entity_type, entity_id))

    # Summarise nodes
    nodes = []
    for node in lineage.get("nodes", []):
        nodes.append({
            "id": node.get("id", ""),
            "name": node.get("name", ""),
            "fullyQualifiedName": node.get("fullyQualifiedName", ""),
            "entityType": node.get("entityType", ""),
        })

    result = {
        "entity": {
            "id": lineage.get("entity", {}).get("id", ""),
            "name": lineage.get("entity", {}).get("name", ""),
            "fullyQualifiedName": lineage.get("entity", {}).get("fullyQualifiedName", ""),
        },
        "nodes": nodes[:20],
        "upstreamEdges": lineage.get("upstreamEdges", [])[:20],
        "downstreamEdges": lineage.get("downstreamEdges", [])[:20],
    }
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# LangChain tools
# ---------------------------------------------------------------------------

TOOLS = [
    StructuredTool.from_function(
        func=_tool_search_metadata,
        name="search_metadata",
        description="Search OpenMetadata for entities matching a query. Use this first to discover entities.",
    ),
    StructuredTool.from_function(
        func=_tool_get_entity_details,
        name="get_entity_details",
        description="Get detailed metadata (columns, tags, owner, description) for a single entity by type and FQN.",
    ),
    StructuredTool.from_function(
        func=_tool_get_entity_lineage,
        name="get_entity_lineage",
        description="Get upstream/downstream lineage graph for an entity by type and UUID.",
    ),
]

# ---------------------------------------------------------------------------
# Agent construction
# ---------------------------------------------------------------------------

_agent_executor = None


def _get_agent():
    """Lazily build and cache the LangChain agent."""
    global _agent_executor  # noqa: PLW0603
    if _agent_executor is not None:
        return _agent_executor

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured — cannot start AI engine.")

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
        request_timeout=30,
    )

    _agent_executor = create_react_agent(llm, tools=TOOLS, state_modifier=SYSTEM_PROMPT)
    logger.info("ai_agent_initialized", model=settings.openai_model, tools=len(TOOLS))
    return _agent_executor


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def process_query(question: str) -> str:
    """Process a natural-language metadata query and return Slack-formatted answer.

    Args:
        question: The user's natural-language question.

    Returns:
        Slack-markdown formatted answer string.
    """
    logger.info("process_query_start", question=question)

    try:
        agent = _get_agent()
        # AgentExecutor.invoke is synchronous — run in thread
        result = await asyncio.to_thread(
            agent.invoke,
            {"messages": [("user", question)]},
        )
        messages = result.get("messages", [])
        if messages:
            answer = messages[-1].content
        else:
            answer = "I couldn't find an answer to that question."
        logger.info("process_query_success", question=question, answer_len=len(answer))
        return answer

    except RuntimeError as exc:
        # Missing API key or config issue
        logger.error("process_query_config_error", error=str(exc))
        return f":warning: *Configuration Error*\n{exc}"

    except Exception as exc:
        logger.error("process_query_error", question=question, error=str(exc), exc_info=True)
        return (
            ":x: *AI Query Error*\n"
            "Something went wrong while processing your question. "
            "Please try rephrasing or contact the Pulse team.\n"
            f"_Error: {type(exc).__name__}_"
        )
