<p align="center">
  <h1 align="center">🫀 OpenMetadata Pulse</h1>
  <p align="center">
    <strong>AI-Powered Slack Bot & Team Collaboration Hub for OpenMetadata</strong>
  </p>
  <p align="center">
    <em>Stop drowning in tabs. Get metadata answers where your team already works — Slack.</em>
  </p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://reactjs.org"><img src="https://img.shields.io/badge/React-18+-61DAFB.svg?style=for-the-badge&logo=react&logoColor=white" alt="React"></a>
  <a href="https://openmetadata.org"><img src="https://img.shields.io/badge/OpenMetadata-Hackathon_2025-7B61FF?style=for-the-badge" alt="OpenMetadata"></a>
  <a href="https://slack.com"><img src="https://img.shields.io/badge/Slack-Bot-4A154B?style=for-the-badge&logo=slack&logoColor=white" alt="Slack"></a>
</p>

---

## 🚀 The Problem

Data teams drown in **context-switching**. Schema changes break silently, data quality checks fail without notice, governance approvals stall — all trapped inside the OpenMetadata UI. Engineers juggle browser tabs, miss critical alerts, and waste hours chasing metadata across tools.

**Pulse fixes this.** It bridges OpenMetadata and Slack so your team gets actionable intelligence where they already work — no tab-switching, no missed alerts.

---

## 🏛️ Three Pillars

### 🤖 AI Slack Bot — Ask Anything, Get Answers Instantly

> `/pulse ask "which tables have no owner?"` → structured, sourced answers in seconds.

- Natural language queries powered by **GPT-4o-mini** + OpenMetadata MCP tools
- `/pulse lineage <table>` — instant lineage visualization
- `/pulse health` — data quality health check at a glance
- Supports entity search, metadata lookup, lineage tracing, and governance queries

### 🔔 Real-Time Notifications — Never Miss a Change

> Schema changed on `dim_customers`? The table owner gets a Slack DM within seconds.

- Webhook-driven: OpenMetadata events → Pulse → Slack in real time
- **Smart owner-based routing** — only the right people get notified
- Rich **Slack Block Kit** messages with actionable context
- Covers schema changes, DQ test failures, ownership updates, and more

### 📊 Community Dashboard — See Your Data Health at a Glance

> Live metrics, trends, and governance workflows — no OM login required.

- **Ownership coverage** — track how much of your catalog has owners
- **Data quality trends** — DQ pass/fail rates over time via Recharts
- **Governance board** — approval workflows and pending reviews
- Real-time updates via **Server-Sent Events (SSE)**

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

## ⚡ Quick Start (< 5 minutes)

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

| Service | URL | Description |
|---------|-----|-------------|
| OpenMetadata | `http://localhost:8585` | OM Server |
| Pulse API | `http://localhost:8000` | Webhook receiver + Dashboard API |
| Dashboard | `http://localhost:3000` | Community Dashboard UI |

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

### 🔧 Local Development

```bash
# Install Python dependencies
pip install -e ".[dev]"

# Run the Slack bot
python -m pulse.bot

# Run the API server
python -m pulse.server

# Run tests
pytest

# Lint & type check
ruff check src/ tests/
mypy src/
```

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph TB_SLACK["🔒 Trust Boundary: Slack Workspace"]
        U["👤 Data Team User"]
        SC["📢 #data-alerts Channel"]
        DM["✉️ Owner DM"]
    end

    subgraph TB_PULSE["🔒 Trust Boundary: Pulse Backend (localhost:8000)"]
        SB["🤖 Slack Bot<br/>slack-bolt · Socket Mode"]
        AI["🧠 AI Query Engine<br/>GPT-4o-mini · LangChain · MCP"]
        WH["📥 Webhook Receiver<br/>FastAPI · POST /webhook"]
        FE["🔍 Event Filter Engine<br/>Tier / Entity / Owner rules"]
        NE["🔔 Notification Engine<br/>Smart Router · Circuit Breaker"]
        TPL["🎨 Template Engine<br/>Slack Block Kit Builder"]
        API["📊 Dashboard API<br/>FastAPI · REST + SSE"]
    end

    subgraph TB_OM["🔒 Trust Boundary: OpenMetadata (localhost:8585)"]
        MCP["🔧 MCP Server<br/>12 tools · data-ai-sdk"]
        EVT["⚡ Event System<br/>Webhooks · Change Events"]
        SEARCH["🔍 Search & Aggregation API"]
        LINEAGE["🔗 Lineage API"]
    end

    subgraph TB_DASH["🔒 Trust Boundary: Dashboard UI (localhost:3000)"]
        UI["⚛️ React + Vite<br/>Recharts · EventSource SSE"]
    end

    %% ── Flow 1: PULL — User → Slash Command → MCP → Slack ──
    U -->|"① /pulse ask · lineage · health"| SB
    SB -->|"NL query"| AI
    AI -->|"search_metadata · get_entity_details"| MCP
    AI -->|"get_entity_lineage"| LINEAGE
    AI -->|"structured answer"| SB
    SB -->|"Block Kit response"| SC

    %% ── Flow 2: PUSH — OM Event → Webhook → Slack ──
    EVT -->|"② POST change event (JSON)"| WH
    WH -->|"validated payload"| FE
    FE -->|"passes filter?"| NE
    NE -->|"select template"| TPL
    TPL -->|"formatted blocks"| NE
    NE -->|"owner-routed alert"| DM
    NE -->|"channel broadcast"| SC

    %% ── Flow 3: SSE — Dashboard ←→ Pulse API ──
    UI -->|"③ GET /api/stats"| API
    API -->|"aggregations"| SEARCH
    API -->|"SSE event stream"| UI

    %% Styling
    classDef trustBoundary fill:#1a1a2e,stroke:#7B61FF,stroke-width:2px,color:#e0e0e0
    classDef slackNode fill:#4A154B,stroke:#E8DEF8,color:#fff
    classDef pulseNode fill:#1e3a5f,stroke:#64B5F6,color:#fff
    classDef omNode fill:#2d1b69,stroke:#7B61FF,color:#fff
    classDef dashNode fill:#1b5e20,stroke:#81C784,color:#fff

    class TB_SLACK trustBoundary
    class TB_PULSE trustBoundary
    class TB_OM trustBoundary
    class TB_DASH trustBoundary
    class U,SC,DM slackNode
    class SB,AI,WH,FE,NE,TPL,API pulseNode
    class MCP,EVT,SEARCH,LINEAGE omNode
    class UI dashNode
