"""Dashboard REST + SSE endpoints for the community dashboard UI."""

from __future__ import annotations

import structlog
from fastapi import APIRouter

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/dashboard")


@router.get("/health")
async def dashboard_health() -> dict[str, str]:
    """Simple health-check for the dashboard API."""
    return {"status": "ok"}


@router.get("/stats")
async def get_stats() -> dict[str, object]:
    """Return high-level metadata stats for the dashboard."""
    # TODO P2-11: wire to OM search aggregations
    return {
        "total_tables": 0,
        "owned_percentage": 0.0,
        "pii_tagged_percentage": 0.0,
        "dq_pass_rate": 0.0,
    }
