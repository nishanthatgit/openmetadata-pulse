# Product Requirements Document (PRD)

> **Track**: T-05 (Community & Comms Apps)
> **Product**: OpenMetadata Pulse

## 1. Vision & Problem Statement

**Problem:** Data practitioners live in Slack/Teams/Google Chat. OpenMetadata (OM) is where the metadata lives. Currently, when an OM alert fires (e.g., pipeline failure, schema drift), it lands in OM, and stewards must manually bridge the gap: copy details, open Slack, tag the owner, and start a thread. This context-switching drains productivity and leads to missed alerts.

**Vision:** "Govern your data where you work." OpenMetadata Pulse is a standalone GenAI Slack Bot and Community Dashboard. It acts as the bridge that brings OpenMetadata directly into Slack channels, allowing practitioners to query, interact with, and receive targeted notifications about their data without leaving their primary communication tool.

## 2. Target Audience (User Personas)

1. **The Data Engineer (DE):** Needs to know immediately if a pipeline they own breaks or if a schema change they pushed breaks downstream assets.
2. **The Data Steward:** Needs to quickly answer questions from business users about data ownership, PII presence, and data quality (DQ).
3. **The Data Leader / Manager:** Needs a high-level view of team collaboration — how fast are DQ alerts resolved? What is the ownership coverage across the domain?

## 3. Core Features (The "Wow" Factors)

### Feature 1: AI-Powered Slack Querying (Conversational Catalog)
- **NL to OM:** Users type `@Pulse which tables in the ecommerce db have no owner?`
- **MCP Integration:** Pulse translates the NL to an OM MCP tool call (`search_metadata`), fetches the result, and formats it cleanly in Slack using Block Kit UI.
- **Lineage in Chat:** `@Pulse show lineage for table dim_customers.` Pulse fetches `get_entity_lineage` and renders a text-based tree in the Slack thread.

### Feature 2: Smart, Owner-Aware Notifications
- **Status Quo:** Webhooks blast a single `#data-alerts` channel, causing alert fatigue.
- **Pulse Approach:** Pulse receives raw OM Webhooks, inspects the entity (e.g., the table that failed a DQ test), looks up the `owner` via MCP (`get_entity_details`), and routes a rich Slack Block message directly to the owner's DM or their specific team channel.

### Feature 3: Community Health Dashboard
- A standalone React GUI (rendered via Vite/FastAPI) that consumes the Pulse backend.
- Displays key community metrics derived from OM data:
  - **Ownership Coverage %** (by Domain/Team).
  - **DQ Event Burn-down** (Incoming vs Resolved alerts).
  - **Real-time Event Stream** (SSE feed of OM events).

## 4. Success Metrics (Judging Alignment)

| Metric | Target | Judging Criterion |
|---|---|---|
| Latency | < 3s for Slack responses | Technical Excellence / UX |
| Relevance | 100% of DQ alerts routed to table owners (not `#general`) | Creativity / Impact |
| MCP Usage | > 4 distinct MCP tools used | Best Use of OpenMetadata |
| Onboarding | < 5 mins to `docker-compose up` | Presentation / UX |

## 5. Scope Boundaries (What we are NOT doing)

- **Not modifying OpenMetadata core:** This is a standalone app leveraging standard APIs and Webhooks.
- **Not building for Microsoft Teams/Discord in Phase 1:** Slack is the target. We abstract the notifier interface to allow future extensions, but Phase 1 is Slack-only.
- **No Complex RBAC in Pulse:** Pulse assumes the permissions of the Bot JWT token configured in its `.env`. User-level impersonation is out of scope.
