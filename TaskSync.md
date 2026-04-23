# TaskSync — Master Task Tracker

> **Last updated**: April 21, 2026 (Day 5)
> **Team**: Data Dudes
> **Days remaining**: 5
> **All tasks ordered by priority. Check off as you complete them.**

---

## Phase 0 — Setup & Claim (Day 5: April 21)

### DD-NKT (@nishanthatgit) — CRITICAL

- [ ] `P0-01` 🔴 Create NEW repo: `nishanthatgit/openmetadata-pulse` on GitHub (public, Apache 2.0)
- [ ] `P0-02` 🔴 Post intent comment on [#27087](https://github.com/open-metadata/OpenMetadata/issues/27087) (Governance Notification Triggers) — signal the Data Dudes' Slack bot approach
- [ ] `P0-03` Add team as collaborators: @Chellammal-K, @lgrock007, @pknaveenece
- [ ] `P0-04` Redeem OpenAI API credits, generate key, save in `.env`
- [ ] `P0-05` Drop `CLAUDE.md` into repo root
- [ ] `P0-06` Star [open-metadata/OpenMetadata](https://github.com/open-metadata/OpenMetadata) — all 4 team members

### Intent Comment Template (for #27087):

```
Hi @PubChimps — sharing what Data Dudes (team of 4) are building for T-05: Community & Comms Apps.

Team: @nishanthatgit @Chellammal-K @lgrock007 @pknaveenece

Approach:
- Standalone Python Slack bot using official `data-ai-sdk` + LangChain + OpenAI GPT-4o-mini
- Connects OM MCP server (8+ tools) for AI-powered NL queries directly in Slack
- Real-time notifications: OM webhook → smart routing → Slack channels (owner-aware)
- Community dashboard: React UI with live activity feed, ownership coverage, DQ trends
- Slack commands: `/pulse ask`, `/pulse lineage`, `/pulse health`
- Standalone repo: github.com/nishanthatgit/openmetadata-pulse (link to follow)

Posting for coordination only — understood this is open competition, not assigned.
We'll link the final submission + demo video before the Apr 26 deadline.
```

### Phase 0 Exit Gate

- [ ] Repo created and all collaborators added
- [ ] Intent comment posted
- [ ] `.env.example` committed

---

## Phase 1 — Foundation (Day 5–6: April 21–22)

> **Strategy**: Get the Slack bot responding to `/pulse` commands and OM webhook receiver running. Both must work before any AI.

### DD-NKT (@nishanthatgit) — Tech Lead

- [ ] `P1-01` Init repo with `pyproject.toml` — deps: `data-ai-sdk[langchain]`, `slack-bolt`, `fastapi`, `uvicorn`, `langchain-openai`
- [ ] `P1-02` Create project structure:
  ```
  openmetadata-pulse/
  ├── pyproject.toml
  ├── .env.example
  ├── src/pulse/
  │   ├── __init__.py
  │   ├── bot.py              ← Slack bot (slack-bolt)
  │   ├── om_client.py        ← data-ai-sdk wrapper
  │   ├── query_engine.py     ← NL → OM MCP tool → Slack blocks
  │   ├── webhook_receiver.py ← FastAPI webhook endpoint
  │   ├── notifier.py         ← Smart event router → Slack
  │   └── dashboard_api.py    ← Dashboard REST + SSE endpoints
  ├── ui/                     ← React dashboard
  ├── docker-compose.yml
  └── tests/
  ```
- [ ] `P1-03` Implement `om_client.py`: connect to OM MCP, wrap `search_metadata` + `get_entity_details`
- [ ] `P1-04` Implement `bot.py`: Slack bolt app, register `/pulse` slash command, health check response
- [x] `P1-05` Verify: `/pulse health` in Slack returns "Pulse is alive, connected to OM at :8585"
- [ ] `P1-06` Review all Phase 1 PRs

### DD-CHK (@Chellammal-K) — Senior Builder

- [ ] `P1-07` Implement `webhook_receiver.py`: FastAPI `POST /webhook` endpoint, parse OM change events
- [ ] `P1-08` Implement `notifier.py`: take parsed event → format as Slack Block Kit message → post to channel
- [ ] `P1-09` Map OM event types to notification templates (schema change, DQ failure, new asset, ownership change)
- [ ] `P1-10` Write 10+ unit tests for webhook parser + notifier (mock Slack API)

### DD-IGR (@lgrock007) — Builder

- [ ] `P1-11` Docker: get local OM instance running at `:8585`
- [ ] `P1-12` Configure OM webhook to POST change events to `localhost:8000/webhook`
- [ ] `P1-13` Pre-seed OM with 50+ tables (varied tiers, owners, tags)
- [ ] `P1-14` Scaffold React dashboard (Vite + React + Recharts)
- [ ] `P1-15` Document setup in `README.md` — Slack bot setup + OM instance in < 5 min

### DD-PKN (@pknaveenece) — Delivery

- [ ] `P1-16` Write project `README.md`: 1-liner, features, architecture placeholder, setup steps
- [ ] `P1-17` Add AI disclosure: "Built with OpenAI GPT-4o-mini via LangChain + data-ai-sdk + slack-bolt"
- [ ] `P1-18` Daily monitor: [unassigned hackathon GFIs](https://github.com/open-metadata/OpenMetadata/issues?q=is%3Aopen+is%3Aissue+label%3Agood-first-issue+label%3Ahackathon+no%3Aassignee)
- [ ] `P1-19` Draft demo narrative outline

### Phase 1 Exit Gate

- [ ] `/pulse health` works in Slack
- [ ] Webhook receiver accepts OM events and logs them
- [ ] At least one event type posts a formatted Slack message
- [ ] Dashboard scaffold renders on `:3000`
- [ ] README + .env.example committed

---

## Phase 2 — Core Features (Day 6–8: April 22–24)

> **Strategy**: Lead with the AI query engine (the "wow" in demo). Then polish notifications. Then dashboard.

### DD-NKT (@nishanthatgit)

- [ ] `P2-01` **AI Query Engine**: `/pulse ask "which tables have PII but no owner?"` → GPT-4o-mini translates NL → selects MCP tools → formats Slack blocks
- [ ] `P2-02` **Lineage in Slack**: `/pulse lineage <entity>` → `get_entity_lineage` → renders upstream/downstream as indented Slack text
- [ ] `P2-03` **Governance Summary**: `/pulse health` → `search_metadata` → tag coverage %, PII %, unowned count → Slack blocks with emoji indicators
- [ ] `P2-04` Multi-tool chaining: ensure AI can chain `search_metadata` → `get_entity_details` → `get_entity_lineage` in one query
- [ ] `P2-05` Review all Phase 2 PRs

### DD-CHK (@Chellammal-K)

- [ ] `P2-06` **Smart Routing**: parse entity ownership from event → route notification only to entity owner's Slack DM or team channel
- [ ] `P2-07` **Rich Slack Blocks**: schema diff view, DQ test result cards, governance approval buttons (Approve/Reject deep-link to OM UI)
- [ ] `P2-08` **Event Filtering**: configurable rules (e.g., "only notify on Tier-1 table changes", "skip bot-generated events")
- [ ] `P2-09` Error handling: retry on Slack API failures, structured error envelope, circuit breaker on OM calls
- [x] `P2-10` Integration tests: webhook → notifier → mock Slack API

### DD-IGR (@lgrock007)

- [ ] `P2-11` Dashboard: connect to `dashboard_api.py` — show activity feed via SSE (real-time event stream)
- [ ] `P2-12` Dashboard: team ownership coverage chart (Recharts donut — owned vs unowned assets per domain)
- [ ] `P2-13` Dashboard: data quality trend chart (pass/fail over last 7 days, per domain)
- [ ] `P2-14` Dashboard: governance workflow board (pending/approved/rejected cards)
- [ ] `P2-15` E2E test: trigger OM event → see notification in Slack + event in dashboard

### DD-PKN (@pknaveenece)

- [ ] `P2-16` Claim + fix a GFI issue if an unassigned one appears (upstream PR)
- [ ] `P2-17` README Mermaid architecture diagram
- [ ] `P2-18` Refresh demo narrative with measurable outcomes
- [ ] `P2-19` Daily refresh competitive analysis — scan board for competing T-05 submissions

### Phase 2 Exit Gate

- [ ] 3 Slack commands working: `/pulse ask`, `/pulse lineage`, `/pulse health`
- [ ] Real-time notifications for 4 event types posting to Slack
- [ ] Smart routing sends DQ alerts only to entity owners
- [ ] Dashboard shows live activity feed + 2 charts
- [ ] 20+ tests passing

---

## Phase 3 — Polish & Ship (Day 9–10: April 25–26)

> **Strategy**: Make the dashboard OM-native quality. Record demo. Ship.

### DD-NKT (@nishanthatgit)

- [ ] `P3-01` **Scheduled Digests**: daily/weekly summary posted to Slack channel — "This week: 12 DQ failures, 5 new tables, 3 governance approvals"
- [ ] `P3-02` Security audit: no secrets in code, input validation on webhook payloads, Slack request signature verification
- [ ] `P3-03` `structlog` with redaction, no `print()`, request_id propagation
- [ ] `P3-04` Review all Phase 3 PRs

### DD-CHK (@Chellammal-K)

- [ ] `P3-05` Edge cases: empty results, auth failures, timeout — all surfaced as friendly Slack messages
- [ ] `P3-06` GitHub Actions CI: lint + typecheck + test-unit + test-integration
- [ ] `P3-07` Coverage report > 60% on `src/pulse/`
- [ ] `P3-08` `/metrics` endpoint: uptime, events processed, queries handled, avg latency

### DD-IGR (@lgrock007)

- [ ] `P3-09` **OM-native UI**: `#7147E8` purple, Inter font, dark mode default
- [ ] `P3-10` Dashboard responsive layout (judges may view on different screens)
- [ ] `P3-11` Loading + error states polished
- [ ] `P3-12` Verify clone → run on clean machine via `docker-compose up`

### DD-PKN (@pknaveenece)

- [ ] `P3-13` Record final demo video (2–3 min, 1920×1080): show Slack interaction + dashboard + real-time notification
- [ ] `P3-14` Record backup demo video
- [ ] `P3-15` README finalized: GIF at top, 3-cmd setup, all features listed, AI disclosure
- [ ] `P3-16` Architecture + trust-boundary diagram embedded in README

### Phase 3 Exit Gate

- [ ] Scheduled digest works
- [ ] Dashboard is OM-native quality
- [ ] Final + backup demo videos recorded
- [ ] README clone → run < 5 min
- [ ] All tests green, > 60% coverage
- [ ] CI pipeline green

---

## Phase 4 — Submit (Day 10: April 26)

### All Team

- [ ] `P4-01` Final README review (@pknaveenece)
- [ ] `P4-02` Repo hygiene: `.gitignore`, no `.env`, no debug code (@nishanthatgit)
- [ ] `P4-03` AI disclosure confirmed (@pknaveenece)
- [ ] `P4-04` Submit hackathon form on WeMakeDevs (@nishanthatgit)
- [ ] `P4-05` Link demo video + repo in submission (@nishanthatgit)
- [ ] `P4-06` Verify GFI PR status (@pknaveenece)
- [ ] `P4-07` Comment submission link on target issues (@nishanthatgit)

---

## ⚖️ Scoring Checklist (Run Before P4-04)

| Criterion                | Check                                                                                   | Score Target |
| ------------------------ | --------------------------------------------------------------------------------------- | ------------ |
| Potential Impact         | Demo shows real Slack notifications + NL queries (not just a static dashboard)           | 9/10         |
| Creativity & Innovation  | AI-powered Slack queries + smart owner-based routing + live dashboard                    | 9/10         |
| Technical Excellence     | Tests pass, structured logging, error handling, CI green                                | 8/10         |
| Best Use of OpenMetadata | 8+ MCP tools used, webhook API, search aggregations, lineage, entity details            | 9/10         |
| User Experience          | Zero-install Slack UX, OM-native dashboard, real-time updates                           | 9/10         |
| Presentation Quality     | README has GIF, Mermaid diagram, < 3 min setup; demo is narrated                       | 8/10         |

---

## Task Status Legend

| Symbol | Meaning             |
| ------ | ------------------- |
| `[ ]`  | Not started         |
| `[/]`  | In progress         |
| `[x]`  | Completed           |
| `[!]`  | Blocked             |
| 🔴     | Critical — do TODAY |
