# Testing

This document defines the testing policy for `api-client-kit`.

The project uses `pytest` and is designed to be tested without real external API calls, real credentials, or real network dependencies.

## Status

`api-client-kit` is currently under active early development.

The current test suite covers imports, request and response models, URL joining,
header merging, timeout resolution, sync/async client foundations, header
redaction, fragment-safe URL/query/userinfo redaction, recursive payload
redaction, bounded body snippets, the current package error taxonomy, internal
safe diagnostic-context construction, and internal HTTP status-to-exception
mapping. As runtime functionality is added, every feature should include focused
tests.

## Test Goals

Tests should prove that the package is:

* importable
* deterministic
* safe around credentials and sensitive data
* compatible with supported Python versions
* consistent across sync and async behavior
* reliable without real network access
* easy to maintain as public APIs evolve

## Test Framework

The project uses:

```text
pytest
```

Run the test suite:

```bash
uv run pytest
```

Run a specific test file:

```bash
uv run pytest tests/unit/test_import_unit.py
```

Run with verbose output:

```bash
uv run pytest -vv
```

## Test Categories

The repository uses these test directories:

```text
tests/
  unit/
  integration/
```

## Unit Tests

Unit tests belong in:

```text
tests/unit/
```

Unit tests should cover isolated behavior such as:

* URL joining
* header merging
* request option defaults
* request context normalization
* response wrapper accessors
* timeout resolution
* header redaction
* URL/query/userinfo redaction and fragment-safe diagnostic URL handling
* recursive payload redaction through Mapping/list/tuple nesting
* mapping normalization, payload immutability, and opaque-leaf behavior
* fake-secret absence from sanitized payload representations
* empty and short body snippets, whitespace preservation, exact maximum bounds,
  and deterministic truncation
* UTF-8 text handling and non-UTF-8 binary byte-count markers
* structured JSON redaction, malformed-JSON text fallback, and the structured
  parsing resource ceiling
* caller-supplied known-secret scrubbing, including a truncation-boundary
  regression case
* `ApiClientError` inheritance and message validation
* optional context handling and defensive shallow context copying
* message-only `str()` and class-plus-message `repr()` behavior
* context non-rendering with fake secrets and native exception chaining
* `NetworkError` and `TimeoutError` hierarchy and construction behavior
* distinction between package `TimeoutError` and `builtins.TimeoutError`
* inherited safe string/representation behavior and context non-rendering for
  network errors
* native cause chaining for network and timeout errors
* HTTP status error hierarchy and required package `ResponseData`
* response identity, its explicit `error.response.raw` access path, and
  exclusion from `Exception.args`
* specialized HTTP status subclass construction and fake response/context secret
  non-rendering
* native chaining for HTTP status errors and errors-subpackage imports while
  top-level exports remain unchanged
* request-only and response-side safe contexts, missing responses, empty
  bodies, URL/header composition, echoed-credential scrubbing, JSON and `+json`
  media types, malformed/non-JSON/binary/large bodies, source immutability, and
  private export boundaries
* explicit status mappings, generic 4xx mapping, 500–599 server mapping, and
  499/500/599/600 boundaries
* non-error and redirect `None` behavior, exact deterministic status-only
  messages, safe context composition, response identity and raw-response path,
  attempt propagation, and private mapping export boundaries

Future feature areas such as auth, retries, rate limits, decode errors, HTTPX
transport mapping, sync/async client HTTP-error integration, `raise_for_status`,
pagination, and observability should receive dedicated tests when implemented.

Unit tests should be fast, deterministic, and independent of external services.

## Integration Tests

Integration tests belong in:

```text
tests/integration/
```

Integration tests should test package behavior across multiple internal components, but they must still avoid real external APIs.

For HTTP behavior, integration tests should use local transports and test doubles such as:

```text
httpx.MockTransport
```

Examples of integration-style behavior:

* sync client request flow
* async client request flow
* request construction through the client
* response wrapping
* client lifecycle behavior

## Client Transport Testing

`SyncClient` and `AsyncClient` accept injected `httpx` transports. Client
transport tests should inject `httpx.MockTransport` to verify request behavior
without real network calls.

Use these tests to assert request construction and response wrapping. Useful
assertions include:

* HTTP method
* joined URL and path
* query parameters
* headers
* JSON or data body
* timeout behavior where applicable
* `ResponseData` wrapping
* lifecycle behavior where applicable

Sync example:

```python
import httpx

from api_client_kit import SyncClient


def handler(request: httpx.Request) -> httpx.Response:
    assert request.method == "GET"
    assert request.url.path == "/users"
    return httpx.Response(200, json={"items": []})


def test_sync_client_with_mock_transport() -> None:
    with SyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        response = client.get("/users")

    assert response.json() == {"items": []}
```

Async tests should use `pytest.mark.asyncio`:

```python
import httpx
import pytest

from api_client_kit import AsyncClient


@pytest.mark.asyncio
async def test_async_client_with_mock_transport() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/status"
        return httpx.Response(200, json={"ok": True})

    async with AsyncClient(
        base_url="https://api.example.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        response = await client.get("/status")

    assert response.json() == {"ok": True}
```

These examples are documentation examples, not doctests.

Real external API calls, real credentials, and network-dependent tests are not
allowed. Future feature areas such as auth, retries, rate limits, structured
errors, body redaction, pagination, and observability should receive dedicated
tests when they are implemented.

## No Real Network Calls

Tests must not call real external APIs.

Do not write tests that require:

* live SaaS APIs
* public internet endpoints
* real API keys
* bearer tokens
* OAuth credentials
* GitHub tokens
* PyPI tokens
* customer data
* local services not created by the test itself

HTTP behavior should be simulated with `httpx.MockTransport` or other local test doubles.

## No Secrets in Tests

Tests must not contain real secrets.

Do not commit:

* API keys
* bearer tokens
* refresh tokens
* passwords
* cookies
* private keys
* real customer data
* real service credentials

Use obvious fake values:

```python
"test-api-key"
"test-token"
"secret-value"
```

Any test involving secrets should use fake values and assert their absence from
redacted helper output. Errors, logs, and hook payloads remain future runtime
integration areas.

## Pytest Markers

The project defines these markers:

```text
unit: Fast isolated unit tests with no external services
integration: Integration tests using local transports or test doubles
```

Example:

```python
from __future__ import annotations

import pytest

pytestmark = [pytest.mark.unit]


def test_example() -> None:
    assert True
```

Run unit tests:

```bash
uv run pytest -m unit
```

Run integration tests:

```bash
uv run pytest -m integration
```

## Async Tests

Async tests use `pytest-asyncio`.

The project uses strict asyncio mode.

Async tests should be explicit:

```python
from __future__ import annotations

import pytest

pytestmark = [pytest.mark.unit]


@pytest.mark.asyncio
async def test_async_example() -> None:
    assert True
```

Avoid implicit event loop behavior.

Avoid global async state.

Prefer function-scoped test isolation unless a stronger reason exists.

## Coverage

Run coverage:

```bash
uv run pytest --cov=api_client_kit --cov-report=term-missing
```

Coverage configuration lives in:

```text
pyproject.toml
```

The v0.1.0 coverage target is at least:

```text
95%
```

Coverage should be meaningful. Do not add low-value tests only to satisfy a number.

Important behavior should be tested directly.

## CI Testing

GitHub Actions runs CI on:

* push to `main`
* pull requests to `main`

CI currently checks supported Python versions:

```text
3.10
3.11
3.12
3.13
```

CI runs:

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=api_client_kit --cov-report=term-missing
uv run python -m build
```

A change is not complete if CI fails.

## Local Test Commands

Standard test run:

```bash
uv run pytest
```

Coverage run:

```bash
uv run pytest --cov=api_client_kit --cov-report=term-missing
```

Full local check sequence:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Build-related check sequence:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pytest --cov=api_client_kit --cov-report=term-missing
uv run python -m build
uv run twine check dist/*
```

## pip-Compatible Test Workflow

The package must remain pip-compatible.

Use this workflow to verify tests outside `uv`:

```bash
deactivate 2>/dev/null || true
rm -rf .venv

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

python -c "import api_client_kit; print(api_client_kit.__version__)"
python -m pytest
python -m ruff check .

deactivate
```

Use:

```bash
python -m pytest
```

instead of bare:

```bash
pytest
```

to ensure tests run with the active virtual environment.

## Test Naming

Use clear test names that describe behavior.

Good examples:

```python
def test_package_imports() -> None:
    ...

def test_redacts_authorization_header() -> None:
    ...

def test_retries_get_after_transient_server_error() -> None:
    ...
```

Avoid vague names:

```python
def test_works() -> None:
    ...

def test_stuff() -> None:
    ...
```

## Test File Naming

Use explicit test file names:

```text
test_import_unit.py
test_redaction_unit.py
test_retry_policy_unit.py
test_sync_client_integration.py
```

Prefer names that make the test category and subject clear.

## Test Style

Python test files should start with:

```python
from __future__ import annotations
```

Use type annotations for test functions:

```python
def test_example() -> None:
    ...
```

Use plain `assert` statements.

Do not import `pytest` unless the test file uses markers, fixtures, `pytest.raises`, parametrization, or other pytest features.

## Determinism

Tests should be deterministic.

Avoid:

* real sleeps
* current wall-clock time unless injected
* random values unless seeded
* network calls
* order-dependent global state
* hidden environment dependencies

Retry and backoff tests should use fake clocks or fake sleepers.

## Future Test Helpers

As the package grows, shared test helpers may be added for:

* fake clocks
* fake sleepers
* `httpx.MockTransport` factories
* reusable request/response builders
* redaction assertions
* hook recorders

Keep test helpers small and explicit.

## Before Committing

Before committing test or runtime changes, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

For coverage-sensitive changes, also run:

```bash
uv run pytest --cov=api_client_kit --cov-report=term-missing
```
