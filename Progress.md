# Progress Tracker

Per-person, per-phase progress on every task in [TaskSync.md](./TaskSync.md). One row per task. Use this file to coordinate day to day.

## How to use this file

1. Pick the next task in the "Order of execution" list for your phase.
2. Open a GitHub issue for that task in `nishanthatgit/openmetadata-pulse` using the right template. Title format: `[<TASK-ID>] <short description>`.
3. Assign the issue to yourself. Paste the issue number into the `Issue` column below.
4. Create a branch: `<type>/<task-id>-<short-slug>` (e.g., `feat/p1-03-om-client`).
5. Walk the lifecycle and tick the boxes as you go.

## Reviewer routing

| Author                                      | Reviewer requested |
| ------------------------------------------- | ------------------ |
| @Chellammal-K, @lgrock007, @pknaveenece     | @nishanthatgit     |
| @nishanthatgit                              | @Chellammal-K      |

## Lifecycle checklist (one row per task)

```
[P] Plan  [B] Build  [V1] Validate  [F] Fix  [V2] Validate  [PR] PR opened  [R] Reviewed  [M] Merged
```

## Status legend

| Symbol | Meaning     |
| ------ | ----------- |
| `[ ]`  | Not started |
| `[/]`  | In progress |
| `[x]`  | Done        |
| `[!]`  | Blocked     |

---

## Phase 0 — Setup & Claim (Day 5, April 21)

**Order of execution:** P0-01 → P0-02 → P0-03 → P0-04 → P0-05 → P0-06.

### @nishanthatgit

| Task ID | Description                                    | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ---------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0-01   | Create repo `nishanthatgit/openmetadata-pulse` |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P0-02   | Post intent comment on upstream #27087         |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P0-03   | Add team as collaborators (3 invites)          |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P0-04   | Redeem OpenAI credits, generate key            |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P0-05   | Drop `CLAUDE.md` into repo root               |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P0-06   | Star open-metadata/OpenMetadata (all 4)        |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### Per-person setup

| Owner          | Star OM repo |
| -------------- | ------------ |
| @nishanthatgit | [ ]          |
| @Chellammal-K  | [ ]          |
| @lgrock007     | [ ]          |
| @pknaveenece   | [ ]          |

---

## Phase 1 — Foundation (Day 5–6, April 21–22)

**Order of execution (cross-team):**

1. P1-11 (IGR: Docker OM running) — unblocks integration testing.
2. P1-01 → P1-02 (NKT: project skeleton + deps) — unblocks everyone else.
3. P1-07 → P1-08 → P1-09 (CHK: webhook + notifier + templates) — feeds NKT's bot.
4. P1-03 → P1-04 → P1-05 (NKT: OM client + Slack bot + verify).
5. P1-12 → P1-13 (IGR: configure webhook + seed tables).
6. P1-14 (IGR: scaffold React dashboard).
7. P1-10 (CHK: 10+ unit tests).
8. P1-15 (IGR: README setup steps).
9. P1-16 → P1-17 (PKN: README + AI disclosure).
10. P1-18 → P1-19 (PKN: GFI monitor + demo narrative).
11. P1-06 (NKT: review all Phase 1 PRs).

### @nishanthatgit

| Task ID | Description                                                | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ---------------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1-01   | Init repo with `pyproject.toml` and Phase 1 deps           |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-02   | Create project structure (`src/pulse/...`, `ui/`, `tests/`)|       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-03   | Implement `om_client.py`: MCP wrapper for search + details |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-04   | Implement `bot.py`: Slack bolt app + `/pulse` command      |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-05   | Verify `/pulse health` works in Slack                      |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-06   | Review all Phase 1 PRs                                     |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @Chellammal-K

| Task ID | Description                                                     | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | --------------------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1-07   | Implement `webhook_receiver.py`: FastAPI POST /webhook          |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-08   | Implement `notifier.py`: event → Slack Block Kit → post         |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-09   | Map 4 event types to Slack notification templates               |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-10   | 10+ unit tests for webhook parser + notifier                    |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @lgrock007