```

### Data Flow Summary

| # | Flow | Path | Trigger |
|---|------|------|---------|
| ① | **Pull** (User → Answer) | User → `/pulse` → Bot → AI → MCP → Slack | Slash command |
| ② | **Push** (Event → Alert) | OM Event → Webhook → Filter → Router → Slack DM/Channel | Schema/DQ/Ownership change |
| ③ | **SSE** (Live Dashboard) | React UI ← SSE ← Dashboard API ← OM Search | Page load / auto-refresh |

### How It Works

1. **User asks a question** in Slack via `/pulse ask "..."` → Slack Bot receives the command
2. **AI Query Engine** interprets the natural language and selects the right MCP tools
3. **MCP Server** executes the query against OpenMetadata and returns structured data
4. **Bot responds** with a rich Slack Block Kit message — sourced, formatted, actionable
5. **Meanwhile**, OpenMetadata pushes change events → Webhook Receiver → Filter Engine → Notification Engine routes alerts to the right owners in Slack
6. **Dashboard** displays live metrics via SSE — ownership, DQ trends, governance status

---

## 📁 Project Structure

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

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| 🧠 **LLM** | OpenAI GPT-4o-mini | Natural language understanding & response generation |
| 🔗 **OM SDK** | `data-ai-sdk[langchain]` | OpenMetadata MCP tool integration |
| 💬 **Bot Engine** | `slack-bolt` | Slack command handling & message posting |
| ⚙️ **Backend** | FastAPI + Uvicorn | Webhook receiver, Dashboard API, SSE streaming |
| ⚛️ **Frontend** | React + Vite + Recharts | Community Dashboard with real-time charts |
| 🔒 **Config** | Pydantic Settings | Type-safe environment variable management |
| 📝 **Logging** | `structlog` | Structured, async-safe logging |
| 🧪 **Testing** | pytest + pytest-asyncio + respx | Async tests with HTTP mocking |
| 🔍 **Lint** | ruff + mypy | Fast linting + strict type checking |
| 🚀 **CI/CD** | GitHub Actions | Automated lint, test, and build pipeline |
| 🐳 **Deployment** | Docker Compose | One-command local deployment |

---

## 📈 Key Metrics & Outcomes

| Metric | Target |
|--------|--------|
| ⏱️ **Response time** | < 5s for NL queries via Slack |
| 📬 **Notification latency** | < 10s from OM event to Slack message |
| 📊 **Ownership visibility** | 100% coverage tracking across catalog |
| 🔄 **Context switches saved** | ~15 per engineer per day |

---

## 🤖 AI Disclosure

This project uses AI at two levels:

- **Runtime**: OpenAI **GPT-4o-mini** via LangChain + `data-ai-sdk` powers the Slack bot's natural language query engine
- **Development**: AI coding assistants were used during development

For full details, see [`AI_DISCLOSURE.md`](AI_DISCLOSURE.md).

---

## 👥 Team — Data Dudes

| Name | GitHub | Role |
|------|--------|------|
| 🧑‍💻 Nishant | [@nishanthatgit](https://github.com/nishanthatgit) | Tech Lead |
| 👩‍💻 Chellammal K | [@Chellammal-K](https://github.com/Chellammal-K) | Senior Builder |
| 👨‍💻 Igrock | [@Igrock007](https://github.com/Igrock007) | Builder |
| 📋 Naveen | [@pknaveenece](https://github.com/pknaveenece) | Delivery / Docs |

---

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE).

---

<p align="center">
  <strong>Built with ❤️ for the OpenMetadata Community Hackathon 2025</strong>
</p>
