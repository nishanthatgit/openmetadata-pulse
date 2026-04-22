# Webhook Configuration Guide

This guide explains how to configure OpenMetadata to send change events to the Pulse API.

## Automated Setup (Recommended)

Run the configuration script after OpenMetadata is up:

```bash
# For local development (OM and Pulse both on localhost)
python scripts/configure_webhook.py

# For Docker Compose setup (services on Docker network)
python scripts/configure_webhook.py --docker
```

The script will:
1. Verify OpenMetadata is reachable
2. Check if the webhook already exists (idempotent)
3. Create or update the webhook with the correct endpoint
4. Enable all relevant event types

## Manual Setup via OM UI

If you prefer to configure the webhook manually:

### Step 1: Open OpenMetadata Settings

1. Navigate to `http://localhost:8585` in your browser
2. Log in with admin credentials (default: `admin` / `admin`)
3. Click the **⚙️ Settings** gear icon in the left sidebar
4. Under **Integrations**, click **Webhooks**

### Step 2: Create a New Webhook

1. Click **+ Add Webhook** button
2. Fill in the following fields:

| Field | Value |
|-------|-------|
| **Name** | `pulse-webhook` |
| **Display Name** | `Pulse Webhook` |
| **Endpoint URL** | `http://pulse-api:8000/webhook` (Docker) or `http://localhost:8000/webhook` (local) |
| **Description** | Sends OM change events to Pulse API |
| **Batch Size** | `10` |
| **Timeout** | `10` seconds |
| **Enabled** | ✅ Yes |

### Step 3: Configure Event Filters

Enable the following event types:

- ✅ `entityCreated` — Triggers when new tables, databases, etc. are created
- ✅ `entityUpdated` — Triggers when entity metadata changes (owner, tags, description)
- ✅ `entityDeleted` — Triggers when entities are deleted
- ✅ `entitySoftDeleted` — Triggers when entities are soft-deleted
- ✅ `testCaseResult` — Triggers when data quality test results are recorded

### Step 4: Save and Test

1. Click **Save** to create the webhook
2. Go to OpenMetadata and create a new table or modify an existing entity
3. Check the Pulse API logs for the webhook event:

```bash
# Check logs
docker-compose logs -f pulse-api | grep webhook_received
```

You should see log entries like:
```
event_type=entityCreated entity_type=table
```

## Endpoint URLs

| Environment | Webhook Endpoint URL |
|-------------|---------------------|
| **Docker Compose** | `http://pulse-api:8000/webhook` |
| **Local Development** | `http://localhost:8000/webhook` |

> **Note:** When running in Docker Compose, use the Docker service name (`pulse-api`)
> instead of `localhost`, as OM and Pulse are on the same Docker network.

## Troubleshooting

### Webhook not receiving events

1. **Verify OM is running:**
   ```bash
   curl http://localhost:8585/api/v1/system/version
   ```

2. **Verify Pulse API is running:**
   ```bash
   curl http://localhost:8000/
   ```

3. **Check webhook status in OM:**
   ```bash
   curl http://localhost:8585/api/v1/webhook/name/pulse-webhook
   ```

4. **Check for network issues (Docker):**
   ```bash
   docker-compose exec openmetadata curl http://pulse-api:8000/
   ```

### Common Errors

| Error | Solution |
|-------|----------|
| Connection refused | Ensure Pulse API is running and the port is correct |
| 404 Not Found | Verify the endpoint URL path is `/webhook` |
| Timeout | Increase the webhook timeout in OM settings |
| Auth error | Check `OM_API_TOKEN` is set correctly |
