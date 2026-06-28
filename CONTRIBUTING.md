# Contributing

Thank you for your interest in contributing to `api-client-kit`.

This project is in early development. The repository is being built as a professional open-source Python package, but the runtime API client functionality is not ready yet.

## Current Status

The project is currently in foundation/bootstrap work.

Early work includes:

* repository structure
* package skeleton
* local development setup
* testing setup
* CI
* documentation
* release process

Runtime client implementation will be added incrementally after the repository foundation is complete.

## Development Principles

Contributions should follow these principles:

* keep changes small and focused
* include tests for behavior changes
* avoid real network calls in tests
* avoid leaking secrets in logs, errors, docs, or examples
* preserve sync and async behavior parity where applicable
* keep public APIs explicit and intentional
* update documentation when public behavior changes

## Local Development

This project is `uv`-first and pip-compatible.

Expected future `uv` workflow:

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

Expected future pip-compatible workflow:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

These commands may evolve while the project is still in Sprint 1 foundation work.

## Tests

Tests use `pytest`.

Tests must not call real external APIs.

HTTP behavior should be tested with local test doubles such as `httpx.MockTransport`.

Feature work should include tests unless the change is documentation-only or infrastructure-only.

## Secrets

Never commit secrets.

Do not commit:

* `.env`
* API keys
* tokens
* private keys
* SSH config
* PyPI credentials
* GitHub credentials
* machine-specific local paths

Use `.env.example` only for safe placeholder documentation.

## Pull Requests

Public pull request guidelines will be expanded before the project is made public.

For now, a good pull request should:

* describe the reason for the change
* keep scope narrow
* include tests when behavior changes
* update docs when public behavior changes
* pass linting, formatting, tests, and CI

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Pre-commit

This project uses `pre-commit` for local file hygiene, Ruff linting, and Ruff formatting.

Install the Git hook after setting up the development environment:

```bash
uv run pre-commit install
```

Run all pre-commit hooks manually:

```bash
uv run pre-commit run --all-files
```

The configured hooks check:

* trailing whitespace
* final newline at end of files
* YAML syntax
* TOML syntax
* large accidental files
* merge conflict markers
* line endings
* Ruff linting
* Ruff formatting

If a hook modifies files, review the changes, stage them again, and rerun the checks before committing.

Pre-commit does not replace the full local check sequence. Before pushing meaningful changes, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```
