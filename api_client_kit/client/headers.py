"""Header utilities for client request construction."""

from __future__ import annotations

from collections.abc import Mapping

import httpx

__all__ = ("merge_headers",)


def merge_headers(
    default_headers: Mapping[str, str] | httpx.Headers | None = None,
    request_headers: Mapping[str, str] | httpx.Headers | None = None,
) -> httpx.Headers:
    """Merge default and request headers with request headers taking precedence."""
    merged = httpx.Headers(default_headers or {})
    merged.update(httpx.Headers(request_headers or {}))
    return merged
