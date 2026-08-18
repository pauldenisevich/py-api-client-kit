"""Sensitive HTTP header redaction."""

from __future__ import annotations

from collections.abc import Mapping

import httpx

__all__ = ("redact_headers",)

_REDACTED = "<redacted>"
_SENSITIVE_HEADER_NAMES = frozenset(
    {
        "authorization",
        "proxy-authorization",
        "cookie",
        "set-cookie",
        "x-api-key",
        "api-key",
        "x-auth-token",
        "x-access-token",
    }
)


def redact_headers(headers: Mapping[str, str] | httpx.Headers) -> httpx.Headers:
    """Return a new header collection with known sensitive values redacted."""
    return httpx.Headers(
        [
            (name, _REDACTED if name.lower() in _SENSITIVE_HEADER_NAMES else value)
            for name, value in httpx.Headers(headers).multi_items()
        ]
    )


def _sensitive_header_values(headers: Mapping[str, str] | httpx.Headers) -> tuple[str, ...]:
    """Return raw values for headers governed by this module's redaction policy."""
    return tuple(
        value
        for name, value in httpx.Headers(headers).multi_items()
        if name.lower() in _SENSITIVE_HEADER_NAMES and value
    )