| Task ID | Description                                           | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ----------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1-11   | Local OM at `:8585` via Docker                        |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-12   | Configure OM webhook → `localhost:8000/webhook`       |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-13   | Pre-seed OM with 50+ tables (tiers, owners, tags)     |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-14   | Scaffold React dashboard (Vite + React + Recharts)    |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-15   | Document setup in README.md (Slack + OM in < 5 min)   |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @pknaveenece

| Task ID | Description                                           | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ----------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1-16   | Write project README.md (1-liner, features, setup)    | 18    | 32  | [x] | [x] | [x] | [ ] | [ ] | [x] | [x] | [x] |
| P1-17   | Add AI disclosure to README                           | 19    | 34  | [x] | [x] | [x] | [ ] | [ ] | [x] | [ ] | [ ] |
| P1-18   | Daily monitor unassigned hackathon GFIs               | 20    | n/a | [x] | [x] | [x] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P1-19   | Draft demo narrative outline                          |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

**GFI Tracking (P1-18)**
- 2026-04-22: Found unassigned hackathon GFI: #27482, #27444, #26712. Team notified in Slack.

### Phase 1 Exit Gate

- [ ] `/pulse health` works in Slack
- [ ] Webhook receiver accepts OM events and logs them
- [ ] At least one event type posts a formatted Slack message
- [ ] Dashboard scaffold renders on `:3000`
- [ ] README + .env.example committed

---

## Phase 2 — Core Features (Day 6–8, April 22–24)

**Order of execution (cross-team):**

1. P2-09 (CHK: error handling + retry/breaker) — foundation.
2. P2-01 (NKT: AI query engine).
3. P2-02 → P2-03 (NKT: lineage + governance summary).
4. P2-06 → P2-07 → P2-08 (CHK: smart routing + rich blocks + filtering).
5. P2-04 (NKT: multi-tool chaining).
6. P2-10 (CHK: integration tests).
7. P2-11 → P2-12 → P2-13 → P2-14 (IGR: dashboard features).
8. P2-15 (IGR: E2E test).
9. P2-16 → P2-17 → P2-18 → P2-19 (PKN: GFI + docs + demo narrative).
10. P2-05 (NKT: review all Phase 2 PRs).

### @nishanthatgit

| Task ID | Description                                                      | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ---------------------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P2-01   | AI Query Engine: `/pulse ask` → GPT-4o-mini → MCP tools → Slack |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-02   | Lineage in Slack: `/pulse lineage` → tree view                   |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-03   | Governance summary: `/pulse health` → coverage metrics           |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-04   | Multi-tool chaining (search → details → lineage in one turn)    |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-05   | Review all Phase 2 PRs                                           |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @Chellammal-K

| Task ID | Description                                                      | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ---------------------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P2-06   | Smart routing: event → owner lookup → route to owner's DM/channel|       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-07   | Rich Slack Blocks: schema diff, DQ cards, approval deep-links   |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-08   | Event filtering: configurable rules (Tier-1 only, skip bots)    |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-09   | Error handling: retry + circuit breaker + error envelope         |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-10   | Integration tests: webhook → notifier → mock Slack              |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @lgrock007

| Task ID | Description                                                      | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ---------------------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P2-11   | Dashboard: live activity feed via SSE                            |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-12   | Dashboard: ownership coverage donut chart                        |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-13   | Dashboard: DQ trend chart (pass/fail over 7 days)                |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-14   | Dashboard: governance workflow board (pending/approved/rejected)  |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-15   | E2E test: OM event → Slack notification + dashboard update       |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @pknaveenece

| Task ID | Description                                           | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ----------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P2-16   | Claim + fix a GFI issue (upstream PR)                 |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-17   | README Mermaid architecture diagram                   |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-18   | Refresh demo narrative with measurable outcomes       |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P2-19   | Daily competitive analysis refresh                    |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### Phase 2 Exit Gate

