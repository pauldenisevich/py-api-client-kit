# Architecture

`api-client-kit` is an opinionated Python toolkit for building robust API clients.

This document describes the current package architecture, public API surface,
internal implementation boundaries, and planned future feature areas.

The project is currently in early development. The core sync/async client
foundation, standalone redaction primitives, package error taxonomy, internal
safe diagnostic-context builder, and internal HTTP status-to-error construction
seam are implemented, while auth, retries, rate-limit handling, pagination, and
observability hooks remain future feature areas.

## Status

Current status:

```text
repository foundation complete
tooling and CI exist
core request and response models exist
URL, header, and timeout request construction utilities exist
synchronous request execution path exists
asynchronous request execution path exists
sync and async convenience methods exist
sync and async client lifecycle support exists
top-level and client subpackage public imports exist
standalone header, diagnostic URL, recursive payload, and bounded body-snippet redaction primitives exist
`ApiClientError`, network errors, HTTP status and decode error types, and
internal status-to-error construction exist
```

## Architectural Goal

The goal of `api-client-kit` is to provide reusable infrastructure primitives for API client development.

A user should be able to build a domain-specific client on top of this package while relying on `api-client-kit` for common client concerns:

* sync and async client foundations
* request and response handling
* authentication
* retry and backoff behavior
* rate-limit handling
* structured errors
* safe redaction
* pagination
* observability hooks
* test-friendly design

The package should stay smaller than a full SDK framework and higher-level than direct `httpx` usage.

## Core Request Pipeline

The long-term request pipeline is:

```text
build request
→ normalize request context
→ apply auth
→ apply rate-limit policy
→ send request
→ retry if needed
→ decode response
→ raise structured errors
→ return response data
→ emit observability hooks
```

Each stage should have a clear responsibility.

The pipeline should be explicit, testable, and safe by default.

## Main Layers

The implemented core runtime foundation currently has these layers:

```text
public client API
  ↓
request options and request context
  ↓
request construction utilities
  ↓
transport execution through httpx
  ↓
response wrapper
```

Future production-oriented feature areas include:

```text
auth providers
  ↓
rate-limit policy
  ↓
retry policy and backoff
  ↓
structured errors and their future client integration
  ↓
pagination helpers
  ↓
observability hooks
```

The current client foundation is intentionally small. Future feature areas
should be documented as available only after they are implemented and tested.

## Public Client Layer

The public client layer provides:

* `SyncClient`
* `AsyncClient`
* common request methods:

  * `get`
  * `post`
  * `put`
  * `patch`
  * `delete`
  * `head`

Sync and async clients should have equivalent behavior unless a difference is intentional and documented.

The public client layer should be small and predictable. It should not hide complex behavior behind unclear global state.

Current implementation note:

* `SyncClient` exists in `api_client_kit.client.sync_client`.
* The `SyncClient` constructor supports `base_url`, `headers`, `timeout`,
  `transport`, and a client-level `raise_for_status: bool = True` policy.
* `base_url` is canonicalized and validated through `join_url`.
* `headers` are stored as client default headers for future requests.
* `timeout` is stored as the client default timeout.
* `transport` can be injected for local tests.
* `raise_for_status` is runtime-validated as a bool, retained as a read-only
  property, and controls package status-error construction in both clients.
* `SyncClient.request()` now exists as the first synchronous request execution
  path.
* `SyncClient.request()` joins the configured `base_url` and request path
  through `join_url`.
* `SyncClient.request()` merges default and request headers through
  `merge_headers`.
* `SyncClient.request()` resolves the client default timeout and per-request
  timeout through `resolve_timeout`.
* `SyncClient.request()` builds an internal `RequestContext`.
* `SyncClient.request()` sends the request through the internal `httpx.Client`.
* `SyncClient.request()` wraps the HTTPX response once as `ResponseData`.
* When `raise_for_status` is true, `SyncClient.request()` passes that wrapper and
  its existing `RequestContext` to the internal status mapper, then raises the
  returned package error or returns the wrapper. When false, it returns the
  wrapper for every HTTP status.
