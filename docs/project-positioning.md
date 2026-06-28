# Py-API-Client-Kit: Project Positioning

`api-client-kit` is an opinionated Python toolkit for building robust API clients.

It is designed for developers who need to build clean, reliable, testable clients for third-party APIs, internal APIs, SaaS integrations, data providers, service-to-service APIs, and automation workflows.

The package is not a generated SDK framework. It is not a replacement for `httpx`. It is not only a retry helper.

It is a client engineering kit: a small, composable infrastructure layer for the recurring concerns that appear in real API client development.

## What `api-client-kit` Is

`api-client-kit` provides reusable primitives for building Python API clients.

It helps package authors and application developers avoid repeatedly rebuilding the same fragile client plumbing:

* sync and async HTTP client foundations
* request and response handling
* authentication extension points
* retry and backoff behavior
* rate-limit interfaces
* structured errors
* safe redaction
* pagination helpers
* observability hooks
* test-friendly client patterns

The goal is to let developers write clear domain-specific endpoint methods while relying on consistent infrastructure for transport behavior, resilience, errors, diagnostics, and testing.

A user should be able to build a package-specific client like this:

```python
class ExampleApi:
    def __init__(self, client):
        self._client = client

    def get_customer(self, customer_id: str):
        return self._client.get(f"/customers/{customer_id}")
```

while `api-client-kit` handles the lower-level concerns around request construction, auth, retries, error mapping, redaction, hooks, and testability.

## Target Users

`api-client-kit` is for Python developers who need to build API clients for:

* SaaS integrations
* internal company APIs
* data APIs
* trading and market-data provider APIs
* admin/control-plane APIs
* service-to-service APIs
* automation scripts that need a proper client layer
* open-source packages that wrap external APIs

The target user is not someone who only needs one quick `httpx.get(...)` call.

The target user is someone whose API integration has become important enough that reliability, maintainability, error handling, redaction, retries, pagination, and tests matter.

## The Problem It Solves

Many API clients start simple:

```python
response = httpx.get(url, headers=headers)
```

That works until real API behavior appears:

* `429 Too Many Requests`
* temporary `500`, `502`, `503`, and `504` responses
* network timeouts
* connection errors
* token failures
* expiring credentials
* inconsistent pagination formats
* unstructured error payloads
* duplicated retry code
* duplicated auth code
* inconsistent sync and async behavior
* secrets leaking into logs
* hard-to-test network behavior

Without a shared client foundation, every project solves these problems slightly differently.

That usually leads to clients that are difficult to test, difficult to debug, inconsistent across endpoints, and unsafe around credentials.

`api-client-kit` exists to provide a reusable foundation for these concerns.

## Why Not Just Use `httpx` Directly?

`httpx` is the HTTP engine.

`api-client-kit` uses `httpx` as the transport layer, but it addresses a different level of the API-client stack.

`httpx` gives developers excellent low-level HTTP primitives:

* request sending
* sync and async clients
* connection pooling
* timeouts
* headers
* transports
* streaming
* mocking support

`api-client-kit` builds on top of those primitives to provide API-client infrastructure:

* request context normalization
* authentication composition
* retry decisions
* backoff calculation
* rate-limit handling points
* structured API errors
* redaction-safe diagnostics
* pagination patterns
* observability hooks
* consistent sync and async client behavior
* testable client construction patterns

Using `httpx` directly is still a good choice for simple scripts or one-off requests.

`api-client-kit` is for cases where the integration deserves a real client layer.

## Why This Is Not a Generated SDK Framework

`api-client-kit` is not an OpenAPI generator and does not attempt to generate a complete client from an API schema.

Generated SDKs are useful when an API has a complete, accurate, stable schema and the goal is to generate endpoint methods automatically.

`api-client-kit` serves a different purpose.

It helps developers build hand-written or semi-structured clients where they want control over public API design, endpoint behavior, error handling, retries, auth, pagination, and testing.

