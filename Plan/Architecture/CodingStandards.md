# Coding Standards

## The Three Laws of Implementation

### Law 1: Layer Separation is Sacred
- **Bot Handlers (`pulse/bot.py`)**: Handle Slack specifics (Socket Mode, mentions). No direct OpenAI or OM calls.
- **Webhooks (`pulse/webhooks.py`)**: Parse HTTP. No business logic.
- **Router (`pulse/router.py`)**: Business logic. Given an OM Event, decide who gets it and what it looks like. Call Clients.
- **Clients (`pulse/clients/`)**: Wrappers for `slack_sdk`, `openai`, `data-ai-sdk`. This is the ONLY place network requests are made.

### Law 2: Handle Every Error Path
For every feature added:
1. What if OpenMetadata is down? (Circuit Breaker opens, return strict error shape, do not crash).
2. What if Slack rejects the Block Kit JSON? (Catch `SlackApiError`, log it, do not crash).
3. What if the entity has no owner? (Router must fall back to `#data-alerts` channel).

### Law 3: Every External Call Has Defense
No raw `urllib` or `requests` calls. Use the provided clients. Every network call must have a hard timeout.

```python
# RIGHT
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
async def get_owner_details(client, fqn: str):
    # httpx handles the pybreaker logic underneath
    return await client.mcp.call_tool("get_entity_details", {"fqn": fqn})
```

## Python Formatting
- Run `ruff format` and `ruff check --fix` before committing.
- `mypy --strict` must pass.

## Logging
DO NOT USE `print()`.
Use `structlog`:
```python
log.info("slack.command.received", user=user_id, command_type="ask")
# ...
log.error("om.mcp.failed", fqn=target_fqn, exc_info=True)
```