* `SyncClient.close()` exists and closes the underlying synchronous
  `httpx.Client`.
* `SyncClient` supports `with SyncClient(...) as client`.
* The sync context manager returns the `SyncClient` instance from `__enter__`
  and closes the underlying `httpx.Client` on exit.
* Double-close is safe because close delegates to `httpx.Client.close()`.
* `SyncClient` provides synchronous convenience methods: `get`, `post`, `put`,
  `patch`, `delete`, and `head`.
* Each synchronous convenience method delegates to `SyncClient.request()`, so
  request execution still uses the same URL joining, header merging, timeout
  resolution, internal request context creation, transport call, and
  `ResponseData` wrapping behavior.
* `post`, `put`, and `patch` accept `json` and `data` payload arguments.
* `get`, `delete`, and `head` cover normal params, headers, timeout,
  idempotency metadata, and tags usage without body-specific convenience
  parameters.
* Request and convenience methods remain the synchronous request path, including
  when used inside a sync context manager.
* `AsyncClient` exists in `api_client_kit.client.async_client`.
* The `AsyncClient` constructor supports `base_url`, `headers`, `timeout`,
  `transport`, and the same client-level `raise_for_status: bool = True` policy.
* `AsyncClient` canonicalizes and validates `base_url` through `join_url`.
* `AsyncClient` stores `headers` as async client default headers for requests.
* `AsyncClient` stores `timeout` as the async client default timeout for
  requests.
* `AsyncClient` accepts an injected `httpx.AsyncBaseTransport` as an async
  transport seam.
* `AsyncClient` creates an internal `httpx.AsyncClient`.
* `AsyncClient.request()` now exists as the first asynchronous request
  execution path.
* `AsyncClient.request()` joins the configured `base_url` and request path
  through `join_url`.
* `AsyncClient.request()` merges default and request headers through
  `merge_headers`.
* `AsyncClient.request()` resolves the async client default timeout and
  per-request timeout through `resolve_timeout`.
* `AsyncClient.request()` builds an internal `RequestContext`.
* `AsyncClient.request()` sends the request through the internal
  `httpx.AsyncClient`.
* `AsyncClient.request()` wraps the HTTPX response once as `ResponseData`.
* When `raise_for_status` is true, `AsyncClient.request()` passes that wrapper
  and its existing `RequestContext` to the internal status mapper, then raises
  the returned package error or returns the wrapper. When false, it returns the
  wrapper for every HTTP status.
* `AsyncClient.aclose()` exists and closes the underlying asynchronous
  `httpx.AsyncClient`.
* `AsyncClient` supports `async with AsyncClient(...) as client`.
* The async context manager returns the `AsyncClient` instance from
  `__aenter__` and closes the underlying `httpx.AsyncClient` on exit.
* Double `aclose()` is safe because `aclose()` delegates to
  `httpx.AsyncClient.aclose()`.
* `AsyncClient` provides asynchronous convenience methods: `get`, `post`,
  `put`, `patch`, `delete`, and `head`.
* Each asynchronous convenience method delegates to `AsyncClient.request()`, so
  async request execution still uses the same URL joining, header merging,
  timeout resolution, internal request context creation, transport call, and
  `ResponseData` wrapping behavior.
* `post`, `put`, and `patch` accept `json` and `data` payload arguments.
* `get`, `delete`, and `head` cover normal params, headers, timeout,
  idempotency metadata, and tags usage without body-specific convenience
  parameters.
* Request and convenience methods remain the asynchronous request path,
  including when used inside an async context manager.
* Retries, auth, rate limits, hooks, logging, and pagination remain future
  feature areas. Standalone redaction helpers do not run in the client request
  path yet.
