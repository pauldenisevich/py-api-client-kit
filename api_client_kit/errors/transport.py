"""Internal HTTPX transport-error translation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from api_client_kit.errors.context import _build_error_context
from api_client_kit.errors.network import NetworkError, TimeoutError  # noqa: A004

if TYPE_CHECKING:
    from api_client_kit.client.models import RequestContext


def _transport_error_from_httpx(
    exc: httpx.TransportError,
    request: RequestContext,
    *,
    attempt: int = 1,
) -> NetworkError:
    """Construct the package error corresponding to an HTTPX transport error."""
    context = _build_error_context(request, attempt=attempt)
    if isinstance(exc, httpx.TimeoutException):
        return TimeoutError("HTTP request timed out", context=context)
    return NetworkError("HTTP transport failed", context=context)
