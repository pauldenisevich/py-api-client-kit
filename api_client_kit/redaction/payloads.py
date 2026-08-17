"""Recursive structured payload redaction."""

from __future__ import annotations

from collections.abc import Mapping

__all__ = ("redact_payload",)

_REDACTED = "<redacted>"
_SENSITIVE_PAYLOAD_KEYS = frozenset(
    {
        "token",
        "access_token",
        "refresh_token",
        "api_key",
        "apikey",
        "key",
        "secret",
        "client_secret",
        "password",
        "auth",
        "authorization",
        "cookie",
        "session",
        "session_id",
    }
)


def redact_payload(payload: object) -> object:
    """Return a recursively redacted copy of supported structured payloads."""
    if isinstance(payload, Mapping):
        return {
            key: (
                _REDACTED
                if isinstance(key, str) and key.casefold() in _SENSITIVE_PAYLOAD_KEYS
                else redact_payload(value)
            )
            for key, value in payload.items()
        }
    if isinstance(payload, list):
        return [redact_payload(value) for value in payload]
    if isinstance(payload, tuple):
        return tuple(redact_payload(value) for value in payload)
    return payload
