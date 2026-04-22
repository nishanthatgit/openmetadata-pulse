#!/usr/bin/env python3
"""Configure OpenMetadata webhook to POST events to the Pulse API.

Usage:
    python scripts/configure_webhook.py [--docker]

    --docker    Use Docker network URL (http://pulse-api:8000/webhook)
                Default uses localhost (http://localhost:8000/webhook)

This script:
1. Authenticates with OpenMetadata using JWT token
2. Checks if a 'pulse-webhook' already exists
3. Creates (or updates) the webhook to point to the Pulse API
4. Enables entityCreated, entityUpdated, entityDeleted, testCaseResult events

Prerequisites:
    - OpenMetadata must be running at OM_SERVER_URL (default: http://localhost:8585)
    - Set OM_API_TOKEN in your .env or environment
"""

from __future__ import annotations

import argparse
import sys

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_OM_URL = "http://localhost:8585"
WEBHOOK_NAME = "pulse-webhook"
LOCAL_ENDPOINT = "http://localhost:8000/webhook"
DOCKER_ENDPOINT = "http://pulse-api:8000/webhook"

# Event types to subscribe to
EVENT_FILTERS = [
    "entityCreated",
    "entityUpdated",
    "entityDeleted",
    "entitySoftDeleted",
    "testCaseResult",
]


def get_env_config() -> tuple[str, str]:
    """Read OM config from environment or .env file."""
    import os
    from pathlib import Path

    # Try loading from .env file
    env_path = Path(__file__).parent.parent / ".env"
    env_vars: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()

    om_url = os.getenv("OM_SERVER_URL", env_vars.get("OM_SERVER_URL", DEFAULT_OM_URL))
    om_token = os.getenv("OM_API_TOKEN", env_vars.get("OM_API_TOKEN", ""))

    return om_url, om_token


def get_auth_headers(token: str) -> dict[str, str]:
    """Build authentication headers."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def check_existing_webhook(
    client: httpx.Client, om_url: str, headers: dict[str, str]
) -> dict | None:
    """Check if the pulse-webhook already exists."""
    try:
        resp = client.get(
            f"{om_url}/api/v1/webhook/name/{WEBHOOK_NAME}",
            headers=headers,
        )
        if resp.status_code == 200:
            return resp.json()
    except httpx.HTTPError:
        pass
    return None


def create_webhook(
    client: httpx.Client,
    om_url: str,
    headers: dict[str, str],
    endpoint: str,
) -> dict:
    """Create the webhook in OpenMetadata."""
    payload = {
        "name": WEBHOOK_NAME,
        "displayName": "Pulse Webhook",
        "description": "Sends OpenMetadata change events to the Pulse API for notifications and dashboard updates.",
        "endpoint": endpoint,
        "eventFilters": [
            {
                "entityType": "all",
                "filters": [
                    {"eventType": evt, "include": ["all"]}
                    for evt in EVENT_FILTERS
                ],
            }
        ],
        "batchSize": 10,
        "timeout": 10,
        "enabled": True,
        "secretKey": "",
    }

    resp = client.post(
        f"{om_url}/api/v1/webhook",
        json=payload,
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


def update_webhook(
    client: httpx.Client,
    om_url: str,
    headers: dict[str, str],
    existing: dict,
    endpoint: str,
) -> dict:
    """Update an existing webhook."""
    existing["endpoint"] = endpoint
    existing["enabled"] = True

    resp = client.put(
        f"{om_url}/api/v1/webhook",
        json=existing,
        headers=headers,
    )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Configure OM webhook for Pulse")
    parser.add_argument(
        "--docker",
        action="store_true",
        help="Use Docker network URL instead of localhost",
    )
    args = parser.parse_args()

    endpoint = DOCKER_ENDPOINT if args.docker else LOCAL_ENDPOINT
    om_url, om_token = get_env_config()
    headers = get_auth_headers(om_token)

    print(f"🔧 Configuring webhook...")
    print(f"   OM URL:    {om_url}")
    print(f"   Endpoint:  {endpoint}")
    print(f"   Events:    {', '.join(EVENT_FILTERS)}")
    print()

    with httpx.Client(timeout=30) as client:
        # Check OM is reachable
        try:
            resp = client.get(f"{om_url}/api/v1/system/version", headers=headers)
            resp.raise_for_status()
            version = resp.json().get("version", "unknown")
            print(f"✅ Connected to OpenMetadata v{version}")
        except httpx.HTTPError as e:
            print(f"❌ Cannot reach OpenMetadata at {om_url}: {e}")
            sys.exit(1)

        # Check if webhook exists
        existing = check_existing_webhook(client, om_url, headers)

        try:
            if existing:
                print(f"📝 Updating existing webhook '{WEBHOOK_NAME}'...")
                result = update_webhook(client, om_url, headers, existing, endpoint)
            else:
                print(f"🆕 Creating webhook '{WEBHOOK_NAME}'...")
                result = create_webhook(client, om_url, headers, endpoint)

            print(f"✅ Webhook configured successfully!")
            print(f"   ID:       {result.get('id', 'N/A')}")
            print(f"   Endpoint: {result.get('endpoint', 'N/A')}")
            print(f"   Enabled:  {result.get('enabled', 'N/A')}")
        except httpx.HTTPStatusError as e:
            print(f"❌ Failed to configure webhook: {e.response.status_code}")
            print(f"   Response: {e.response.text}")
            sys.exit(1)


if __name__ == "__main__":
    main()
