"""Package-defined HTTP status error types."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from api_client_kit.errors.base import ApiClientError

if TYPE_CHECKING:
    from api_client_kit.client.models import ResponseData

__all__ = (  # noqa: RUF022
    "HttpStatusError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
)


class HttpStatusError(ApiClientError):
    """Base exception for HTTP status failures."""

    def __init__(
        self,
        message: str,
        *,
        response: ResponseData,
        context: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize an HTTP failure with its package response."""
        super().__init__(message, context=context)
        self._response = response

    @property
    def response(self) -> ResponseData:
        """Return the package response associated with the HTTP failure."""
        return self._response


class AuthenticationError(HttpStatusError):
    """Exception for HTTP authentication failures."""


class AuthorizationError(HttpStatusError):
    """Exception for HTTP authorization failures."""


class NotFoundError(HttpStatusError):
    """Exception for HTTP resource-not-found failures."""


class ConflictError(HttpStatusError):
    """Exception for HTTP conflict failures."""


class ValidationError(HttpStatusError):
    """Exception for HTTP validation failures."""


class RateLimitError(HttpStatusError):
    """Exception for HTTP rate-limit failures."""


class ServerError(HttpStatusError):
    """Exception for HTTP server failures."""
