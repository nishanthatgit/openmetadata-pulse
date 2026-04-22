"""Tests for the Slack Block Kit templates."""

from unittest.mock import patch

import pytest

from pulse.templates import (
    EVENT_EMOJI,
    _build_base_blocks,
    _build_om_url,
    _humanize_event_type,
    route_payload_to_template,
    template_dq_failure,
    template_entity_created,
    template_entity_deleted,
    template_generic,
    template_ownership_change,
    template_schema_change,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_humanize_event_type():
    assert _humanize_event_type("entityCreated") == "Entity Created"
    assert _humanize_event_type("entitySoftDeleted") == "Entity Soft Deleted"
    assert _humanize_event_type("testCaseResult") == "Test Case Result"

def test_build_om_url():
    with patch("pulse.templates.settings") as mock_settings:
        mock_settings.om_server_url = "http://localhost:8585/"
        url = _build_om_url("table", "sample.public.orders")
    assert url == "http://localhost:8585/table/sample.public.orders"

def test_build_base_blocks():
    with patch("pulse.templates.settings") as mock_settings:
        mock_settings.om_server_url = "http://localhost:8585"
        blocks = _build_base_blocks(":new:", "entityCreated", "table", "db.schema.tbl")
    
    assert len(blocks) == 3
    assert blocks[0]["type"] == "header"
    assert "Entity Created" in blocks[0]["text"]["text"]
    assert blocks[1]["type"] == "section"
    assert "db.schema.tbl" in blocks[1]["text"]["text"]
    assert blocks[2]["type"] == "context"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

@pytest.fixture
def base_payload():
    return {
        "eventType": "unknown",
        "entityType": "table",
        "entityFullyQualifiedName": "sample.public.orders"
    }

def test_template_entity_created(base_payload):
    payload = {
        **base_payload,
        "eventType": "entityCreated",
        "owner": {"name": "Data Team"},
        "tags": [{"tagFQN": "Tier.Tier1"}]
    }
    blocks = template_entity_created(payload)
    
    assert len(blocks) == 5  # header, section, new section, context, actions
    
    # Check the custom section
    custom_section = blocks[2]
    assert custom_section["type"] == "section"
    fields = custom_section["fields"]
    assert "Data Team" in fields[0]["text"]
    assert "Tier.Tier1" in fields[1]["text"]

def test_template_entity_created_missing_fields(base_payload):
    """Should handle missing owner/tags gracefully."""
    payload = {**base_payload, "eventType": "entityCreated"}
    blocks = template_entity_created(payload)
    
    custom_section = blocks[2]
    assert "Unowned" in custom_section["fields"][0]["text"]
    assert "No Tier" in custom_section["fields"][1]["text"]

def test_template_entity_deleted(base_payload):
    payload = {
        **base_payload,
        "eventType": "entityDeleted",
        "updatedBy": "admin_user"
    }
    blocks = template_entity_deleted(payload)
    
    custom_section = blocks[2]
    assert custom_section["type"] == "section"
    assert "admin_user" in custom_section["text"]["text"]

def test_template_entity_deleted_missing_fields(base_payload):
    payload = {**base_payload, "eventType": "entityDeleted"}
    blocks = template_entity_deleted(payload)
    assert "Unknown" in blocks[2]["text"]["text"]

def test_template_dq_failure(base_payload):
    payload = {
        **base_payload,
        "eventType": "testCaseResult",
        "testCaseResult": {
            "testCaseStatus": "Failed",
            "result": "Found 5 nulls, expected 0"
        }
    }
    blocks = template_dq_failure(payload)
    
    custom_section = blocks[2]
    assert "Failed" in custom_section["fields"][0]["text"]
    assert "Found 5 nulls" in custom_section["fields"][1]["text"]

def test_template_dq_failure_missing_fields(base_payload):
    payload = {**base_payload, "eventType": "testCaseResult"}
    blocks = template_dq_failure(payload)
    
    custom_section = blocks[2]
    assert "Failed" in custom_section["fields"][0]["text"]
    assert "N/A" in custom_section["fields"][1]["text"]

def test_template_ownership_change(base_payload):
    payload = {
        **base_payload,
        "eventType": "entityUpdated",
        "changeDescription": {
            "fieldsUpdated": [
                {"name": "owner", "oldValue": '{"name": "Old Team"}', "newValue": '{"name": "New Team"}'}
            ]
        }
    }
    blocks = template_ownership_change(payload)
    
    custom_section = blocks[2]
    assert "Old Team" in custom_section["text"]["text"]
    assert "New Team" in custom_section["text"]["text"]

def test_template_ownership_change_missing_fields(base_payload):
    payload = {
        **base_payload,
        "eventType": "entityUpdated",
        "changeDescription": {
            "fieldsUpdated": [
                {"name": "owner"} # missing old/new values
            ]
        }
    }
    blocks = template_ownership_change(payload)
    assert "Unknown" in blocks[2]["text"]["text"]

def test_template_schema_change(base_payload):
    payload = {
        **base_payload,
        "eventType": "entityUpdated",
        "changeDescription": {
            "fieldsAdded": [
                {"name": "columns", "newValue": '[{"name": "new_col"}]'}
            ]
        }
    }
    blocks = template_schema_change(payload)
    
    custom_section = blocks[2]
    assert "Added:" in custom_section["text"]["text"]
    assert "new_col" in custom_section["text"]["text"]

def test_template_schema_change_missing_fields(base_payload):
    payload = {
        **base_payload,
        "eventType": "entityUpdated",
        "changeDescription": {
            "fieldsAdded": [
                {"name": "columns"} # missing newValue
            ]
        }
    }
    blocks = template_schema_change(payload)
    assert "Added:" in blocks[2]["text"]["text"]
    assert "[]" in blocks[2]["text"]["text"]

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def test_route_payload_entity_created():
    payload = {"eventType": "entityCreated"}
    blocks = route_payload_to_template(payload)
    assert len(blocks) == 5 # Should use template_entity_created

def test_route_payload_entity_deleted():
    payload = {"eventType": "entityDeleted"}
    blocks = route_payload_to_template(payload)
    assert len(blocks) == 5 # Should use template_entity_deleted

def test_route_payload_test_case_result():
    payload = {"eventType": "testCaseResult"}
    blocks = route_payload_to_template(payload)
    assert len(blocks) == 5 # Should use template_dq_failure

def test_route_payload_ownership_change():
    payload = {
        "eventType": "entityUpdated",
        "changeDescription": {
            "fieldsUpdated": [{"name": "owner"}]
        }
    }
    blocks = route_payload_to_template(payload)
    assert "Changed from" in str(blocks)

def test_route_payload_schema_change():
    payload = {
        "eventType": "entityUpdated",
        "changeDescription": {
            "fieldsAdded": [{"name": "columns"}]
        }
    }
    blocks = route_payload_to_template(payload)
    assert "*Added:*" in str(blocks)

def test_route_payload_generic_update():
    payload = {
        "eventType": "entityUpdated",
        "changeDescription": {
            "fieldsUpdated": [{"name": "description"}]
        }
    }
    blocks = route_payload_to_template(payload)
    # generic returns 4 blocks: header, section, context, actions
    assert len(blocks) == 4

def test_route_payload_unknown():
    payload = {"eventType": "unknownEvent"}
    blocks = route_payload_to_template(payload)
    assert len(blocks) == 4
