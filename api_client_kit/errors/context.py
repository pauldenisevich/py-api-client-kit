"""Internal construction of bounded, sanitized diagnostic error context."""

from __future__ import annotations

import json
from contextlib import suppress
from typing import TYPE_CHECKING

from api_client_kit.redaction.bodies import safe_body_snippet
from api_client_kit.redaction.headers import _sensitive_header_values, redact_headers
from api_client_kit.redaction.urls import _sensitive_url_values, redact_url

if TYPE_CHECKING:
    import httpx

    from api_client_kit.client.models import RequestContext


def _build_error_context(
    request: RequestContext,
    *,
    response: httpx.Response | None = None,
    attempt: int = 1,
) -> dict[str, object]:
    """Build package-owned safe diagnostics without retaining transport objects."""
    request_headers = request.headers or {}
    context: dict[str, object] = {
        "method": request.method,
        "url": redact_url(request.url),
        "request_headers": dict(redact_headers(request_headers).items()),
        "attempt": attempt,
    }
    if response is None:
        return context

    known_request_secrets = (
        *_sensitive_header_values(request_headers),
        *_sensitive_url_values(request.url),
    )
    body_snippet = safe_body_snippet(response.content, secret_values=known_request_secrets)
    context.update(
        {
            "status_code": response.status_code,
            "response_headers": dict(redact_headers(response.headers).items()),
            "body_snippet": body_snippet,
        }
    )
    if _is_json_media_type(response.headers.get("content-type")):
        with suppress(json.JSONDecodeError):
            context["payload"] = json.loads(body_snippet)
    return context


def _is_json_media_type(content_type: str | None) -> bool:
    if content_type is None:
        return False
    media_type = content_type.split(";", 1)[0].strip().casefold()
    type_name, separator, subtype = media_type.partition("/")
    return (
        separator == "/"
        and type_name == "application"
        and (subtype == "json" or subtype.endswith("+json"))
    )
