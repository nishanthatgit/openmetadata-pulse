# OpenMetadata Pulse

> **AI-Powered Slack Bot & Team Collaboration Hub for OpenMetadata**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)

---

## What is Pulse?

Data teams drown in context-switching. Schema changes, failed data quality checks, governance approvals — all trapped inside the OM UI. **Pulse** bridges OpenMetadata and Slack so your team gets notified where they actually work.

### Three Pillars

| Pillar | Description |
|--------|-------------|
| 🤖 **AI Slack Bot** | `/pulse ask "which tables have no owner?"` — NL queries via GPT-4o-mini + OM MCP tools |
| 🔔 **Real-Time Notifications** | OM webhook → smart owner-based routing → Slack Block Kit messages |
| 📊 **Community Dashboard** | Live ownership coverage, DQ trends, governance workflow board |

---

## Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Version | Check Command |
|------|---------|---------------|
| **Docker Desktop** | 4.x+ | `docker --version` |
| **Docker Compose** | v2+ | `docker compose version` |
| **Python** | 3.11+ | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | 2.x+ | `git --version` |

### Slack App Setup

1. Go to [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From an app manifest**
2. Paste this manifest:

```yaml
display_information:
  name: OpenMetadata Pulse
  description: AI-powered metadata assistant
features:
  bot_user:
    display_name: Pulse
    always_online: true
  slash_commands:
    - command: /pulse
      description: OpenMetadata assistant
      usage_hint: "[health|ask|lineage|help]"
oauth_config:
  scopes:
    bot:
      - commands
      - chat:write
      - chat:write.public
settings:
  socket_mode_enabled: true
```

3. Install the app to your workspace
4. Copy these tokens:
   - **Bot Token** (`xoxb-...`) → from **OAuth & Permissions**
   - **App Token** (`xapp-...`) → from **Basic Information** → **App-Level Tokens** (create one with `connections:write` scope)
   - **Signing Secret** → from **Basic Information**

---

## Quick Start (< 5 minutes)

### 1. Clone

```bash
git clone https://github.com/nishanthatgit/openmetadata-pulse.git
cd openmetadata-pulse
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# OpenMetadata
OM_SERVER_URL=http://localhost:8585    # OM API endpoint
OM_API_TOKEN=                          # JWT token (generate from OM UI → Settings → Bots)

# Slack (from your Slack App)
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini              # Default model

# Ports
DASHBOARD_PORT=3000
API_PORT=8000
```

### 3. Start Everything

```bash
# Start OpenMetadata + Pulse API + Bot
docker-compose up -d

# Wait ~2 minutes for OM to initialize, then verify:
curl http://localhost:8585/api/v1/system/version
# Expected: {"version":"x.x.x", ...}
```

### 4. Seed Test Data (Optional)

```bash
pip install httpx
python scripts/seed_om.py
# Creates 54 tables across 3 databases with varied metadata
```

### 5. Configure Webhook

```bash
python scripts/configure_webhook.py --docker
# Links OM events → Pulse API
```

### 6. Start Dashboard (Development)

```bash
cd ui
npm install
npm run dev
# Opens at http://localhost:3000
```

---

## Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OM_SERVER_URL` | ✅ | `http://localhost:8585` | OpenMetadata API base URL |
| `OM_API_TOKEN` | ✅ | — | JWT token for OM API authentication |
| `SLACK_BOT_TOKEN` | ✅ | — | Slack bot OAuth token (`xoxb-...`) |
| `SLACK_APP_TOKEN` | ✅ | — | Slack app-level token (`xapp-...`) for Socket Mode |
| `SLACK_SIGNING_SECRET` | ✅ | — | Slack signing secret for request verification |
| `OPENAI_API_KEY` | ✅ | — | OpenAI API key for AI queries |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | OpenAI model to use |
| `API_PORT` | ❌ | `8000` | Pulse API server port |
| `DASHBOARD_PORT` | ❌ | `3000` | Dashboard dev server port |

---

## Architecture

```mermaid
graph TB
    subgraph Slack["Slack Workspace"]
        U[Data Team User]
        SC[Slack Channel]
    end
    subgraph Pulse["OpenMetadata Pulse"]
        SB[Slack Bot<br/>slack-bolt]
        AI[AI Query Engine<br/>GPT-4o-mini + LangChain]
        WH[Webhook Receiver<br/>FastAPI]
        NE[Notification Engine<br/>Smart Router]
        API[Dashboard API<br/>FastAPI]
    end
    subgraph OM["OpenMetadata"]
        MCP[MCP Server<br/>12 tools]
        EVT[Event System<br/>Webhooks]
        SEARCH[Search API]
    end
    subgraph Dashboard["Community Dashboard"]
        UI[React UI<br/>Recharts + SSE]
    end
    U -->|/pulse ask ...| SB
    SB --> AI
    AI -->|search_metadata<br/>get_entity_details<br/>get_entity_lineage| MCP
    EVT -->|change events| WH
    WH --> NE
    NE -->|formatted blocks| SC
    API -->|SSE stream| UI
    API -->|aggregations| SEARCH
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | OpenAI GPT-4o-mini |
| OM SDK | `data-ai-sdk[langchain]` |
| Bot Engine | `slack-bolt` |
| Backend | FastAPI + Uvicorn |
| Frontend | React + Vite + Recharts + SSE |
| Testing | pytest + pytest-asyncio + respx |
| Lint | ruff + mypy |
| CI | GitHub Actions |
| Deployment | Docker Compose |

---

## Project Structure

```
openmetadata-pulse/
├── src/pulse/              # Python backend
│   ├── bot.py              # Slack bot (slack-bolt, Socket Mode)
│   ├── server.py           # FastAPI server (webhook + dashboard API)
│   ├── webhook_receiver.py # POST /webhook endpoint
│   ├── notifier.py         # Smart notification router
│   ├── om_client.py        # OpenMetadata API client
│   ├── query_engine.py     # AI query engine (LangChain)
│   ├── dashboard_api.py    # Dashboard REST API
│   └── config.py           # Centralized settings (pydantic-settings)
├── ui/                     # React dashboard
│   ├── src/components/     # React components
│   ├── src/lib/            # Utilities (SSE client)
│   └── vite.config.ts      # Vite config (port 3000)
├── scripts/                # Utility scripts
│   ├── configure_webhook.py
│   └── seed_om.py
├── tests/                  # Test suite
├── docker-compose.yml      # Full development stack
├── Dockerfile              # Python app container
└── pyproject.toml          # Python project config
```

---

## Troubleshooting

### OpenMetadata won't start

```bash
# Check logs
docker-compose logs openmetadata

# Common fix: MySQL needs time to initialize on first run
# Wait 2-3 minutes and check again
docker-compose ps
```

### "Connection refused" on port 8585

- OM takes ~2 minutes to boot. Wait and retry.
- Ensure Docker has enough memory allocated (≥ 4GB recommended).

### Slack bot not responding

1. Verify tokens in `.env` are correct
2. Check Socket Mode is enabled in your Slack app settings
3. Verify the `/pulse` slash command is configured
4. Check bot logs: `docker-compose logs pulse-bot`

### Dashboard build errors

```bash
cd ui
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## Development

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/
```

---

## AI Disclosure

Built with **OpenAI GPT-4o-mini** via LangChain + `data-ai-sdk` + `slack-bolt`.

---

## Team — Data Dudes

| Name | GitHub | Role |
|------|--------|------|
| Nishant | [@nishanthatgit](https://github.com/nishanthatgit) | Tech Lead |
| Chellammal K | [@Chellammal-K](https://github.com/Chellammal-K) | Senior Builder |
| Igrock | [@Igrock007](https://github.com/Igrock007) | Builder |
| Naveen | [@pknaveenece](https://github.com/pknaveenece) | Delivery / Docs |

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
