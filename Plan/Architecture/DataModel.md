# Data Model

> The agent has no database. All state is in-memory Pydantic objects, lost on restart.

## Pydantic Models (Canonical Shapes)

### `OpenMetadataEventPayload`

Standardized representation of incoming webhooks from OM.

```python
from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime
from uuid import UUID

class EntityReference(BaseModel):
    id: UUID
    type: str
    name: str
    fullyQualifiedName: str

class ChangeEvent(BaseModel):
    eventType: Literal["entityCreated", "entityUpdated", "entityDeleted", "entitySoftDeleted"]
    entityType: str
    entityId: UUID
    entityFullyQualifiedName: str
    timestamp: int
    changeDescription: dict[str, Any] | None = None
    entity: dict[str, Any]  # The raw entity state at time of event

class OpenMetadataWebhookPayload(BaseModel):
    # OM sends an array of change events
    events: list[ChangeEvent]
    timestamp: int
```

### `RoutedNotification`

Internal model representing a decision made by the Smart Notification Router.

```python
class RoutedNotification(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    om_entity_fqn: str
    event_type: str
    severity: Literal["low", "medium", "high", "critical"]
    target_slack_id: str | None = None          # User ID or Channel ID
    fallback_channel: str = "#data-alerts"
    formatted_blocks: list[dict[str, Any]]      # Slack Block Kit JSON
    routing_reason: str                         # e.g., "Routed to U123456 because they are listed as table owner."
```

### `SlackQueryContext`

Represents an incoming natural language command from Slack.

```python
class SlackQueryContext(BaseModel):
    interaction_id: UUID = Field(default_factory=uuid4)
    slack_user_id: str
    slack_channel_id: str
    raw_text: str
    command_type: Literal["ask", "lineage", "health", "mention"]
    received_at: datetime
```

## State Persistence Boundaries

| Store | What's in it | Lifetime |
|---|---|---|
| In-memory dictionary | Active SSE connections (Dashboard UI clients) | Until process restart / client disconnect |
| `logs/pulse.log` | JSON structured audit logs | 5 rotating files of 10 MB each |
| Slack Thread | Conversation history for multi-turn LLM context | Persistent in Slack platform |

## Error Envelope

Every API error response (e.g., from the webhook endpoint) uses this shape:

```python
class ErrorEnvelope(BaseModel):
    code: str                                         # snake_case machine-readable
    message: str                                      # human-readable, safe to render
    request_id: UUID
    ts: datetime
    details: dict[str, Any] | None = None             
```
