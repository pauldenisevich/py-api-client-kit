"""Package-defined response decoding error types."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from api_client_kit.errors.base import ApiClientError

if TYPE_CHECKING:
    from api_client_kit.client.models import ResponseData

__all__ = ("DecodeError",)


class DecodeError(ApiClientError):
    """Exception for failures while decoding a package response."""

    def __init__(
        self,
        message: str,
        *,
        response: ResponseData,
        context: Mapping[str, object] | None = None,
    ) -> None:
        """Initialize a decoding failure with its package response."""
        super().__init__(message, context=context)
        self._response = response

    @property
    def response(self) -> ResponseData:
        """Return the package response associated with the decoding failure."""
        return self._response
