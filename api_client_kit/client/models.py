"""Request and response model primitives."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

__all__ = ("RequestOptions",)


@dataclass(frozen=True, slots=True)
class RequestOptions:
    """User-facing request options for a client request."""

    method: str
    path: str
    params: Mapping[str, Any] | None = None
    headers: Mapping[str, str] | None = None
    json: Any | None = None
    data: Any | None = None
    timeout: float | httpx.Timeout | None = None
    idempotency_key: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RequestContext:
    """Internal normalized request context for the client pipeline."""

    method: str
    url: str
    headers: Mapping[str, str] | None = None
    params: Mapping[str, Any] | None = None
    json: Any | None = None
    data: Any | None = None
    timeout: float | httpx.Timeout | None = None
    attempt: int = 1
    idempotency_key: str | None = None
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "method", self.method.upper())
