# Documentation

This directory contains the public documentation for `api-client-kit`.

`api-client-kit` is currently under active early development. Some documents describe current repository behavior, while others describe the intended v0.1.0 package direction.

## Start Here

For a high-level explanation of the project, start with:

* [Project Positioning](project-positioning.md)

For architecture and development workflow, see:

* [Architecture](architecture.md)
* [Local Development](local-development.md)

For repository workflow and release process, see:

* [Git Policy](git-policy.md)
* [Release Process](release.md)

## Project Status

Current status:

```text
package skeleton exists
local development tooling exists
CI exists
runtime API client implementation not started yet
not published to PyPI yet
```

The package is not ready for production use.

The first intended usable public release is:

```text
api-client-kit==0.1.0
```

## Current Documentation

The following public docs currently exist:

* [Project Positioning](project-positioning.md) — explains what the package is, who it is for, and how it differs from raw `httpx`, SDK generators, and retry-only helpers.
* [Architecture](architecture.md) — describes the intended package architecture, request pipeline, layers, and design boundaries.
* [Local Development](local-development.md) — explains devcontainer setup, `uv`, pip-compatible workflow, checks, pre-commit, and package builds.
* [Testing](testing.md) — documents pytest, unit/integration test categories, no-network policy, coverage, async tests, and CI testing behavior.
* [Git Policy](git-policy.md) — documents branch model, commit message policy, local checks, push policy, versioning, and tags.
* [Release Process](release.md) — documents version bumps, changelog updates, local checks, CI verification, tags, PyPI verification, and GitHub releases.

## Planned Foundation Docs

The following public docs are planned as part of the documentation foundation:

* `security-and-redaction.md` — redaction principles and secret-safety policy.

## Planned Feature Docs

The following docs are expected as runtime features are implemented:

* `auth.md` — auth provider interface, API key auth, bearer token auth, and composite auth.
* `errors.md` — structured errors, HTTP status mapping, network errors, decode errors, and safe context.
* `retries.md` — retry policy, retryable status codes, retryable exceptions, idempotency, and backoff.
* `ratelimits.md` — rate-limit interfaces, `Retry-After`, and default no-op behavior.
* `pagination.md` — cursor pagination, page-number pagination, Link header pagination, and sync/async iteration.

These docs should be created when the corresponding package features are implemented or when a design note is useful before implementation.

## Development Documentation

Local development supports both workflows:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python -m build
```

and:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check .
```

The `uv` workflow is the primary maintainer workflow.

The pip-compatible workflow is required so the package remains usable for contributors who do not use `uv`.

See [Local Development](local-development.md) for details.

## Testing Documentation

Testing documentation should explain:

* unit tests
* integration tests with local transports/test doubles
* `httpx.MockTransport`
* no real network calls
* no real API keys or secrets
* coverage expectations
* async test behavior
* CI test behavior

The v0.1.0 coverage target is at least 95%.

## Documentation Rules

Public docs should be practical, accurate, and repository-oriented.

Do not document features as available until they are implemented and tested.

Do not include private maintainer notes, private execution context, credentials, local machine paths, or unpublished private planning details in public docs.

## Documentation Roadmap

Documentation will expand alongside implemented package functionality.

As features are added, the docs should be updated to cover:

* core sync and async clients
* request and response handling
* structured errors
* redaction
* authentication
* retries and backoff
* rate-limit handling
* pagination
* observability hooks
* examples
* release process

Public documentation should describe implemented behavior clearly and avoid presenting planned features as already available.
