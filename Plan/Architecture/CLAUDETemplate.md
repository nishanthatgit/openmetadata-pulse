# `CLAUDE.md` Template for OpenMetadata Pulse

> Drop this verbatim into the root of `nishanthatgit/openmetadata-pulse` once the repo is created.

---

```markdown
# CLAUDE.md

## Project: OpenMetadata Pulse

A standalone Python GenAI Slack Bot and Event Router for OpenMetadata.
Submitted to WeMakeDevs × OM Hackathon, Track T-05: Community & Comms Apps.
Team: Data Dudes.

## Architecture

Pattern: Modular Slack Bot + FastAPI sidecar.
```
src/pulse/
├── bot.py             ← Slack Bolt app definitions & commands.
├── router.py          ← Smart event router & notification logic.
├── webhooks.py        ← FastAPI routes for OM event ingestion.
├── exceptions.py      ← Standardized errors.
├── clients/           ← om_client, openai_client wrappers.
├── models/            ← Pydantic DataModels.
└── observability/     ← structured logging, prometheus metrics.
```

Layer rules:
- Slack command handlers parse text and pass to the query engine.
- Webhook routes validate payloads and pass to the router.
- Clients encapsulate all external API calls with timeouts and circuit breakers.

## Tech Stack
- Backend: Python 3.11+ + FastAPI + `slack-bolt`
- OM Interaction: `data-ai-sdk[langchain]`
- LLM: OpenAI GPT-4o-mini
- Observability: structlog + prometheus-client
- UI: Vite + React + Recharts (Dashboard)

## Code Conventions (Strict Enforcements)
1. **Three Laws of Implementation**: Layer separation, handle every error path, defend every external call with timeout + pybreaker.
2. **Type Hints**: `mypy --strict` is mandatory.
3. **No `print()` or `logging.info()`**: Use `structlog.get_logger(__name__)` configured for JSON output.
4. **Resilience**: Every `slack_sdk` or `om_client` call must have a timeout.
5. **No Secrets**: Use `.env`. Secrets handled by `pydantic-settings`.
6. **Async Default**: FastAPI routes and Slack bot handlers should be standard Python `async`.

## Reading Order for AI Sessions
1. This file.
2. `Plan/Project/PRD.md` — What we are building.
3. `Plan/Architecture/Overview.md` — Context diagrams.
4. `Plan/Architecture/DataModel.md` — Payload shapes.
5. `Plan/Architecture/APIContract.md` — Webhook ingestion shapes.

## Current Phase
Phase 1 (Foundation) — Getting the bot pinging OM and the webhook receiving payloads.
```
