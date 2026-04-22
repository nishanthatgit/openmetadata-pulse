"""Tests for the resilience infrastructure (retries and circuit breakers)."""

import pytest
import pybreaker
from unittest.mock import MagicMock

from slack_sdk.errors import SlackApiError

from pulse.resilience import (
    slack_breaker,
    om_breaker,
    is_retryable_slack_error,
    error_envelope,
)
from pulse.om_client import _is_retryable_om_error
from pulse.exceptions import OMConnectionError, OMClientError


def test_is_retryable_slack_error():
    # 429 Rate Limit
    response = MagicMock()
    response.status_code = 429
    exc_429 = SlackApiError("rate limited", response=response)
    assert is_retryable_slack_error(exc_429) is True

    # 500 Server Error
    response.status_code = 500
    exc_500 = SlackApiError("server error", response=response)
    assert is_retryable_slack_error(exc_500) is True

    # 400 Bad Request
    response.status_code = 400
    exc_400 = SlackApiError("bad request", response=response)
    assert is_retryable_slack_error(exc_400) is False

    # Non-Slack error
    assert is_retryable_slack_error(ValueError("oops")) is False


def test_is_retryable_om_error():
    # OMConnectionError is retryable
    assert _is_retryable_om_error(OMConnectionError("conn error")) is True

    # 502/503/504/429 OMClientError is retryable
    assert _is_retryable_om_error(OMClientError("502 error", status_code=502)) is True
    assert _is_retryable_om_error(OMClientError("429 error", status_code=429)) is True

    # 404 OMClientError is not retryable
    assert _is_retryable_om_error(OMClientError("not found", status_code=404)) is False

    # Other exceptions
    assert _is_retryable_om_error(ValueError("oops")) is False


def test_error_envelope_format():
    exc = ValueError("test exception")
    payload = error_envelope("test_action", exc, extra="data")
    
    assert payload["action"] == "test_action"
    assert payload["error_type"] == "ValueError"
    assert payload["message"] == "test exception"
    assert payload["context"]["extra"] == "data"


@pytest.fixture(autouse=True)
def reset_breakers():
    """Reset circuit breakers before each test."""
    slack_breaker.close()
    om_breaker.close()


def test_slack_circuit_breaker_trips_after_failures():
    """Verify slack_breaker opens after 5 failures."""
    
    @slack_breaker
    def failing_call():
        raise ValueError("simulated failure")
        
    # Cause 5 failures
    for _ in range(5):
        with pytest.raises(ValueError):
            failing_call()
            
    # The 6th call should immediately raise CircuitBreakerError
    with pytest.raises(pybreaker.CircuitBreakerError):
        failing_call()


@pytest.mark.asyncio
async def test_om_circuit_breaker_trips():
    """Verify om_breaker opens after 5 failures."""
    
    @om_breaker
    async def failing_call():
        raise ValueError("simulated failure")
        
    for _ in range(5):
        with pytest.raises(ValueError):
            await failing_call()
            
    with pytest.raises(pybreaker.CircuitBreakerError):
        await failing_call()
