"""Request and response model primitives."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

__all__ = ("RequestOptions",)


# ------------------------------------------------
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
