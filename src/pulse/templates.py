"""Slack Block Kit templates for OpenMetadata event types."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from pulse.config import settings

# ---------------------------------------------------------------------------
# Event type → emoji mapping
# ---------------------------------------------------------------------------

EVENT_EMOJI: dict[str, str] = {
    "entityCreated": ":new:",
    "entityUpdated": ":pencil2:",
    "entityDeleted": ":wastebasket:",
    "entitySoftDeleted": ":ghost:",
    "testCaseResult": ":test_tube:",
}

# ---------------------------------------------------------------------------
# Core Helpers
# ---------------------------------------------------------------------------


def _humanize_event_type(event_type: str) -> str:
    """Convert camelCase event type to a human-readable title."""
    spaced = re.sub(r"([A-Z])", r" \1", event_type).strip()
    return spaced.title()


def _build_om_url(entity_type: str, fqn: str) -> str:
    """Construct a deep-link URL to an entity in the OpenMetadata UI."""
    base = settings.om_server_url.rstrip("/")
    return f"{base}/{entity_type}/{fqn}"


def _safe_json_loads(val: Any) -> Any:
    """Attempt to parse a string as JSON; return the original if parsing fails."""
    if isinstance(val, str):
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            pass
    return val


def _build_base_blocks(
    emoji: str, event_type: str, entity_type: str, fqn: str
) -> list[dict[str, Any]]:
    """Build the common Header, Section, and Context blocks."""
    human_event = _humanize_event_type(event_type)
    om_url = _build_om_url(entity_type, fqn)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {human_event}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Entity Type:* `{entity_type}`\n*FQN:* <{om_url}|{fqn}>",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f":clock1: {now}  |  `{event_type}`",
                },
            ],
        },
    ]


def _append_action_block(blocks: list[dict[str, Any]], entity_type: str, fqn: str) -> list[dict[str, Any]]:
    """Append the standard 'View in OpenMetadata' button block."""
    om_url = _build_om_url(entity_type, fqn)
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View in OpenMetadata",
                    "emoji": True,
                },
                "url": om_url,
                "action_id": "view_in_om",
            },
        ],
    })
    return blocks


# ---------------------------------------------------------------------------
# Template Functions
# ---------------------------------------------------------------------------


def template_schema_change(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Template for schema changes (columns added/removed/modified)."""
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    fqn = payload.get("entityFullyQualifiedName", "")
    emoji = EVENT_EMOJI.get(event_type, ":bell:")

    blocks = _build_base_blocks(emoji, event_type, entity_type, fqn)
    
    change_desc = payload.get("changeDescription", {})
    diff_text = ""
    
    for change_type in ["fieldsAdded", "fieldsDeleted", "fieldsUpdated"]:
        for field in change_desc.get(change_type, []):
            if field.get("name") == "columns":
                old_val = _safe_json_loads(field.get("oldValue", "[]"))
                new_val = _safe_json_loads(field.get("newValue", "[]"))
                
                # Truncate stringification to prevent oversized Slack blocks
                old_str = str(old_val)[:500]
                new_str = str(new_val)[:500]
                
                diff_text += f"*{change_type.replace('fields', '')}:*\n`Old:` {old_str}\n`New:` {new_str}\n\n"

    if diff_text:
        blocks.insert(2, {
            "type": "section",
            "text": {"type": "mrkdwn", "text": diff_text.strip()[:3000]}
        })

    return _append_action_block(blocks, entity_type, fqn)


