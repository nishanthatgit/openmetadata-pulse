"""FastAPI application — composes webhook receiver + dashboard API."""

from __future__ import annotations

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pulse.config import settings
from pulse.dashboard_api import router as dashboard_router
from pulse.webhook_receiver import router as webhook_router

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="OpenMetadata Pulse API",
    version="0.1.0",
    description="Webhook receiver and dashboard API for OpenMetadata Pulse.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {"service": "openmetadata-pulse", "version": "0.1.0"}


def main() -> None:
    """Run the API server."""
    logger.info("starting_api_server", port=settings.api_port)
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port)


if __name__ == "__main__":
    main()
