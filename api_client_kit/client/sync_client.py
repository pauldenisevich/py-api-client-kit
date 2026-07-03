"""Synchronous client foundation."""

from __future__ import annotations

from collections.abc import Mapping

import httpx

from api_client_kit.client.timeouts import TimeoutValue
from api_client_kit.client.urls import join_url

__all__ = ("SyncClient",)


class SyncClient:
    """Synchronous API client foundation."""

    def __init__(
        self,
        *,
        base_url: str,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue = 5.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base_url = join_url(base_url)
        self._default_headers = httpx.Headers(headers or {})
        self._timeout = timeout
        self._transport = transport
        self._client = httpx.Client(transport=transport)

    @property
    def base_url(self) -> str:
        """Configured API base URL."""
        return self._base_url

    @property
    def default_headers(self) -> httpx.Headers:
        """Configured default request headers."""
        return httpx.Headers(self._default_headers)

    @property
    def timeout(self) -> TimeoutValue:
        """Configured default request timeout."""
        return self._timeout
