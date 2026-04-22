# 🎬 Demo Video Narrative Outline

> **Target duration**: 2:30 – 3:00  
> **Format**: Screen recording with voiceover  
> **Audience**: Hackathon judges, OpenMetadata community  
> **Goal**: Show Pulse solving a real pain point — context-switching for data teams

---

## 📋 Section Breakdown

| # | Section | Duration | Screen |
|---|---------|----------|--------|
| 1 | The Problem | 0:00 – 0:30 | Slides / OM UI |
| 2 | Meet Pulse | 0:30 – 0:45 | Architecture diagram |
| 3 | Live Demo — Slack Bot | 0:45 – 1:30 | Slack workspace |
| 4 | Live Demo — Notifications | 1:30 – 2:00 | OM UI → Slack |
| 5 | Live Demo — Dashboard | 2:00 – 2:30 | Community Dashboard |
| 6 | Wrap-Up | 2:30 – 2:45 | Closing slide |

---

## 🎙️ Detailed Script

### Section 1: The Problem (0:00 – 0:30)

**Screen**: Show OpenMetadata UI with multiple browser tabs open (tables, lineage, DQ tests). Then show a Slack workspace with no metadata context.

**Talking Points**:
- *"If you're a data engineer, you know this pain. Your metadata lives in OpenMetadata... but your team lives in Slack."*
- *"Schema changes break silently. DQ tests fail without anyone noticing. Ownership questions bounce around for hours."*
- *"Teams waste an average of 15+ context switches per day jumping between tools."*
- *"What if your metadata came to you — right where you work?"*

**Measurable Outcome**: *"Teams lose ~15 context switches per day to tool-hopping."*

---

### Section 2: Meet Pulse (0:30 – 0:45)

**Screen**: Show the Mermaid architecture diagram from README (full-screen, clean render).

**Talking Points**:
- *"Meet OpenMetadata Pulse — an AI-powered Slack bot and collaboration hub."*
- *"Three pillars: an AI Slack Bot for instant answers, real-time notifications for change events, and a community dashboard for live metrics."*
- *"Built on GPT-4o-mini, LangChain, data-ai-sdk, and slack-bolt — fully integrated with OpenMetadata's MCP tools."*

---

### Section 3: Live Demo — Slack Bot (0:45 – 1:30)

**Screen**: Slack workspace — #data-team channel

#### Demo 3a: `/pulse ask` (0:45 – 1:05)

**Action**: Type `/pulse ask "which tables have no owner?"` in Slack

**Talking Points**:
- *"Let's start with a natural language query. I'll ask Pulse which tables have no owner."*
- *Show the bot processing indicator*
- *"In under 5 seconds, Pulse queries OpenMetadata via MCP tools and returns a structured, sourced answer."*
- *"No SQL, no UI navigation — just plain English."*

**Measurable Outcome**: *"Response in < 5 seconds — 10x faster than manual search."*

#### Demo 3b: `/pulse lineage` (1:05 – 1:20)

**Action**: Type `/pulse lineage dim_customers`

**Talking Points**:
- *"Need to understand impact before a change? Ask for lineage."*
- *"Pulse traces upstream and downstream dependencies and formats them right in Slack."*
- *"Before, this required navigating to the OM UI, finding the table, clicking Lineage. Now: one command."*

#### Demo 3c: `/pulse health` (1:20 – 1:30)

**Action**: Type `/pulse health`

**Talking Points**:
- *"One more — a quick health check. Pulse summarizes your data quality status across the catalog."*
- *"DQ pass rates, recent failures, tables needing attention — all at a glance."*

---

### Section 4: Live Demo — Notifications (1:30 – 2:00)

**Screen**: Split view — OpenMetadata UI (left) + Slack (right)

#### Demo 4a: Trigger a Schema Change (1:30 – 1:45)

**Action**: In OM UI, add a column to `dim_customers` (e.g., `loyalty_tier`)

**Talking Points**:
- *"Now let's see real-time notifications in action."*
- *"I'm adding a new column to dim_customers in OpenMetadata..."*
- *Switch to Slack — notification appears within seconds*
- *"Boom. The table owner gets a Slack notification immediately — with the exact change, who made it, and a direct link."*

**Measurable Outcome**: *"Notification delivered in < 10 seconds from event."*

