"""Sensitive URL, userinfo, and query redaction."""

from __future__ import annotations

from urllib.parse import unquote_plus, urlsplit, urlunsplit

import httpx

__all__ = ("redact_url",)

_REDACTED = "<redacted>"
_SENSITIVE_QUERY_NAMES = frozenset(
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
        "session",
        "session_id",
        "auth",
        "authorization",
    }
)


def redact_url(url: str | httpx.URL) -> str:
    """Return a diagnostic URL with known credential-bearing components redacted."""
    if not isinstance(url, (str, httpx.URL)):
        msg = "url must be str or httpx.URL"
        raise TypeError(msg)

    raw_url = str(url)
    url_without_fragment, _, _ = raw_url.partition("#")
    parts = urlsplit(url_without_fragment)
    netloc = _redact_userinfo(parts.netloc)
    query = _redact_query(parts.query)

    return urlunsplit((parts.scheme, netloc, parts.path, query, ""))


def _redact_query(query: str) -> str:
    if not query:
        return query

    redacted_segments: list[str] = []
    for segment in query.split("&"):
        name, separator, _ = segment.partition("=")
        if separator and unquote_plus(name).casefold() in _SENSITIVE_QUERY_NAMES:
            redacted_segments.append(f"{name}={_REDACTED}")
        else:
            redacted_segments.append(segment)
    return "&".join(redacted_segments)


def _redact_userinfo(netloc: str) -> str:
    userinfo, separator, host = netloc.rpartition("@")
    if not separator:
        return netloc

    _, password_separator, _ = userinfo.partition(":")
    redacted_userinfo = f"{_REDACTED}:{_REDACTED}" if password_separator else _REDACTED
    return f"{redacted_userinfo}@{host}"
