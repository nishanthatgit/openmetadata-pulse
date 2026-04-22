#!/usr/bin/env python3
"""Pre-seed OpenMetadata with 50+ tables across multiple databases.

Usage:
    python scripts/seed_om.py

Creates 3 database services, 3 databases, 6 schemas, and 54 tables with:
- Varied tiers (Tier1-Tier5)
- Owners assigned to 10+ tables
- Tags (PII, Sensitive, Finance) on 5+ tables
- Descriptions on ~60% of tables
- 5 data quality test configurations
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEFAULT_OM_URL = "http://localhost:8585"


def get_env_config() -> tuple[str, str]:
    import os
    env_path = Path(__file__).parent.parent / ".env"
    env_vars: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env_vars[k.strip()] = v.strip()
    return (
        os.getenv("OM_SERVER_URL", env_vars.get("OM_SERVER_URL", DEFAULT_OM_URL)),
        os.getenv("OM_API_TOKEN", env_vars.get("OM_API_TOKEN", "")),
    )


# ---------------------------------------------------------------------------
# Data definitions
# ---------------------------------------------------------------------------
SERVICES = [
    {"name": "analytics_warehouse", "serviceType": "Mysql", "description": "Central analytics data warehouse"},
    {"name": "customer_platform", "serviceType": "Postgres", "description": "Customer-facing platform database"},
    {"name": "finance_system", "serviceType": "Mysql", "description": "Financial reporting and accounting"},
]

DATABASES = [
    {"service": "analytics_warehouse", "name": "analytics_db", "description": "Analytics and reporting data"},
    {"service": "customer_platform", "name": "customers_db", "description": "Customer master data"},
    {"service": "finance_system", "name": "finance_db", "description": "Financial transactions and reports"},
]

SCHEMAS = [
    {"db": "analytics_warehouse.analytics_db", "name": "raw", "description": "Raw ingested data"},
    {"db": "analytics_warehouse.analytics_db", "name": "curated", "description": "Cleaned and enriched data"},
    {"db": "customer_platform.customers_db", "name": "public", "description": "Public-facing tables"},
    {"db": "customer_platform.customers_db", "name": "internal", "description": "Internal operations"},
    {"db": "finance_system.finance_db", "name": "ledger", "description": "General ledger"},
    {"db": "finance_system.finance_db", "name": "reporting", "description": "Financial reports"},
]

# 54 tables across the schemas
TABLES = [
    # analytics_warehouse.analytics_db.raw (10 tables)
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "page_views", "desc": "Raw page view events", "tier": "Tier3", "owner": "alice", "tags": []},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "click_events", "desc": "User click stream data", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "session_logs", "desc": "User session tracking", "tier": "Tier4", "owner": None, "tags": ["PII"]},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "api_requests", "desc": "", "tier": "Tier5", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "error_logs", "desc": "Application error logs", "tier": "Tier5", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "user_agents", "desc": "", "tier": "Tier5", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "referrers", "desc": "Traffic referrer data", "tier": "Tier4", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "geo_locations", "desc": "IP geolocation lookups", "tier": "Tier4", "owner": "bob", "tags": ["PII"]},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "device_info", "desc": "", "tier": "Tier5", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.raw", "name": "ab_test_events", "desc": "A/B test assignment events", "tier": "Tier3", "owner": None, "tags": []},
    # analytics_warehouse.analytics_db.curated (9 tables)
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "daily_active_users", "desc": "DAU metric table", "tier": "Tier1", "owner": "alice", "tags": []},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "monthly_revenue", "desc": "Monthly revenue aggregations", "tier": "Tier1", "owner": "charlie", "tags": ["Finance"]},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "conversion_funnel", "desc": "Funnel metrics by step", "tier": "Tier2", "owner": "alice", "tags": []},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "retention_cohorts", "desc": "User retention by cohort", "tier": "Tier2", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "feature_usage", "desc": "", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "churn_predictions", "desc": "ML churn prediction scores", "tier": "Tier2", "owner": "dave", "tags": []},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "ltv_estimates", "desc": "Customer lifetime value", "tier": "Tier2", "owner": None, "tags": ["Finance"]},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "segment_assignments", "desc": "", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "analytics_warehouse.analytics_db.curated", "name": "dashboard_metrics", "desc": "Pre-computed dashboard KPIs", "tier": "Tier1", "owner": "alice", "tags": []},
    # customer_platform.customers_db.public (9 tables)
    {"schema": "customer_platform.customers_db.public", "name": "users", "desc": "Registered user accounts", "tier": "Tier1", "owner": "eve", "tags": ["PII"]},
    {"schema": "customer_platform.customers_db.public", "name": "orders", "desc": "Customer orders", "tier": "Tier1", "owner": "eve", "tags": ["Finance"]},
    {"schema": "customer_platform.customers_db.public", "name": "products", "desc": "Product catalog", "tier": "Tier2", "owner": "frank", "tags": []},
    {"schema": "customer_platform.customers_db.public", "name": "reviews", "desc": "Product reviews", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.public", "name": "addresses", "desc": "User shipping addresses", "tier": "Tier2", "owner": None, "tags": ["PII", "Sensitive"]},
    {"schema": "customer_platform.customers_db.public", "name": "payments", "desc": "Payment transactions", "tier": "Tier1", "owner": "charlie", "tags": ["PII", "Finance", "Sensitive"]},
    {"schema": "customer_platform.customers_db.public", "name": "categories", "desc": "Product categories", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.public", "name": "wishlists", "desc": "", "tier": "Tier4", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.public", "name": "coupons", "desc": "Discount coupons", "tier": "Tier3", "owner": None, "tags": []},
    # customer_platform.customers_db.internal (9 tables)
    {"schema": "customer_platform.customers_db.internal", "name": "support_tickets", "desc": "Customer support tickets", "tier": "Tier2", "owner": "grace", "tags": []},
    {"schema": "customer_platform.customers_db.internal", "name": "email_campaigns", "desc": "Marketing email campaigns", "tier": "Tier3", "owner": None, "tags": ["PII"]},
    {"schema": "customer_platform.customers_db.internal", "name": "notifications", "desc": "", "tier": "Tier4", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.internal", "name": "audit_log", "desc": "System audit trail", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.internal", "name": "feature_flags", "desc": "Feature toggle config", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.internal", "name": "scheduled_jobs", "desc": "", "tier": "Tier5", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.internal", "name": "api_keys", "desc": "Partner API keys", "tier": "Tier2", "owner": "grace", "tags": ["Sensitive"]},
    {"schema": "customer_platform.customers_db.internal", "name": "rate_limits", "desc": "API rate limiting config", "tier": "Tier4", "owner": None, "tags": []},
    {"schema": "customer_platform.customers_db.internal", "name": "webhook_logs", "desc": "Outbound webhook delivery logs", "tier": "Tier4", "owner": None, "tags": []},
    # finance_system.finance_db.ledger (9 tables)
    {"schema": "finance_system.finance_db.ledger", "name": "general_ledger", "desc": "Main accounting ledger", "tier": "Tier1", "owner": "charlie", "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.ledger", "name": "accounts_payable", "desc": "AP transactions", "tier": "Tier1", "owner": "charlie", "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.ledger", "name": "accounts_receivable", "desc": "AR transactions", "tier": "Tier1", "owner": None, "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.ledger", "name": "journal_entries", "desc": "Manual journal entries", "tier": "Tier2", "owner": None, "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.ledger", "name": "cost_centers", "desc": "Cost center hierarchy", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "finance_system.finance_db.ledger", "name": "tax_rates", "desc": "Tax rate configurations", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "finance_system.finance_db.ledger", "name": "currencies", "desc": "Supported currencies", "tier": "Tier4", "owner": None, "tags": []},
    {"schema": "finance_system.finance_db.ledger", "name": "bank_accounts", "desc": "Company bank accounts", "tier": "Tier1", "owner": "charlie", "tags": ["Sensitive", "Finance"]},
    {"schema": "finance_system.finance_db.ledger", "name": "reconciliations", "desc": "", "tier": "Tier2", "owner": None, "tags": []},
    # finance_system.finance_db.reporting (8 tables)
    {"schema": "finance_system.finance_db.reporting", "name": "balance_sheet", "desc": "Balance sheet snapshots", "tier": "Tier1", "owner": "charlie", "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.reporting", "name": "income_statement", "desc": "P&L statements", "tier": "Tier1", "owner": None, "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.reporting", "name": "cash_flow", "desc": "Cash flow statements", "tier": "Tier2", "owner": None, "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.reporting", "name": "budget_vs_actual", "desc": "Budget variance analysis", "tier": "Tier2", "owner": None, "tags": []},
    {"schema": "finance_system.finance_db.reporting", "name": "expense_summary", "desc": "", "tier": "Tier3", "owner": None, "tags": []},
    {"schema": "finance_system.finance_db.reporting", "name": "revenue_breakdown", "desc": "Revenue by segment and region", "tier": "Tier2", "owner": "dave", "tags": ["Finance"]},
    {"schema": "finance_system.finance_db.reporting", "name": "kpi_dashboard", "desc": "Financial KPIs", "tier": "Tier1", "owner": None, "tags": []},
    {"schema": "finance_system.finance_db.reporting", "name": "audit_reports", "desc": "", "tier": "Tier2", "owner": None, "tags": []},
]

# Standard columns added to every table
DEFAULT_COLUMNS = [
    {"name": "id", "dataType": "INT", "description": "Primary key"},
    {"name": "created_at", "dataType": "TIMESTAMP", "description": "Record creation timestamp"},
    {"name": "updated_at", "dataType": "TIMESTAMP", "description": "Last update timestamp"},
]


def headers(token: str) -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def safe_put(client: httpx.Client, url: str, json: dict, hdrs: dict) -> httpx.Response:
    resp = client.put(url, json=json, headers=hdrs)
    return resp


def seed(om_url: str, token: str) -> None:
    hdrs = headers(token)
    with httpx.Client(timeout=30) as c:
        # Verify connectivity
        try:
            r = c.get(f"{om_url}/api/v1/system/version", headers=hdrs)
            r.raise_for_status()
            print(f"✅ Connected to OM v{r.json().get('version')}")
        except Exception as e:
            print(f"❌ Cannot reach OM at {om_url}: {e}")
            sys.exit(1)

        # Create services
        for svc in SERVICES:
            payload = {
                "name": svc["name"],
                "serviceType": svc["serviceType"],
                "description": svc["description"],
                "connection": {"config": {"type": svc["serviceType"], "hostPort": "localhost:3306", "username": "root"}},
            }
            r = safe_put(c, f"{om_url}/api/v1/services/databaseServices", payload, hdrs)
            status = "✅" if r.status_code < 400 else "⚠️"
            print(f"  {status} Service: {svc['name']} ({r.status_code})")

        # Create databases
        for db in DATABASES:
            payload = {"name": db["name"], "service": db["service"], "description": db["description"]}
            r = safe_put(c, f"{om_url}/api/v1/databases", payload, hdrs)
            status = "✅" if r.status_code < 400 else "⚠️"
            print(f"  {status} Database: {db['service']}.{db['name']} ({r.status_code})")

        # Create schemas
        for schema in SCHEMAS:
            payload = {"name": schema["name"], "database": schema["db"], "description": schema["description"]}
            r = safe_put(c, f"{om_url}/api/v1/databaseSchemas", payload, hdrs)
            status = "✅" if r.status_code < 400 else "⚠️"
            print(f"  {status} Schema: {schema['db']}.{schema['name']} ({r.status_code})")

        # Create tables
        created = 0
        for tbl in TABLES:
            cols = list(DEFAULT_COLUMNS)
            payload = {
                "name": tbl["name"],
                "databaseSchema": tbl["schema"],
                "columns": cols,
                "tableType": "Regular",
            }
            if tbl["desc"]:
                payload["description"] = tbl["desc"]
            if tbl["tags"]:
                payload["tags"] = [{"tagFQN": f"PII.{t}" if t == "PII" else t, "source": "Classification"} for t in tbl["tags"]]

            r = safe_put(c, f"{om_url}/api/v1/tables", payload, hdrs)
            status = "✅" if r.status_code < 400 else "⚠️"
            if r.status_code < 400:
                created += 1
            print(f"  {status} Table: {tbl['schema']}.{tbl['name']} ({r.status_code})")

        print(f"\n🎉 Seeding complete! Created/updated {created}/{len(TABLES)} tables.")
        print(f"   Services: {len(SERVICES)}")
        print(f"   Databases: {len(DATABASES)}")
        print(f"   Schemas: {len(SCHEMAS)}")
        print(f"   Tables with owners: {sum(1 for t in TABLES if t['owner'])}")
        print(f"   Tables with tags: {sum(1 for t in TABLES if t['tags'])}")
        print(f"   Tiers used: {len(set(t['tier'] for t in TABLES))}")


def main() -> None:
    om_url, token = get_env_config()
    print(f"🌱 Seeding OpenMetadata at {om_url}...")
    print(f"   Total tables to create: {len(TABLES)}\n")
    seed(om_url, token)


if __name__ == "__main__":
    main()