- [ ] 3 Slack commands working: `/pulse ask`, `/pulse lineage`, `/pulse health`
- [ ] Real-time notifications for 4 event types
- [ ] Smart routing to entity owners
- [ ] Dashboard shows live feed + 2 charts
- [ ] 20+ tests passing

---

## Phase 3 — Polish & Ship (Day 9–10, April 25–26)

**Order of execution (cross-team):**

1. P3-01 (NKT: scheduled digests).
2. P3-05 → P3-08 (CHK: edge cases + CI + coverage + metrics).
3. P3-09 → P3-10 → P3-11 (IGR: OM-native UI + responsive + polish).
4. P3-02 → P3-03 (NKT: security + logging).
5. P3-06 → P3-07 (CHK: CI + coverage).
6. P3-12 (IGR: clean-machine verify).
7. P3-13 → P3-14 (PKN: demo recordings).
8. P3-15 → P3-16 (PKN: final README + diagrams).
9. P3-04 (NKT: review all Phase 3 PRs).

### @nishanthatgit

| Task ID | Description                                                   | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ------------------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P3-01   | Scheduled digests: daily/weekly summary to Slack channel      |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-02   | Security audit: no secrets, input validation, Slack sig verify|       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-03   | structlog + redaction + request_id; no print()                |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-04   | Review all Phase 3 PRs                                        |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @Chellammal-K

| Task ID | Description                                                   | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ------------------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P3-05   | Edge cases as friendly Slack messages                         |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-06   | GitHub Actions CI: lint + typecheck + test                    |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-07   | Coverage report > 60% on `src/pulse/`                         |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-08   | `/metrics` endpoint: uptime, events, queries, latency         |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @lgrock007

| Task ID | Description                                                  | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ------------------------------------------------------------ | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P3-09   | OM-native UI: `#7147E8`, Inter font, dark mode default       |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-10   | Responsive layout for judging on different screens           |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-11   | Loading + error states polished                              |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-12   | Verify clone → run on clean machine via docker-compose       |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### @pknaveenece

| Task ID | Description                                                  | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | ------------------------------------------------------------ | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P3-13   | Record final demo video (2–3 min, 1920×1080)                 |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-14   | Record + verify backup demo video                            |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-15   | README finalized: GIF, 3-cmd setup, features, AI disclosure  |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P3-16   | Architecture diagram embedded in README                      |       |     | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

### Phase 3 Exit Gate

- [ ] Scheduled digest works
- [ ] Dashboard is OM-native quality
- [ ] Final + backup demo videos recorded
- [ ] README clone → run < 5 min
- [ ] All tests green, > 60% coverage
- [ ] CI pipeline green

---

## Phase 4 — Submit (Day 10, April 26)

### All team

| Task ID | Owner          | Description                                         | Issue | PR  | P   | B   | V1  | F   | V2  | PR  | R   | M   |
| ------- | -------------- | --------------------------------------------------- | ----- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P4-01   | @pknaveenece   | Final README review                                 |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P4-02   | @nishanthatgit | Repo hygiene + no secrets check                     |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P4-03   | @pknaveenece   | AI disclosure confirmed                             |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P4-04   | @nishanthatgit | Submit hackathon form on WeMakeDevs                 |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P4-05   | @nishanthatgit | Link demo + repo in submission                      |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P4-06   | @pknaveenece   | Verify GFI PR status                                |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| P4-07   | @nishanthatgit | Comment submission link on target issues             |       | n/a | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## Snapshot per person

| Owner          | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total |
| -------------- | ------- | ------- | ------- | ------- | ------- | ----- |
| @nishanthatgit | 6       | 6       | 5       | 4       | 4       | 25    |
| @Chellammal-K  | 0       | 4       | 5       | 4       | 0       | 13    |
| @lgrock007     | 0       | 5       | 5       | 4       | 0       | 14    |
| @pknaveenece   | 0       | 4       | 4       | 4       | 3       | 15    |

Update the counts above only if you add or remove rows.
