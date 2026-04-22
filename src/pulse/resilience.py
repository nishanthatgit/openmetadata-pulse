"""Resilience infrastructure for OpenMetadata Pulse.

Provides globally configured circuit breakers and error formatting utilities
to ensure the bot does not crash and handles transient failures gracefully.
"""

from typing import Any

import pybreaker
import structlog
from slack_sdk.errors import SlackApiError

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Circuit Breakers
# ---------------------------------------------------------------------------

# Circuit breaker for OpenMetadata API
# Trips after 5 failures, attempts a reset after 60 seconds
om_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    state_storage=pybreaker.CircuitMemoryStorage(),
    name="openmetadata",
)

# Circuit breaker for Slack API
# Trips after 5 failures, attempts a reset after 60 seconds
slack_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    state_storage=pybreaker.CircuitMemoryStorage(),
    name="slack",
)

def is_retryable_slack_error(exc: Exception) -> bool:
    """Return True if the SlackApiError should trigger a retry."""
    if not isinstance(exc, SlackApiError):
        return False
    # Slack API returns 429 for rate limits, or 5xx for server errors
    status = exc.response.status_code if exc.response else 500
    return status == 429 or status >= 500


# ---------------------------------------------------------------------------
# Error Envelope
# ---------------------------------------------------------------------------

def error_envelope(action: str, exc: Exception, **kwargs: Any) -> dict[str, Any]:
    """Standardize error logging shape for unhandled exceptions.
    
    Args:
        action: What the system was trying to do (e.g. "webhook_processing").
        exc: The exception that was caught.
        **kwargs: Additional context variables to log.
    
    Returns:
        A dictionary representation of the error.
    """
    error_payload = {
        "action": action,
        "error_type": exc.__class__.__name__,
        "message": str(exc),
        "context": kwargs,
    }
    logger.error("pulse_error", **error_payload, exc_info=True)
    return error_payload
