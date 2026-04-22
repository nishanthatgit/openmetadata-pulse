"""Custom exceptions for OpenMetadata Pulse."""

from __future__ import annotations


class PulseError(Exception):
    """Base exception for all Pulse errors."""


class OMClientError(PulseError):
    """Raised when an OpenMetadata API call fails.

    Attributes:
        status_code: HTTP status code (if applicable).
        detail: Human-readable error detail.
        url: The URL that was called.
    """

    def __init__(
        self,
        detail: str,
        *,
        status_code: int | None = None,
        url: str = "",
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.url = url
        super().__init__(f"OMClientError({status_code}): {detail} [{url}]")


class OMConnectionError(OMClientError):
    """Raised when the OM server is unreachable."""


class OMAuthError(OMClientError):
    """Raised on 401/403 from the OM server."""


class OMNotFoundError(OMClientError):
    """Raised on 404 from the OM server."""