* Auth, retry, rate-limit, and hooks constructor parameters are intentionally
  absent until their behavior is implemented.

The `api_client_kit.client` subpackage now exports the stable public
client API:

* `AsyncClient`
* `RequestOptions`
* `ResponseData`
* `SyncClient`

Top-level `api_client_kit` also exports the stable public client API
and version value:

* `AsyncClient`
* `RequestOptions`
* `ResponseData`
* `SyncClient`
* `__version__`

The `api_client_kit.client` implementation modules also define internal request
context and utility helpers. `RequestContext` remains internal and is not
exported from top-level `api_client_kit` or `api_client_kit.client`. URL,
header, and timeout helpers such as `join_url`, `merge_headers`, and
`resolve_timeout` remain module-level utilities and are not top-level exports or
client subpackage exports.

## Request Model Layer

The request model layer defines user-facing and internal request structures.

Current implementation note:

* `RequestOptions` exists as the user-facing request options model.
* Supported fields are `method`, `path`, `params`, `headers`, `json`, `data`,
  `timeout`, `idempotency_key`, and `tags`.
* `RequestContext` exists as the internal normalized request context for the
  client pipeline. It is importable from `api_client_kit.client.models`, but it
  is not part of the public export surface.
* `RequestContext` supports `method`, `url`, `headers`, `params`, `json`,
  `data`, `timeout`, `attempt`, `idempotency_key`, and `tags`.
* `RequestContext.method` is normalized to uppercase, and `attempt` defaults to
  `1`.
* Header merging, timeout resolution, and URL joining are implemented as
  separate utilities.

`RequestOptions` and `ResponseData` are part of the public API surface.
`RequestContext` is internal pipeline state and remains outside the top-level
and client subpackage export surfaces.

The internal request context is the object used by the current sync and async
request paths after URL joining, header merging, and timeout resolution.

## URL Utilities

Current implementation note:

* `join_url` exists in `api_client_kit.client.urls`.
* It joins configured API base URLs with request paths.
* Leading request slashes do not reset or drop the configured base path, so a
  base URL such as `https://api.example.com/v1` and a request path such as
  `/users` produce `https://api.example.com/v1/users`.
* Request-path query strings are preserved.
* Base URLs must be absolute HTTP or HTTPS URLs.
* Base URLs with query strings or fragments are rejected.
* The helper does not send requests.
* The helper does not merge query params dictionaries.
* Header merging and timeout resolution are implemented as separate utilities.

`SyncClient` and `AsyncClient` use this helper to canonicalize and validate
their configured base URL. `SyncClient.request()` and `AsyncClient.request()`
also use this helper to join the configured base URL and per-request path.
Leading request slashes preserve configured base path prefixes.

## Header Utilities

Current implementation note:

* `merge_headers` exists in `api_client_kit.client.headers`.
* It applies client default headers first.
* It applies request headers second, so request headers override defaults.
* Header matching is case-insensitive through `httpx.Headers`.
* Case-insensitive overrides do not preserve duplicate logical headers.
* The helper returns a new `httpx.Headers` object.
* The helper does not mutate input dictionaries or input `httpx.Headers`
  objects.
* Timeout resolution is implemented as a separate utility.

`SyncClient.request()` uses this helper to merge client default headers with
per-request headers before sending through `httpx.Client`.
`AsyncClient.request()` uses this helper to merge async client default headers
with per-request headers before sending through `httpx.AsyncClient`.

## Timeout Utilities

Current implementation note:

* `resolve_timeout` exists in `api_client_kit.client.timeouts`.
* It selects the effective request timeout.
* Omitted per-request timeout values use the client default timeout.
* Explicit per-request timeout values override the client default timeout.
* Explicit per-request `None` is preserved and can override the client default.
* `float`, `httpx.Timeout`, and `None` values are passed through as-is.
* No custom timeout model exists yet.

