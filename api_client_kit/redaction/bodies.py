"""Bounded safe HTTP-style body diagnostics."""

from __future__ import annotations

import json
from collections.abc import Iterable

from api_client_kit.redaction.payloads import redact_payload

__all__ = ("safe_body_snippet",)

_EMPTY_BODY_MARKER = "<empty>"
_REDACTED = "<redacted>"
_TRUNCATION_MARKER = "…<truncated>"
_MAX_BODY_SNIPPET_CHARS = 1024
_MAX_STRUCTURED_BODY_SIZE = 65_536


def safe_body_snippet(
    body: str | bytes,
    *,
    secret_values: Iterable[str] = (),
) -> str:
    """Return a bounded, redacted diagnostic rendering of an HTTP-style body."""
    if not isinstance(body, (str, bytes)):
        msg = "body must be str or bytes"
        raise TypeError(msg)

    if isinstance(body, bytes):
        if not body:
            return _EMPTY_BODY_MARKER
        try:
            text = body.decode("utf-8")
        except UnicodeDecodeError:
            return f"<binary body: {len(body)} bytes>"
        structured_eligible = len(body) <= _MAX_STRUCTURED_BODY_SIZE
    else:
        if not body:
            return _EMPTY_BODY_MARKER
        text = body
        structured_eligible = len(text) <= _MAX_STRUCTURED_BODY_SIZE

    secrets = _normalized_secret_values(secret_values)
    if structured_eligible:
        rendered = _render_structured_json(text, secrets)
        return _truncate(rendered)
    return _render_oversized_text(text, secrets)


def _render_structured_json(text: str, secrets: tuple[str, ...]) -> str:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return _scrub_secret_values(text, secrets)

    redacted = redact_payload(parsed)
    scrubbed = _scrub_json_string_values(redacted, secrets)
    return json.dumps(scrubbed, ensure_ascii=False, separators=(",", ":"))


def _normalized_secret_values(secret_values: Iterable[str]) -> tuple[str, ...]:
    return tuple(
        sorted({value for value in secret_values if value}, key=lambda value: (-len(value), value))
    )


def _scrub_json_string_values(value: object, secrets: tuple[str, ...]) -> object:
    if isinstance(value, dict):
        return {
            _scrub_secret_values(key, secrets)
            if isinstance(key, str)
            else key: _scrub_json_string_values(nested_value, secrets)
            for key, nested_value in value.items()
        }
    if isinstance(value, list):
        return [_scrub_json_string_values(nested_value, secrets) for nested_value in value]
    if isinstance(value, str):
        return _scrub_secret_values(value, secrets)
    return value


def _scrub_secret_values(text: str, secrets: tuple[str, ...]) -> str:
    if not secrets:
        return text

    fragments: list[str] = []
    position = 0
    while position < len(text):
        matched_secret = next(
            (secret for secret in secrets if text.startswith(secret, position)), None
        )
        if matched_secret is None:
            fragments.append(text[position])
            position += 1
        else:
            fragments.append(_REDACTED)
            position += len(matched_secret)
    return "".join(fragments)


def _render_oversized_text(text: str, secrets: tuple[str, ...]) -> str:
    prefix_length = _MAX_BODY_SNIPPET_CHARS - len(_TRUNCATION_MARKER)
    prefix = text[:prefix_length]
    lookahead_length = max((len(secret) for secret in secrets), default=0)
    lookahead = text[prefix_length : prefix_length + lookahead_length]
    prefix = _remove_partial_secret_suffix(prefix, lookahead, secrets)
    prefix = _scrub_secret_values(prefix, secrets)
    return f"{prefix[:prefix_length]}{_TRUNCATION_MARKER}"


def _remove_partial_secret_suffix(
    text: str,
    lookahead: str,
    secrets: tuple[str, ...],
) -> str:
    if any(text.endswith(secret) for secret in secrets):
        return text

    for secret in secrets:
        max_prefix_length = min(len(secret) - 1, len(text))
        for prefix_length in range(max_prefix_length, 0, -1):
            if text.endswith(secret[:prefix_length]) and lookahead.startswith(
                secret[prefix_length:]
            ):
                return text[:-prefix_length]
    return text


def _truncate(text: str) -> str:
    if len(text) <= _MAX_BODY_SNIPPET_CHARS:
        return text

    prefix_length = _MAX_BODY_SNIPPET_CHARS - len(_TRUNCATION_MARKER)
    return f"{text[:prefix_length]}{_TRUNCATION_MARKER}"
