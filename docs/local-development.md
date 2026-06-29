# Local Development

This document explains how to set up and work on `api-client-kit` locally.

`api-client-kit` is currently under active early development. The package skeleton, tooling, CI, and documentation foundation are in place, while runtime API client functionality is still being built.

## Prerequisites

Recommended local tooling:

* Git
* Docker Desktop
* Visual Studio Code
* VS Code Dev Containers extension
* GitHub SSH access
* Python 3.12 for primary local development

The package supports Python `>=3.10`, but the primary local development environment uses Python 3.12.

CI verifies the package against:

```text
3.10
3.11
3.12
3.13
```

## Development Environment

The recommended development environment is the VS Code devcontainer.

The devcontainer provides:

* Python 3.12
* `uv`
* Git
* build tools
* shell utilities
* Ruff support
* Pytest support
* package build tooling

Open the repository in VS Code and run:

```text
Dev Containers: Reopen in Container
```

After the container starts, verify:

```bash
python --version
uv --version
git --version
git status
```

Expected:

```text
Python 3.12.x
uv available
git available
repository status visible
```

## uv Workflow

The primary development workflow uses `uv`.

Install dependencies:

```bash
uv sync --extra dev
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Check formatting:

```bash
uv run ruff format --check .
```

Apply formatting:

```bash
uv run ruff format .
```

Run coverage:

```bash
uv run pytest --cov=api_client_kit --cov-report=term-missing
```

Build the package:

```bash
uv run python -m build
```

Validate built artifacts:

```bash
uv run twine check dist/*
```

## pip-Compatible Workflow

The project is `uv`-first, but it must remain pip-compatible.

Use this workflow to verify pip compatibility:

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
```

Use `python -m pytest` and `python -m ruff` instead of bare `pytest` or `ruff` to ensure the commands run inside the active virtual environment.

When finished:

```bash
deactivate
```

To return to the normal `uv` workflow:

```bash
rm -rf .venv
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## Makefile Shortcuts

The repository includes Makefile shortcuts for common commands.

Install dependencies:

```bash
make install
```

Run linting:

```bash
make lint
```

Apply formatting:

```bash
make format
```

Check formatting:

```bash
make format-check
```

Run tests:

```bash
make test
```

Run coverage:

```bash
make coverage
```

Run the standard local check sequence:

```bash
make check
```

Build the package:

```bash
make build
```

Clean generated local artifacts:

```bash
make clean
```

## Tests

Tests use `pytest`.

Run the test suite:

```bash
uv run pytest
```

Current test categories:

```text
tests/unit/
tests/integration/
```

Unit tests should cover isolated logic.

Integration tests should use local transports and test doubles. They must not call real external APIs.

HTTP behavior should be tested with `httpx.MockTransport`.

Tests must not require real credentials, tokens, API keys, or network access.

## Coverage

Run coverage with:

```bash
uv run pytest --cov=api_client_kit --cov-report=term-missing
```

The v0.1.0 coverage target is at least 95%.

Coverage configuration lives in:

```text
pyproject.toml
```

## Linting and Formatting

Ruff is used for linting and formatting.

Run linting:

```bash
uv run ruff check .
```

Run formatting check:

```bash
uv run ruff format --check .
```

Apply formatting:

```bash
uv run ruff format .
```

Ruff configuration lives in:

```text
pyproject.toml
```

## Pre-commit

The project uses `pre-commit` for local file hygiene and formatting/linting hooks.

Install the Git hook once:

```bash
uv run pre-commit install
```

Run all hooks manually:

```bash
uv run pre-commit run --all-files
```

If a hook modifies files, review the changes, stage them again, and rerun checks before committing.

Pre-commit does not replace the normal local check sequence.

Before meaningful commits, still run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Build

Build package artifacts with:

```bash
uv run python -m build
```

Expected output:

```text
dist/
  api_client_kit-<version>.tar.gz
  api_client_kit-<version>-py3-none-any.whl
```

Validate artifacts with:

```bash
uv run twine check dist/*
```

Do not commit `dist/` or build artifacts unless a release process explicitly requires it.

## GitHub SSH

GitHub SSH should work inside the devcontainer through the local SSH agent.

Verify:

```bash
ssh -T git@github.com
git status
```

A successful GitHub SSH response usually looks like:

```text
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

Do not commit SSH keys, SSH config, tokens, or credentials.

## Signed Commits

Commits should be signed.

After committing, verify the signature locally:

```bash
git log --show-signature -1
```

After pushing, verify GitHub shows the commit as:

```text
Verified
```

## Local Files and Secrets

Never commit secrets or local-only files.

Do not commit:

* `.env`
* API keys
* bearer tokens
* refresh tokens
* passwords
* cookies
* private SSH keys
* GitHub tokens
* PyPI tokens
* local machine paths
* generated caches
* virtual environments
* build artifacts

Use `.env.example` only for safe placeholder documentation.

## Standard Local Check Sequence

Before every meaningful commit, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

For build or release-related work, also run:

```bash
uv run python -m build
uv run twine check dist/*
```

For coverage-sensitive work, run:

```bash
uv run pytest --cov=api_client_kit --cov-report=term-missing
```

## Before Committing

Before committing:

```bash
git status
git diff
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Stage only intentional files:

```bash
git add <files>
git diff --cached
```

Commit:

```bash
git commit -m "<type>: <message>"
```

Push:

```bash
git push origin main
```

After pushing, verify:

* the commit appears on GitHub
* the commit is `Verified`
* GitHub Actions pass

## Troubleshooting

### `pytest` runs from the wrong environment

Use:

```bash
python -m pytest
```

instead of:

```bash
pytest
```

This ensures pytest runs through the active Python interpreter.

### Package import fails after dependency changes

Recreate the environment:

```bash
rm -rf .venv
uv sync --extra dev
uv run python -c "import api_client_kit; print(api_client_kit.__version__)"
uv run pytest
```

### Ruff reports formatting issues

Apply formatting:

```bash
uv run ruff format .
```

Then rerun:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

### Build artifacts are stale

Clean and rebuild:

```bash
make clean
uv run python -m build
uv run twine check dist/*
```
