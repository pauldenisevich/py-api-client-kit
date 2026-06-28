# api-client-kit

> Work in progress: this package is under active early development and is not ready for production use yet.

`api-client-kit` is an opinionated Python toolkit for building robust API clients.

It is designed to help developers build clean, reliable, testable clients for third-party APIs, internal APIs, SaaS integrations, data providers, service-to-service APIs, and automation workflows.

The package is not a generated SDK framework. It is not a replacement for `httpx`. It is not only a retry helper.

It is a client engineering kit: a small, composable infrastructure layer for the recurring concerns that appear in real API client development.

## Project Status

Current status:

```text
private repository
Sprint 1 foundation work in progress
package skeleton being created
runtime client implementation not started yet
not published to PyPI yet
```

The first public usable release target is:

```text
api-client-kit==0.1.0
```

A possible placeholder package release may happen earlier as:

```text
api-client-kit==0.0.1
```

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

## Design Goals

`api-client-kit` is designed around a few core principles:

* small core, composable pieces
* sync and async parity
* deterministic and testable behavior
* no real network calls in tests
* safe redaction of secrets and credentials
* minimal runtime dependencies
* explicit public API
* practical documentation from early development

## Installation

The package is not published yet.

Future installation target:

```bash
pip install api-client-kit
```

For `uv` users:

```bash
uv add api-client-kit
```

## Development

This repository is `uv`-first and will remain pip-compatible.

Expected future local development commands:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python -m build
```

Pip-compatible workflow target:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Testing Policy

Tests will use `pytest`.

Tests must not call real external APIs.

HTTP behavior should be tested with local test doubles such as `httpx.MockTransport`.

## Python Support

Primary development Python version:

```text
Python 3.12
```

Supported Python versions for the first usable release:

```text
Python >=3.10
```

Initial CI matrix target:

```text
3.10, 3.11, 3.12, 3.13
```

## License

MIT License.