`SyncClient.request()` uses this helper to select the effective timeout before
sending through `httpx.Client`. `AsyncClient.request()` uses the same helper to
select the effective timeout before sending through `httpx.AsyncClient`.
Omitted request timeouts use the client default, while explicit per-request
values, including `None`, override the default.

## Future Auth Layer

The future auth layer should allow request authentication to be composed and
tested.

Planned concepts:

* auth provider interface
* no-auth/default provider
* API key auth
* bearer token auth
* composite auth

Auth providers should modify request context before transport execution once
auth support exists.

Secrets must not leak into errors, logs, hook payloads, or diagnostics.

## Future Rate-Limit Layer

The future rate-limit layer should provide a standard extension point before
request execution.

Planned concepts:

* rate-limiter protocol
* no-op rate limiter
* future concrete rate-limit implementations

The rate-limit layer is not part of the current implemented foundation. More
advanced rate limiting can be added later.

## Transport Layer

`api-client-kit` uses `httpx` as the HTTP engine.

The current transport layer handles request execution through:

* `httpx.Client` in `SyncClient`
* `httpx.AsyncClient` in `AsyncClient`
* injectable sync and async transports for tests
* `httpx.MockTransport` in integration-style tests

The package should not replace `httpx`.

Instead, it should build API-client infrastructure around it.

## Future Retry and Backoff Layer

The future retry layer should make transient failure handling deterministic and
testable.

Planned concepts:

* retry policy protocol
* default retry policy
* no-retry policy
* retryable status codes
* retryable exceptions
* idempotency-aware behavior
* exponential backoff
* optional deterministic jitter
* injectable sleeper and clock
* `Retry-After` parsing

Tests must not use real sleeps.

Retry behavior is not part of the current implemented foundation. When added,
it should be predictable and easy to inspect.

## Response and Decoding Layer

The response layer should wrap raw `httpx` responses with package-level behavior.

Current implementation note:

* `ResponseData` exists as a lightweight wrapper around `httpx.Response`.
* It stores the wrapped response as `raw`.
* It exposes `status_code`, `headers`, `text`, `content`, and `json()`.
* `status_code`, `headers`, `text`, and `content` delegate directly to the raw
  response.
* `.json()` delegates parsing to `httpx.Response.json()` and translates its
  `json.JSONDecodeError` failures to `DecodeError`.
* Both client request paths wrap an HTTPX response once as `ResponseData` and,
  when `raise_for_status` is true, pass that wrapper and their existing
  `RequestContext` to the internal status mapper. The mapper either returns a
  package status error or `None`, allowing the same wrapper to be returned.

Explicit JSON parsing is not Content-Type gated: valid JSON is returned even
with missing or misleading media types. On failure, the flow is:

```text
ResponseData.json()
        ↓
httpx.Response.json()
        ├── success → actual parsed JSON value
        └── JSONDecodeError
                ↓
         internal safe decode context
                ↓
         DecodeError from the original cause
```

Decode context always contains `status_code`, `content_type`, and a bounded
`body_snippet`; an attached HTTPX request additionally supplies `method` and a
sanitized `url`. Content type is diagnostic only.

## Current Redaction Primitives and Error Foundation

The `api_client_kit.redaction` subpackage provides four standalone reusable
helpers: `redact_headers`, `redact_payload`, `redact_url`, and
`safe_body_snippet`. They redact approved sensitive header, structured-payload,
and query values, while `redact_url` also redacts userinfo and removes URL
fragments. `redact_payload` recurses through mappings, lists, and tuples;
mapping outputs normalize to plain dictionaries. `safe_body_snippet` composes
`redact_payload` for eligible valid JSON and otherwise provides a bounded text
or binary diagnostic representation. They are used by the internal HTTP status
mapping for error diagnostics, but are not integrated with clients, logs, or
hooks.

`api_client_kit.errors.ApiClientError` is the implemented root package exception
foundation. It accepts a safe message and optional already-prepared diagnostic
context. Its automatic string representation is the message only, and its
representation is the runtime class name plus the message; neither renders
context. The base class does not sanitize arbitrary supplied context.

