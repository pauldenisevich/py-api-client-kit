"""Synchronous client foundation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

import httpx

from api_client_kit.client.headers import merge_headers
from api_client_kit.client.models import RequestContext, ResponseData
from api_client_kit.client.timeouts import TimeoutValue, resolve_timeout
from api_client_kit.client.urls import join_url
from api_client_kit.errors.mapping import _http_error_for_response
from api_client_kit.errors.transport import _transport_error_from_httpx

__all__ = ("SyncClient",)


class _RequestTimeoutUnset:
    """Private sentinel type for omitted per-request timeout values."""


_REQUEST_TIMEOUT_UNSET: Final = _RequestTimeoutUnset()


class SyncClient:
    """Synchronous API client foundation."""

    def __init__(
        self,
        *,
        base_url: str,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue = 5.0,
        transport: httpx.BaseTransport | None = None,
        raise_for_status: bool = True,
    ) -> None:
        if not isinstance(raise_for_status, bool):
            raise TypeError("raise_for_status must be bool")

        self._base_url = join_url(base_url)
        self._default_headers = httpx.Headers(headers or {})
        self._timeout = timeout
        self._transport = transport
        self._raise_for_status = raise_for_status
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

    @property
    def raise_for_status(self) -> bool:
        """Configured HTTP status error policy."""
        return self._raise_for_status

    def close(self) -> None:
        """Close the underlying synchronous HTTP client."""
        self._client.close()

    def __enter__(self) -> SyncClient:
        """Enter the synchronous client context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit the synchronous client context manager."""
        self.close()

    def request(
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
        """Send a synchronous request."""
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

        try:
            raw_response = self._client.request(
                method=context.method,
                url=context.url,
                params=context.params,
                headers=context.headers,
                json=context.json,
                data=context.data,
                timeout=context.timeout,
            )
        except httpx.TransportError as exc:
            raise _transport_error_from_httpx(exc, context) from exc

        response = ResponseData(raw=raw_response)
        if self._raise_for_status:
            error = _http_error_for_response(response, context)
            if error is not None:
                raise error

        return response

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send a synchronous GET request."""
        return self.request(
            "GET",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )

    def post(
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
        """Send a synchronous POST request."""
        return self.request(
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

    def put(
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
        """Send a synchronous PUT request."""
        return self.request(
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

    def patch(
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
        """Send a synchronous PATCH request."""
        return self.request(
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

    def delete(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send a synchronous DELETE request."""
        return self.request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )

    def head(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | httpx.Headers | None = None,
        timeout: TimeoutValue | _RequestTimeoutUnset = _REQUEST_TIMEOUT_UNSET,
        idempotency_key: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> ResponseData:
        """Send a synchronous HEAD request."""
        return self.request(
            "HEAD",
            path,
            params=params,
            headers=headers,
            timeout=timeout,
            idempotency_key=idempotency_key,
            tags=tags,
        )
