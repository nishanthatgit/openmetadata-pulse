# API Contract

## Versioning
- **v1**: this document. Breaking changes bump to `v2`.
- Base path: `/api/v1/`

## Auth
- **v1 (hackathon)**: Local development without strict auth on the webhook receiver. Validate Slack signatures using `slack-bolt` best practices. Validate OM webhooks using a configured secret token (header match).

## Routes

### `POST /api/v1/webhook/openmetadata`

Receives Change Events from OpenMetadata.

**Headers:**
`Authorization: Bearer <CONFIGURED_WEBHOOK_SECRET>`

**Request:**
OpenMetadata standard Change Events array payload. (Matches `OpenMetadataWebhookPayload` in DataModel.md).

**Response 202 — Accepted**:
We immediately return 202 to OM to prevent webhook timeouts, then process the routing asynchronously.

```json
{
  "request_id": "uuid-v4",
  "status": "processing",
  "ts": "2026-04-26T14:30:00.000Z"
}
```

**Response 401 — Unauthorized**: Secret missing/invalid.

---

### `GET /api/v1/stream`

Server-Sent Events (SSE) endpoint for the Community Dashboard.

**Request:** None (browser standard EventSource).

**Response 200 — text/event-stream**:
```text
data: {"type": "event", "fqn": "ecommerce_db.shopify.customers", "action": "schema_change"}

data: {"type": "health_metric", "coverage": 92.5}
```

---

### `GET /api/v1/healthz`

Liveness/readiness probe.

**Response 200**:
```json
{
  "status": "ok",
  "checks": {
    "om_mcp": { "ok": true, "latency_ms": 42 },
    "slack_api": { "ok": true, "latency_ms": 115 },
    "openai": { "ok": true, "latency_ms": 180 }
  },
  "version": "0.1.0",
  "ts": "2026-04-26T14:30:00.000Z"
}
```

---

### `GET /api/v1/metrics`

Prometheus text-format metrics.

| Metric | Type | Labels |
|---|---|---|
| `pulse_webhook_events_total` | counter | `event_type`, `entity_type` |
| `pulse_routed_notifications_total`| counter | `severity`, `destination_type` |
| `pulse_slack_queries_total` | counter | `command_type`, `outcome` |
| `pulse_llm_tokens_total`| counter | `direction`, `model` |
| `pulse_circuit_breaker_state` | gauge | `circuit` (om_mcp, slack, openai) |
