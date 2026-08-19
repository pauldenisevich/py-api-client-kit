"""Internal HTTP status-to-error construction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api_client_kit.errors.context import _build_error_context
from api_client_kit.errors.http import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    HttpStatusError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)

if TYPE_CHECKING:
    from api_client_kit.client.models import RequestContext, ResponseData


_EXPLICIT_HTTP_ERRORS: dict[int, type[HttpStatusError]] = {
    401: AuthenticationError,
    403: AuthorizationError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
}


def _http_error_for_response(
    response: ResponseData,
    request: RequestContext,
    *,
    attempt: int = 1,
) -> HttpStatusError | None:
    """Construct the package HTTP error for an error response, if any."""
    status_code = response.status_code
    if status_code < 400:
        return None

    error_type = _EXPLICIT_HTTP_ERRORS.get(status_code)
    if error_type is None:
        error_type = ServerError if 500 <= status_code <= 599 else HttpStatusError

    return error_type(
        f"HTTP request failed with status {status_code}",
        response=response,
        context=_build_error_context(request, response=response.raw, attempt=attempt),
    )
