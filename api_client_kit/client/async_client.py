"""Asynchronous client foundation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

import httpx

from api_client_kit.client.headers import merge_headers
from api_client_kit.client.models import RequestContext, ResponseData
from api_client_kit.client.timeouts import TimeoutValue, resolve_timeout
from api_client_kit.client.urls import join_url

__all__ = ("AsyncClient",)


class _RequestTimeoutUnset:
    """Private sentinel type for omitted per-request timeout values."""


_REQUEST_TIMEOUT_UNSET: Final = _RequestTimeoutUnset()


class AsyncClient:
    """Asynchronous API client foundation."""

    def __init__(
        self,
        *,
        base_url: str,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = join_url(base_url)
        self._default_headers = httpx.Headers(headers or {})
        self._timeout = timeout
        self._transport = transport
        self._client = httpx.AsyncClient(transport=transport)

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

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        json: Any | None = None,
        data: Any | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send an asynchronous request."""
        url = join_url(self._base_url, path)
        merged_headers = merge_headers(self._default_headers, headers)

        if timeout is _REQUEST_TIMEOUT_UNSET:
            effective_timeout = resolve_timeout(default_timeout=self._timeout)
        else:
            effective_timeout = resolve_timeout(
                default_timeout=self._timeout,
                request_timeout=timeout,
            )

        context = RequestContext(
            method=method,
            url=url,
            headers=merged_headers,
            params=params,
            json=json,
            data=data,
            timeout=effective_timeout,
            attempt=1,
            idempotency_key=idempotency_key,
            tags=tags,
        )

        response = await self._client.request(
            method=context.method,
            url=context.url,
            params=context.params,
            headers=context.headers,
            json=context.json,
            data=context.data,
            timeout=context.timeout,
        )

        return ResponseData(raw=response)

    async def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send an asynchronous GET request."""
        return await self.request(
            "GET",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )

    async def post(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        json: Any | None = None,
        data: Any | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send an asynchronous POST request."""
        return await self.request(
            "POST",
            path,
            params=params,
            headers=headers,
            json=json,
            data=data,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )

    async def put(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        json: Any | None = None,
        data: Any | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send an asynchronous PUT request."""
        return await self.request(
            "PUT",
            path,
            params=params,
            headers=headers,
            json=json,
            data=data,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )

    async def patch(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        json: Any | None = None,
        data: Any | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send an asynchronous PATCH request."""
        return await self.request(
            "PATCH",
            path,
            params=params,
            headers=headers,
            json=json,
            data=data,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )

    async def delete(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send an asynchronous DELETE request."""
        return await self.request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )

    async def head(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send an asynchronous HEAD request."""
        return await self.request(
            "HEAD",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )
