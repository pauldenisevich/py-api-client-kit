"""URL utilities for client request construction."""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

__all__ = ("join_url",)


def join_url(base_url: str, path: str = "") -> str:
    """Join an API base URL and request path without dropping base path prefixes."""
    base = urlsplit(base_url)
    request = urlsplit(path)

    if not base_url:
        msg = "base_url must not be empty"
        raise ValueError(msg)
    if base.scheme not in {"http", "https"}:
        msg = "base_url must be an absolute HTTP or HTTPS URL"
        raise ValueError(msg)
    if not base.netloc:
        msg = "base_url must include a host"
        raise ValueError(msg)
    if base.query:
        msg = "base_url must not include a query string"
        raise ValueError(msg)
    if base.fragment:
        msg = "base_url must not include a fragment"
        raise ValueError(msg)

    if request.scheme or request.netloc:
        msg = "path must be relative to base_url"
        raise ValueError(msg)
    if request.fragment:
        msg = "path must not include a fragment"
        raise ValueError(msg)

    base_path = base.path.rstrip("/")
    request_path = request.path.strip("/")

    if request_path:
        joined_path = f"{base_path}/{request_path}" if base_path else f"/{request_path}"
    else:
        joined_path = base_path

    return urlunsplit((base.scheme, base.netloc, joined_path, request.query, ""))
