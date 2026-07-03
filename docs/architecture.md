# Architecture

`api-client-kit` is an opinionated Python toolkit for building robust API clients.

This document describes the intended package architecture and request pipeline.

The project is currently in early development. Some architecture described here is planned for the first usable public release and may not be implemented yet.

## Status

Current status:

```text
repository foundation complete
package skeleton exists
client subpackage skeleton exists
tooling and CI exist
runtime client behavior not implemented yet
```

This document should be updated as the implementation becomes real.

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

The intended architecture has these layers:

```text
public client API
  ↓
request options and request context
  ↓
auth providers
  ↓
rate-limit policy
  ↓
transport execution through httpx
  ↓
retry policy and backoff
  ↓
response wrapper and decoding
  ↓
structured errors and redaction
  ↓
pagination helpers
  ↓
observability hooks
```

Not every layer is implemented yet.

## Public Client Layer

The public client layer is expected to provide:

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

The `api_client_kit.client` subpackage currently exists as an importable skeleton only. It does not yet provide `SyncClient`, `AsyncClient`, request models, response wrappers, URL joining, header merging, or network behavior.

## Request Model Layer

The request model layer should define user-facing and internal request structures.

Planned concepts:

* request options model
* internal request context
* normalized method
* resolved URL
* merged headers
* query parameters
* request body
* timeout
* idempotency metadata
* user metadata or tags

The request context should be the object passed through the pipeline.

## Auth Layer

The auth layer should allow request authentication to be composed and tested.

Planned concepts:

* auth provider interface
* no-auth/default provider
* API key auth
* bearer token auth
* composite auth

Auth providers should modify request context before transport execution.

Secrets must not leak into errors, logs, hook payloads, or diagnostics.

## Rate-Limit Layer

The rate-limit layer should provide a standard seam before request execution.

Planned concepts:

* rate-limiter protocol
* no-op rate limiter
* future concrete rate-limit implementations

For v0.1.0, the rate-limit layer is expected to be intentionally small. More advanced rate limiting can be added later.

## Transport Layer

`api-client-kit` uses `httpx` as the HTTP engine.

The transport layer should handle actual request execution through:

* `httpx.Client`
* `httpx.AsyncClient`
* injectable transports for tests
* `httpx.MockTransport` in integration-style tests

The package should not replace `httpx`.

Instead, it should build API-client infrastructure around it.

## Retry and Backoff Layer

The retry layer should make transient failure handling deterministic and testable.

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

Retry behavior should be predictable and easy to inspect.

## Response and Decoding Layer

The response layer should wrap raw `httpx` responses with package-level behavior.

Planned concepts:

* response wrapper
* status code access
* response headers
* raw response access
* text/body access
* JSON helper
* decode error handling

Detailed decoding behavior should be documented once implemented.

## Error and Redaction Layer

Errors should be structured, useful, and safe.

Planned concepts:

* base package error
* HTTP status errors
* network errors
* timeout errors
* decode errors
* safe request context
* safe response context
* sanitized headers
* sanitized URLs
* safe body snippets
* recursive payload redaction helpers

Error messages and representations must not leak credentials.

Redaction is part of the architecture, not an afterthought.

## Pagination Layer

The pagination layer should provide reusable helpers for common API pagination patterns.

Planned concepts:

* page model
* paginator protocol
* cursor pagination
* page-number pagination
* Link header pagination
* sync iteration helpers
* async iteration helpers

Pagination helpers should avoid hard-coding one vendor’s response shape into the core.

## Observability Layer

The observability layer should let users inspect client behavior without coupling the package to a specific metrics, logging, or tracing system.

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

Hook payloads must follow the same redaction rules as errors and logs.

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
  py.typed

tests/
  unit/
  integration/
```

The `api_client_kit/client/` modules are present so Sprint 2 work has stable module boundaries. They intentionally do not implement runtime client behavior yet.

Expected future package structure may include modules such as:

```text
api_client_kit/
  auth/
  errors/
  hooks/
  pagination/
  ratelimits/
  redaction/
  retries/
  transport/
```

The exact structure may evolve as implementation begins.

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

Parity should apply to:

* request construction
* auth behavior
* retry behavior
* rate-limit behavior
* error mapping
* redaction
* pagination
* hooks

Implementation may differ internally, but user-facing behavior should be consistent.

## Public API Policy

Public API should be explicit.

Package-level exports should be intentional.

A name exposed from `api_client_kit.__init__` should be treated as part of the compatibility surface.

Internal helpers should stay internal until they are stable enough to expose.

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
