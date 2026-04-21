"""Tests for the webhook receiver endpoint."""

import pytest
from fastapi.testclient import TestClient

from pulse.server import app

client = TestClient(app)


def test_webhook_accepts_event():
    payload = {
        "eventType": "entityCreated",
        "entityType": "table",
        "entityFullyQualifiedName": "sample.public.orders",
    }
    resp = client.post("/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "openmetadata-pulse"