#### Demo 4b: DQ Test Failure (1:45 – 2:00)

**Action**: Show a pre-triggered DQ test failure notification in Slack

**Talking Points**:
- *"Same thing happens for data quality failures. When a DQ test fails, the table owner gets notified instantly."*
- *"No more checking dashboards every morning — Pulse brings the alert to you."*
- *"Smart routing means only the right people get notified — no spam."*

---

### Section 5: Live Demo — Dashboard (2:00 – 2:30)

**Screen**: Community Dashboard (`http://localhost:3000`)

#### Demo 5a: Ownership Coverage (2:00 – 2:10)

**Action**: Show the ownership coverage metrics

**Talking Points**:
- *"Finally, our Community Dashboard — a live view of your data estate's health."*
- *"Ownership coverage shows you how much of your catalog is owned — here we're at 72%, with a goal of 90%."*

#### Demo 5b: DQ Trends (2:10 – 2:20)

**Action**: Show the data quality trend chart (Recharts line/bar chart)

**Talking Points**:
- *"DQ trends over time — you can see pass rates improving as the team responds to Pulse notifications."*
- *"This used to require custom SQL queries. Now it's real-time, auto-updating."*

#### Demo 5c: Governance Board (2:20 – 2:30)

**Action**: Show the governance workflow board

**Talking Points**:
- *"And the governance board — pending approvals, review requests, and workflow status."*
- *"All powered by SSE for real-time updates — no page refreshes needed."*

---

### Section 6: Wrap-Up (2:30 – 2:45)

**Screen**: Closing slide with tech stack, team, and call to action

**Talking Points**:
- *"OpenMetadata Pulse: AI-powered Slack bot, real-time notifications, live dashboard."*
- *"Built with GPT-4o-mini, LangChain, data-ai-sdk, FastAPI, React, and slack-bolt."*
- *"We're Data Dudes — Nishant, Chellammal, Igrock, and Naveen."*
- *"Pulse turns OpenMetadata from a tool you visit into a service that works for you."*
- *"Thank you — and check us out on GitHub."*

**Measurable Outcome**: *"Saves ~15 context switches/day, < 5s query response, < 10s notification delivery."*

---

## 🖥️ Screen Sequence Summary

| Timestamp | Screen | Key Action |
|-----------|--------|------------|
| 0:00 | OM UI + multiple tabs | Show the context-switching problem |
| 0:30 | Architecture diagram | Introduce Pulse and 3 pillars |
| 0:45 | Slack — `/pulse ask` | NL query → structured response |
| 1:05 | Slack — `/pulse lineage` | Lineage tracing in one command |
| 1:20 | Slack — `/pulse health` | DQ health check at a glance |
| 1:30 | OM UI + Slack (split) | Schema change → instant notification |
| 1:45 | Slack notification | DQ failure alert with smart routing |
| 2:00 | Dashboard — ownership | Live ownership coverage metrics |
| 2:10 | Dashboard — DQ trends | Recharts line chart, real-time |
| 2:20 | Dashboard — governance | Workflow board with SSE updates |
| 2:30 | Closing slide | Tech stack, team, CTA |

---

## 📏 Measurable Outcomes to Mention

| Metric | Value | When to Mention |
|--------|-------|----------------|
| Context switches saved | ~15/engineer/day | Section 1 (Problem) |
| NL query response time | < 5 seconds | Section 3 (Slack Bot) |
| Notification latency | < 10 seconds | Section 4 (Notifications) |
| Manual search speedup | 10x faster | Section 3 (Slack Bot) |
| Ownership visibility | 100% coverage tracking | Section 5 (Dashboard) |

---

## ✅ Pre-Recording Checklist

- [ ] OpenMetadata running with sample data loaded
- [ ] Slack workspace configured with Pulse bot installed
- [ ] All 3 `/pulse` commands working (ask, lineage, health)
- [ ] At least one webhook notification trigger prepared
- [ ] Dashboard running at `localhost:3000` with live data
- [ ] Screen recording software set up (OBS or similar)
- [ ] Microphone tested for clear voiceover
- [ ] Read script aloud — confirm it fits in 2:30–3:00

---

<p align="center">
  <em>Prepared by Data Dudes — OpenMetadata Community Hackathon 2025</em>
</p>