The current package error taxonomy is:

```text
ApiClientError
├── NetworkError
│   └── TimeoutError
├── HttpStatusError
│   ├── AuthenticationError
│   ├── AuthorizationError
│   ├── NotFoundError
│   ├── ConflictError
│   ├── ValidationError
│   ├── RateLimitError
│   └── ServerError
└── DecodeError
```

`NetworkError` and `TimeoutError` inherit the base safe message/context
representation behavior unchanged. Their definitions contain no HTTPX mapping
logic, and clients do not raise them yet.

`HttpStatusError` requires and retains the package `ResponseData` supplied to
its constructor, preserving object identity. The explicit raw HTTPX escape hatch
is `error.response.raw`; the exception has no direct raw-response alias.
Responses and inherited context are excluded from automatic `str()` and
`repr()` rendering. One internal mapping module constructs an HTTP error for a
`ResponseData` status as follows:

```text
ResponseData.status_code
        ↓
single internal status mapping
        ↓
correct HttpStatusError subtype
        +
_build_error_context(...)
        ↓
fully constructed package HTTP error
```

The exact mapping is 401 to `AuthenticationError`, 403 to
`AuthorizationError`, 404 to `NotFoundError`, 409 to `ConflictError`, 422 to
`ValidationError`, and 429 to `RateLimitError`. Statuses from 500 through 599
map to `ServerError`; all other statuses at least 400 map to `HttpStatusError`.
Statuses below 400 produce no error. The mapping is internal and is shared by
both client request paths.

`DecodeError` directly subclasses `ApiClientError`, rather than
`HttpStatusError`,
because decoding failures are independent of status classification. It requires
the package `ResponseData` wrapper and retains the supplied wrapper by identity.
The explicit raw HTTPX path is `error.response.raw`. Neither the attached response
nor optional context is included in automatic `str()` or `repr()` output.
`ResponseData.json()` uses `DecodeError` as its stable package failure contract
for standard-library `json.JSONDecodeError` parser failures. It preserves the
same package response by identity and chains the original parser exception.

Future error concepts:

* HTTPX-to-package transport mapping and client integration

HTTPX-to-package transport mapping and client/error integration remain future
work.

## Future Pagination Layer

The future pagination layer should provide reusable helpers for common API
pagination patterns.

Planned concepts:

* page model
* paginator protocol
* cursor pagination
* page-number pagination
* Link header pagination
* sync iteration helpers
* async iteration helpers

Pagination helpers should avoid hard-coding one vendor's response shape into the
core.

## Future Observability Layer

The future observability layer should let users inspect client behavior without
coupling the package to a specific metrics, logging, or tracing system.

Planned concepts:

* hooks protocol
* no-op hooks
* hook context models
* before-request events
* after-response events
* retry events
* error events
* rate-limit wait events
* redaction-safe logging hooks

Hook payloads must follow the same redaction rules as errors and logs once hooks
exist.

## Package Structure

Current implemented package structure:

```text
api_client_kit/
  __init__.py
  client/
    __init__.py
    models.py
    sync_client.py
    async_client.py
    urls.py
    headers.py
    timeouts.py
  redaction/
    __init__.py
    bodies.py
    headers.py
    payloads.py
    urls.py
  errors/
    __init__.py
    base.py
    context.py
    decode.py
    http.py
    mapping.py
    network.py
  py.typed

tests/
  unit/
  integration/
```

