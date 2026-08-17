"""Package-defined network transport error types."""

from __future__ import annotations

from api_client_kit.errors.base import ApiClientError

__all__ = (
    "NetworkError",
    "TimeoutError",
)


class NetworkError(ApiClientError):
    """Base exception for network transport failures."""


class TimeoutError(NetworkError):  # noqa: A001
    """Exception for network transport timeout failures."""
