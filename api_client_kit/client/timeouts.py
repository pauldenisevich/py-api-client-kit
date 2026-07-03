"""Timeout utilities for client request construction."""

from __future__ import annotations

from typing import Final, TypeAlias

import httpx

TimeoutValue: TypeAlias = float | httpx.Timeout | None

__all__ = ("resolve_timeout",)


class _UnsetTimeout:
    """Private sentinel type for omitted per-request timeout values."""


_TIMEOUT_UNSET: Final = _UnsetTimeout()


def resolve_timeout(
    default_timeout: TimeoutValue = None,
    request_timeout: TimeoutValue | _UnsetTimeout = _TIMEOUT_UNSET,
) -> TimeoutValue:
    """Resolve the effective timeout for a request."""
    if request_timeout is _TIMEOUT_UNSET:
        return default_timeout
    return request_timeout
