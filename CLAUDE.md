# CLAUDE.md — OpenMetadata Pulse

This file provides context for AI coding assistants.

## Project Overview

OpenMetadata Pulse is an AI-powered Slack bot and team collaboration hub for OpenMetadata.
It bridges the gap between the OM UI and where data teams actually work: Slack.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Slack**: slack-bolt (official Python SDK)
- **AI**: OpenAI GPT-4o-mini via LangChain + data-ai-sdk
- **Frontend**: React + Vite + Recharts (in `ui/`)
- **Testing**: pytest + pytest-asyncio + respx
- **Lint**: ruff + mypy

## Project Structure

```
src/pulse/           # Main Python package
  bot.py             # Slack bot (slack-bolt) — /pulse commands
  om_client.py       # data-ai-sdk wrapper for OM MCP tools
  query_engine.py    # NL → OM MCP tool → Slack blocks
  webhook_receiver.py# FastAPI POST /webhook endpoint
  notifier.py        # Smart event router → Slack
  dashboard_api.py   # Dashboard REST + SSE endpoints
ui/                  # React dashboard (Vite)
tests/               # pytest tests
```

## Key Commands

```bash
# Install deps
pip install -e ".[dev]"

# Run the bot + API
python -m pulse.bot

# Run tests
pytest

# Lint
ruff check src/ tests/
mypy src/
```

## Conventions

- Use `structlog` for all logging — no `print()`
- Type hints on all public functions
- Async-first: FastAPI endpoints and Slack handlers are async
- All env vars loaded via pydantic-settings in `config.py`
- Tests use `respx` to mock HTTP calls