def template_dq_failure(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Template for DQ test failures."""
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    fqn = payload.get("entityFullyQualifiedName", "")
    emoji = EVENT_EMOJI.get(event_type, ":bell:")

    blocks = _build_base_blocks(emoji, event_type, entity_type, fqn)
    
    test_case_res = payload.get("testCaseResult", {})
    status = test_case_res.get("testCaseStatus", "Failed")
    result_str = test_case_res.get("result", "N/A")
    
    blocks.insert(2, {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*Status:*\n`{status}`"},
            {"type": "mrkdwn", "text": f"*Result:*\n{result_str[:1500]}"},
        ]
    })
    
    return _append_action_block(blocks, entity_type, fqn)


def template_entity_created(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Template for newly created assets."""
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    fqn = payload.get("entityFullyQualifiedName", "")
    emoji = EVENT_EMOJI.get(event_type, ":bell:")

    blocks = _build_base_blocks(emoji, event_type, entity_type, fqn)
    
    owner_info = payload.get("owner")
    owner_name = "Unowned"
    if isinstance(owner_info, dict):
        owner_name = owner_info.get("name", "Unowned")
        
    tags = payload.get("tags", [])
    tier_str = next((tag.get("tagFQN") for tag in tags if tag.get("tagFQN", "").startswith("Tier")), "No Tier")

    blocks.insert(2, {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*Owner:*\n{owner_name}"},
            {"type": "mrkdwn", "text": f"*Tier:*\n{tier_str}"},
        ]
    })
    
    return _append_action_block(blocks, entity_type, fqn)


def template_ownership_change(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Template for ownership changes."""
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    fqn = payload.get("entityFullyQualifiedName", "")
    emoji = EVENT_EMOJI.get(event_type, ":bell:")

    blocks = _build_base_blocks(emoji, event_type, entity_type, fqn)
    
    change_desc = payload.get("changeDescription", {})
    diff_text = ""
    for field in change_desc.get("fieldsUpdated", []):
        if field.get("name") == "owner":
            old_val = _safe_json_loads(field.get("oldValue", "{}"))
            new_val = _safe_json_loads(field.get("newValue", "{}"))
            
            old_name = old_val.get("name", "Unknown") if isinstance(old_val, dict) else str(old_val)
            new_name = new_val.get("name", "Unknown") if isinstance(new_val, dict) else str(new_val)
            
            diff_text = f"Changed from `{old_name}` to `{new_name}`"

    if diff_text:
        blocks.insert(2, {
            "type": "section",
            "text": {"type": "mrkdwn", "text": diff_text}
        })

    return _append_action_block(blocks, entity_type, fqn)


def template_entity_deleted(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Template for deleted assets."""
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    fqn = payload.get("entityFullyQualifiedName", "")
    emoji = EVENT_EMOJI.get(event_type, ":bell:")

    blocks = _build_base_blocks(emoji, event_type, entity_type, fqn)
    
    updated_by = payload.get("updatedBy", "Unknown")
    
    blocks.insert(2, {
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"Entity was removed by `{updated_by}`."}
    })
    
    return _append_action_block(blocks, entity_type, fqn)


def template_generic(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Fallback template for generic updates."""
    event_type = payload.get("eventType", "unknown")
    entity_type = payload.get("entityType", "unknown")
    fqn = payload.get("entityFullyQualifiedName", "")
    emoji = EVENT_EMOJI.get(event_type, ":bell:")

    blocks = _build_base_blocks(emoji, event_type, entity_type, fqn)
    return _append_action_block(blocks, entity_type, fqn)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def route_payload_to_template(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Determine the correct template and generate Slack blocks for the payload."""
    event_type = payload.get("eventType", "unknown")
    
    if event_type == "entityCreated":
        return template_entity_created(payload)
    
    elif event_type in ("entityDeleted", "entitySoftDeleted"):
        return template_entity_deleted(payload)
        
    elif event_type == "testCaseResult":
        return template_dq_failure(payload)
        
    elif event_type == "entityUpdated":
        # Need to check changeDescription to see if it's schema or ownership
        change_desc = payload.get("changeDescription", {})
        
        # Check ownership first
        for field in change_desc.get("fieldsUpdated", []):
            if field.get("name") == "owner":
                return template_ownership_change(payload)
                
        # Check schema (columns)
        for change_type in ("fieldsAdded", "fieldsDeleted", "fieldsUpdated"):
            for field in change_desc.get(change_type, []):
                if field.get("name") == "columns":
                    return template_schema_change(payload)
                    
        return template_generic(payload)
        
    # Fallback
    return template_generic(payload)
