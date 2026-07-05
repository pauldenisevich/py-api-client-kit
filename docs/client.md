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
plugins, structured package errors, redaction, retries/backoff, `Retry-After`
handling, rate-limit handling, pagination helpers, or observability hooks and
logging.

Non-2xx HTTP responses currently return `ResponseData`; package-level status
errors are not implemented yet.

The package remains work in progress and is not ready for production use.
