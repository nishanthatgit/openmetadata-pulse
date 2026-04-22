# Non-Functional Requirements (NFRs)

## NFR-01: Agent Responsiveness
The AI Query Engine via Slack must provide an initial visible response to the user (e.g., an ack or a typing indicator via `slack-bolt`) within **1 second** of receiving a command.
The fully formatted LLM answer (including MCP fetching) must return in under **5 seconds** for P90.

## NFR-02: Webhook Idempotency & Latency
The `POST /webhook/openmetadata` API must acknowledge the OM Webhook (return 202) within **500 milliseconds**. All blocking operations (routing, hitting the OM API for owners, sending to Slack) must happen asynchronously or via background tasks. 
Duplicate webhook deliveries (via same event ID) should be quietly ignored.

## NFR-03: Resiliency (The Circuit Breakers)
Every external call requires a pybreaker circuit breaker and a Tenacity retry block.
1. **OM MCP Client**: 3 retries (exp backoff 0.5s to 2s). Circuit opens on 5 consecutive failures.
2. **Slack API**: 3 retries on 429/5xx only. Circuit opens on 5 failures.
3. **OpenAI**: 2 retries. Circuit opens on 3 failures.

## NFR-04: Stateless Notification Router
The application does not use a persistent database for Slack routing rules. It infers routing dynamically by querying OpenMetadata for the specific entity's `owner` or `domain` at the time the webhook is processed. 

## NFR-05: Observability
All codebase layers must log JSON using `structlog`.
A `/metrics` endpoint must be exposed for Prometheus scraping, tracking at minimum:
- Webhook arrival rates.
- Notification dispatch success/failure counts.
- Slack query classification latency.
