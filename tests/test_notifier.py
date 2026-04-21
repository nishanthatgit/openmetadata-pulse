"""Tests for the notification engine."""

from pulse.notifier import _format_slack_blocks


def test_format_slack_blocks_schema_change():
    blocks = _format_slack_blocks(":pencil2:", "entityUpdated", "table", "db.schema.users")
    assert len(blocks) == 1
    assert "entityUpdated" in blocks[0]["text"]["text"]
    assert "db.schema.users" in blocks[0]["text"]["text"]


def test_format_slack_blocks_entity_created():
    blocks = _format_slack_blocks(":new:", "entityCreated", "topic", "kafka.orders")
    assert ":new:" in blocks[0]["text"]["text"]