The `api_client_kit/client/` modules contain the implemented core runtime client
foundation and supporting request construction utilities. The `redaction/`
modules provide standalone reusable redaction primitives. The `errors/`
subpackage currently provides `ApiClientError`, `NetworkError`, `TimeoutError`,
`HttpStatusError`, its specialized HTTP status subclasses, `DecodeError`, an
internal safe diagnostic-context builder, and an internal status mapping factory.
The builder
accepts `RequestContext`, an optional HTTP response, and an attempt number; it
returns sanitized request diagnostics, response status, headers, a bounded body
snippet, and optional structured JSON diagnostics when a response exists. The
payload diagnostic is eligible only for `application/json` and
`application/*+json` media types (including parameters), is parsed from the
already-sanitized bounded snippet, and is omitted if that parse fails. This
best-effort enrichment never changes the mapped HTTP status error or produces a
`DecodeError`. The mapping factory is not exported and constructs status errors
with that context. Both clients pass their existing request context and response
wrapper to it when status raising is enabled.

Future package structure may include modules such as:

```text
api_client_kit/
  auth/
  hooks/
  pagination/
  ratelimits/
  retries/
  transport/
```

The exact structure may evolve as those feature areas are implemented.

Public exports should be intentional and documented.

Internal modules may change more freely than public API exports.

## Testing Architecture

Testing is part of the architecture.

Rules:

* use `pytest`
* do not call real external APIs
* do not require real secrets
* use `httpx.MockTransport` for HTTP behavior tests
* keep retry/backoff tests deterministic
* avoid real sleeps
* test sync and async behavior consistently
* test redaction explicitly

Test categories:

```text
tests/unit/
tests/integration/
```

Unit tests should cover pure logic.

Integration tests should use local transports and test doubles, not external services.

## Dependency Policy

Runtime dependencies should stay minimal.

Current runtime dependency baseline:

```text
httpx
```

Development dependencies belong in the optional `dev` dependency group.

Do not add runtime dependencies casually. Every runtime dependency increases the installation footprint for package users.

## Sync and Async Parity

Sync and async clients should share the same conceptual behavior.

Current sync and async parity applies to:

* request construction
* base URL handling
* default and per-request header handling
* default and per-request timeout handling
* request execution through `httpx`
* convenience methods
* response wrapping
* HTTP status mapping and disabled-policy pass-through
* safe status diagnostics and response/raw-response ownership
* lifecycle support

Future sync and async parity should also apply to:

* auth behavior
* retry behavior
* rate-limit behavior
* pagination
* hooks

Implementation may differ internally, but user-facing behavior should be consistent.

## Public API Policy

The top-level `api_client_kit` package namespace is the primary public
compatibility surface.

The following top-level names are public:

* `AsyncClient`
* `RequestOptions`
* `ResponseData`
* `SyncClient`
* `__version__`

The `api_client_kit.client` subpackage also exports the core public client API:

* `AsyncClient`
* `RequestOptions`
* `ResponseData`
* `SyncClient`

Internal implementation modules may change between releases unless their names
are explicitly documented as public API.

`RequestContext` is internal request-pipeline state and is not part of the
public API.

URL, header, and timeout helpers such as `join_url`, `merge_headers`, and
`resolve_timeout` are currently module-level implementation utilities. They are
not top-level exports and are not exported from `api_client_kit.client`.

Public API changes are compatibility-affecting changes and should be reflected
in release notes and versioning decisions.

Runtime behavior, structured errors, retries, auth, rate limits, hooks, logging,
and pagination remain separate feature areas. Standalone redaction primitives do
not imply automatic runtime integration.

## Non-Goals

`api-client-kit` is not intended to be:

* a full SDK generator
* an OpenAPI code generator
* a replacement for `httpx`
* a web framework
* a credential vault
* a distributed rate limiter
* a schema validation framework
* a full tracing or metrics framework

The project should provide clean API-client infrastructure primitives first.

## Architecture Evolution

This document should evolve with the package.

When a major runtime feature is implemented, update this document and the feature-specific docs.

Feature-specific docs may include:

* `auth.md`
* `errors.md`
* `retries.md`
* `ratelimits.md`
* `pagination.md`
* `security-and-redaction.md`

Do not document planned behavior as available until it is implemented and tested.
