# api-client-kit

[![CI](https://github.com/pauldenisevich/py-api-client-kit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/pauldenisevich/py-api-client-kit/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/api-client-kit.svg)](https://pypi.org/project/api-client-kit/)
[![Python versions](https://img.shields.io/pypi/pyversions/api-client-kit.svg)](https://pypi.org/project/api-client-kit/)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

> Work in progress: `api-client-kit` is under active early development and is not ready for production use yet.

`api-client-kit` is an opinionated Python toolkit for building robust API clients.

It helps developers build clean, reliable, testable clients for third-party APIs, internal APIs, SaaS integrations, data providers, service-to-service APIs, and automation workflows.

The package is not a generated SDK framework. It is not a replacement for `httpx`. It is not only a retry helper.

It is a client engineering kit: a small, composable infrastructure layer for the recurring concerns that appear in real API client development.

## Status

Current status:

```text
public repository
placeholder package published to PyPI
package skeleton exists
local development tooling exists
CI exists
runtime API client implementation not started yet
````

The current PyPI release is:

```text
api-client-kit==0.0.1
```

This release exists to reserve the package name and connect the PyPI project to the public GitHub repository.

The package is not ready for production use.

The first intended usable public release is:

```text
api-client-kit==0.1.0
```

## What Problem This Solves

Many API clients start as a simple request:

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
* duplicated retry logic
* duplicated auth logic
* inconsistent sync and async behavior
* secrets leaking into logs or errors
* hard-to-test network behavior

Without a reusable foundation, every project tends to rebuild these pieces differently.

`api-client-kit` exists to provide shared infrastructure for those concerns.

## The Solution

`api-client-kit` provides reusable primitives for building API clients with consistent behavior around transport, auth, retries, errors, redaction, pagination, hooks, and tests.

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

The goal is to let developers write clean domain-specific endpoint methods while relying on tested infrastructure for lower-level client behavior.

## Planned Capabilities

The package is intended to provide reusable primitives for:

* sync and async API clients
* request and response handling
* authentication providers
* retries and backoff
* rate-limit handling
* structured errors
* safe redaction
* pagination helpers
* observability hooks
* test-friendly API client development

## v0.1.0 Roadmap

Planned v0.1.0 scope includes:

* `SyncClient`
* `AsyncClient`
* request options model
* internal request context
* response wrapper
* URL joining
* header merging
* timeout support
* structured error hierarchy
* safe request/response error context
* header, URL, query, and payload redaction helpers
* API key auth
* bearer token auth
* composite auth
* retry policy interface
* default retry policy
* exponential backoff
* `Retry-After` parsing
* basic rate-limiter interface
* pagination helpers
* observability hook interfaces
* redaction-safe logging hooks
* examples
* public documentation
* CI and release workflow

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

The project focuses on API-client infrastructure primitives first.

## Installation

The placeholder package is published on PyPI:

```bash
pip install api-client-kit==0.0.1
```

For `uv` users:

```bash
uv add api-client-kit==0.0.1
```

This version is not production-ready and does not yet include runtime API client functionality.

The first intended usable public release will be:

```text
api-client-kit==0.1.0
```

## Documentation

Public documentation lives in [`docs/`](docs/).

Start here:

* [Project Positioning](docs/project-positioning.md)
* [Architecture](docs/architecture.md)
* [Local Development](docs/local-development.md)
* [Testing](docs/testing.md)
* [Security and Redaction](docs/security-and-redaction.md)
* [Release Process](docs/release.md)

## Development

This repository is `uv`-first and remains pip-compatible.

For local setup, checks, testing, build commands, and contribution workflow, see:

* [Local Development](docs/local-development.md)
* [Testing](docs/testing.md)
* [Git Policy](docs/git-policy.md)

## Testing Policy

Tests use `pytest`.

Tests must not call real external APIs.

HTTP behavior should be tested with local test doubles such as `httpx.MockTransport`.

Feature work should include tests.

## Python Support

Primary development Python version:

```text
Python 3.12
```

Supported Python versions for the first usable release:

```text
Python >=3.10
```

CI target matrix:

```text
3.10, 3.11, 3.12, 3.13
```

## License

MIT License.
