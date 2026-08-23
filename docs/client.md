# Client Usage

## Status

The core sync and async client foundation is available.

The package remains work in progress and is not ready for production use.

## Imports

Use `api_client_kit` as the primary public import surface:

```python
from api_client_kit import AsyncClient, RequestOptions, ResponseData, SyncClient
```

The `api_client_kit.client` subpackage also exports the core client API, but
the top-level namespace is the recommended user-facing import path.

## Synchronous Client

```python
from api_client_kit import SyncClient

with SyncClient(base_url="https://api.example.com") as client:
    response = client.get("/users", params={"limit": 10})

print(response.status_code)
print(response.json())
```

`SyncClient` supports `request()` and the convenience methods `get`, `post`,
`put`, `patch`, `delete`, and `head`. Responses are returned as `ResponseData`
with `status_code`, `headers`, `text`, `content`, and `json()`.

`SyncClient` and `AsyncClient` default to `raise_for_status=True`. Statuses
below 400, including redirects, return `ResponseData`; statuses at least 400
raise the matching package error from `api_client_kit.errors`. For example, a 404 raises
`NotFoundError`, while a 5xx response raises `ServerError`.

```python
from api_client_kit.errors import NotFoundError

try:
    response = client.get("/users/123")
except NotFoundError as error:
    response = error.response
```

Pass `raise_for_status=False` when callers need `ResponseData` for every HTTP
status, including 4xx and 5xx responses.

## JSON Decoding

`ResponseData.json()` explicitly attempts to parse the response body as JSON; it
does not gate parsing on `Content-Type` or status code. Valid JSON returns its
actual Python value, including objects, arrays, scalars, and `null`. Valid JSON
therefore still parses when the media type is missing or misleading.

Invalid JSON, an empty body, and plain-text/non-JSON content raise the stable
package `DecodeError` when `.json()` is called:

```python
from api_client_kit.errors import DecodeError

try:
    payload = response.json()
except DecodeError as error:
    # The original json.JSONDecodeError is available as error.__cause__.
    payload = None
```

The package error is the intended control-flow type; its message is safe and
does not expose parser or server text.

## Transport Errors

`SyncClient` and `AsyncClient` normalize HTTPX transport failures before any
response exists:

```text
httpx.TimeoutException -> TimeoutError
other httpx.TransportError -> NetworkError
```

The package messages are fixed (`HTTP request timed out` and `HTTP transport
failed`), and the original HTTPX exception remains available as `error.__cause__`.
That explicit cause is raw low-level diagnostic state and is not sanitized.
Package error context contains only safe, request-side diagnostics. The
`raise_for_status` setting controls HTTP response-status mapping only; it does
not disable transport-error mapping.

```python
from api_client_kit.errors import NetworkError, TimeoutError
```

## Asynchronous Client

```python
import asyncio

from api_client_kit import AsyncClient


async def main() -> None:
    async with AsyncClient(base_url="https://api.example.com") as client:
        response = await client.get("/users", params={"limit": 10})

    print(response.status_code)
    print(response.json())


asyncio.run(main())
```

`AsyncClient` supports `request()` and the async convenience methods `get`,
`post`, `put`, `patch`, `delete`, and `head`.

## Testing With MockTransport

`SyncClient` and `AsyncClient` accept injectable `httpx` transports. Tests can
use `httpx.MockTransport` to exercise request behavior without real network
calls.

```python
import httpx

from api_client_kit import SyncClient


def handler(request: httpx.Request) -> httpx.Response:
    assert request.url.path == "/users"
    return httpx.Response(200, json={"items": []})


with SyncClient(
    base_url="https://api.example.test",
    transport=httpx.MockTransport(handler),
) as client:
    response = client.get("/users")

assert response.json() == {"items": []}
```

For async tests, pass `httpx.MockTransport` to `AsyncClient` with an async
handler and use the client's async context manager.

## Current Limitations

The current client foundation intentionally does not yet implement auth
plugins, retries/backoff, `Retry-After` handling, rate-limit handling,
pagination helpers, or observability hooks and logging.

Both clients map HTTP statuses at least 400 to package status errors by default;
pass `raise_for_status=False` for explicit non-2xx pass-through.

The package remains work in progress and is not ready for production use.
