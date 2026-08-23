"""Request and response model primitives."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from api_client_kit.errors.context import _build_decode_error_context
from api_client_kit.errors.decode import DecodeError

__all__ = ("RequestOptions", "ResponseData")


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


@dataclass(frozen=True, slots=True)
class ResponseData:
    """Lightweight wrapper around an httpx response."""

    raw: httpx.Response

    @property
    def status_code(self) -> int:
        return self.raw.status_code

    @property
    def headers(self) -> httpx.Headers:
        return self.raw.headers

    @property
    def text(self) -> str:
        return self.raw.text

    @property
    def content(self) -> bytes:
        return self.raw.content

    def json(self) -> Any:
        try:
            return self.raw.json()
        except json.JSONDecodeError as exc:
            raise DecodeError(
                "Failed to decode response as JSON",
                response=self,
                context=_build_decode_error_context(self),
            ) from exc