The package should make it easier to build a good API client. It should not decide the entire public SDK surface for the user.

## Why This Is Not Just a Retry Library

Retries are only one part of robust API client behavior.

A real client also needs to handle:

* auth injection
* retry eligibility
* idempotency
* backoff
* `Retry-After`
* rate-limit behavior
* structured status errors
* network errors
* timeout errors
* decode errors
* pagination
* redaction
* hooks
* sync and async parity
* tests without real network calls

A generic retry library may help with retry loops, but it usually does not understand the full API-client request lifecycle.

`api-client-kit` treats retries as one part of a broader request pipeline.

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

This pipeline should remain explicit and testable.

Each stage should have a clear responsibility. The project should avoid hidden global state, implicit network behavior, and large framework-style abstractions.

## Design Principles

### Small Core, Composable Pieces

The project should provide useful primitives without becoming a giant framework.

Core pieces should be small, explicit, and independently testable.

Users should be able to adopt the parts they need without buying into an overly rigid architecture.

### Sync and Async Parity

Sync and async clients should behave consistently.

A user building both sync and async clients should not need to learn two different conceptual models.

Where sync and async behavior differs, the difference should be intentional and documented.

### Testability First

API clients must be easy to test without real network calls.

The project should support `httpx.MockTransport` and injectable behavior for retry, backoff, clock, sleep, and transport concerns.

Tests should be deterministic.

Real sleeps and real external API calls do not belong in the test suite.

### Safe by Default

API clients often handle credentials, tokens, cookies, customer data, and sensitive request payloads.

The package must treat redaction as a core concern, not an afterthought.

Errors, logs, hooks, and diagnostics must not leak credentials.

### Minimal Runtime Dependencies

Runtime dependencies should stay small.

`httpx` is the primary runtime dependency.

Development and testing tools should remain optional development dependencies.

### Explicit Public API

Public exports should be intentional.

The package should avoid accidentally exposing internal implementation details as stable API.

Internal modules can evolve as the project matures, but public API changes should be deliberate and documented.

### Documentation from Day One

The project should be understandable from the beginning.

Documentation should explain practical usage, local development, testing, release process, auth, errors, retries, rate limits, pagination, and redaction.

Docs should be engineering-oriented, not marketing fluff.

## What Belongs in This Project

The following concerns belong in `api-client-kit`:

* reusable sync and async client foundations
* request options and request context models
* response wrappers
* URL joining
* header merging
* timeout handling
* auth provider interfaces
* API key auth
* bearer token auth
* composite auth
* structured API errors
* sanitized error context
* safe body snippets
* retry policy protocols
* default retry behavior
* no-retry behavior
* retryable status and exception handling
* exponential backoff
* `Retry-After` parsing
* rate-limit interfaces
* no-op rate limiter
* pagination protocols
* cursor pagination
* page-number pagination
* Link header pagination
* hooks protocols
* null hooks
* redaction-safe logging hooks
* examples and test helpers

These features should be implemented incrementally, with tests and documentation.

## What Does Not Belong in This Project

The project should not become:

* a full SDK generator
* an OpenAPI code generator
* a replacement for `httpx`
* a web framework
* a credential vault
* a distributed rate limiter
* a schema validation framework
* a full tracing or metrics framework

Some integrations may need those tools, but they are outside the core responsibility of `api-client-kit`.

The package should provide clean API-client infrastructure primitives first.

## Positioning Summary

`api-client-kit` sits between raw HTTP clients and full generated SDKs.

It is higher-level than direct `httpx` usage because it provides reusable API-client infrastructure.

It is lower-level than generated SDKs because users still own their domain-specific client design.

It is broader than a retry library because it treats retries as one stage in a complete API-client request lifecycle.

The project should remain focused on helping Python developers build robust, safe, testable API clients without repeatedly rebuilding the same plumbing.
