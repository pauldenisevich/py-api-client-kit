# Git Policy

This document defines the Git workflow for `api-client-kit`.

The goal is to keep development fast, clean, reviewable, and safe while the project moves from private foundation work toward a public open-source release.

## Branch Model

The default branch is `main`.

The project uses trunk-based development.

In the current solo-maintainer phase, direct commits to `main` are allowed when the change is small, scoped, reviewed locally, and verified before push.

This policy is intentional. The project is being built through small commits with local checks and signed commits rather than large long-lived branches.

## Direct Commits to `main`

Direct commits to `main` are allowed while the project is solo-maintained.

Before committing directly to `main`, confirm:

* the change has a narrow scope
* the changed files are understood
* private files are not staged
* generated junk files are not staged
* local checks pass
* the commit message uses the correct project prefix
* the commit is signed
* the push is intentional

Direct commits should not be used for unclear or risky work.

## Short-Lived Branches

Short-lived branches are optional.

Use a short-lived branch when the work is risky, experimental, or difficult to review as one direct commit.

Good reasons to use a short-lived branch:

* large refactor
* CI workflow experiment
* release workflow change
* packaging behavior change
* public API design change
* multi-commit feature spike
* work that may need to be abandoned or rewritten

Short-lived branches should be merged or deleted quickly.

Avoid long-running branches.

## Long-Lived Branches

Long-lived development branches are discouraged.

The project should avoid maintaining separate permanent branches such as:

```text
develop
dev
staging
next
```

The normal development target is `main`.

Release tags identify released versions. Long-running release branches are not needed at this stage.

## Pull Requests

Pull requests are optional while the project is solo-maintained.

After the repository becomes public, external contributions should normally use pull requests.

Maintainer changes may still be committed directly to `main` when the change is small, scoped, and verified.

## Required Local Discipline

Every meaningful change should follow this local discipline:

```text
edit
review diff
run checks
commit
push
verify remote status
```

Before committing, inspect:

```bash
git status
git diff
git diff --cached
```

Before pushing, run the project checks that are available for the current stage.

The normal local check sequence is:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

For build or release work, also run:

```bash
uv run python -m build
```

## Signed Commits

Commits should be signed.

The maintainer workflow uses SSH commit signing from inside the devcontainer.

After committing, verify the local signature:

```bash
git log --show-signature -1
```

After pushing, verify GitHub shows the commit as:

```text
Verified
```

## Commit Message Policy

Commit messages should be short, clear, and action-oriented.

Use this format:

```text
<type>: <summary>
```

The summary should describe what changed, not how difficult the work was.

Good examples:

```text
chore: add devcontainer foundation
docs: add project positioning
build: configure package metadata
test: configure coverage
ci: add lint test and build workflow
```

Avoid vague messages such as:

```text
update stuff
fix things
changes
work
misc
```

## Commit Prefixes

Use these commit prefixes:

| Prefix      | Use for                                                               |
| ----------- | --------------------------------------------------------------------- |
| `chore:`    | repository maintenance, non-runtime setup, small project housekeeping |
| `feat:`     | user-facing package functionality                                     |
| `fix:`      | bug fixes                                                             |
| `docs:`     | documentation-only changes                                            |
| `test:`     | tests or test configuration                                           |
| `ci:`       | GitHub Actions, CI/CD, release workflows                              |
| `refactor:` | behavior-preserving code restructuring                                |
| `build:`    | packaging, dependencies, build system, tooling configuration          |
| `release:`  | release commits, version bumps, changelog finalization                |

## Prefix Rules

Use `docs:` when the change only affects documentation.

Use `test:` when the change only affects tests or test configuration.

Use `build:` for package metadata, dependencies, build tools, Ruff, Pytest, coverage, pre-commit, Makefile, and packaging configuration.

Use `ci:` only for CI/CD workflow files and automation.

Use `chore:` for project setup and maintenance that does not fit `build:`, `docs:`, `test:`, or `ci:`.

Use `feat:` only when adding public package behavior.

Use `fix:` only when correcting broken behavior.

Use `refactor:` only when restructuring code without changing behavior.

Use `release:` only for formal release preparation commits.

## Scope

Optional scopes may be added later if useful:

```text
feat(client): add sync client request method
test(retries): add retry policy tests
docs(auth): document bearer token auth
```

For now, scopes are optional. Prefer simple messages unless a scope improves clarity.

## Commit Body

Most small commits do not need a body.

Use a commit body when the change needs extra context, such as:

* why a tradeoff was chosen
* why a non-obvious implementation is safe
* what follow-up work remains
* why a temporary limitation exists

## Signed Commit Requirement

Commits should be signed.

After committing, verify locally:

```bash
git log --show-signature -1
```

After pushing, verify GitHub shows the commit as:

```text
Verified
```

## Local Pre-Commit Checklist

Before every meaningful commit, run the standard local checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

These checks verify:

* Ruff linting passes
* Ruff formatting is already applied
* the test suite passes

If any check fails, do not commit yet. Fix the issue, rerun the checks, and review the diff again.

## Optional Full Pre-Commit Run

The repository also uses `pre-commit`.

Run all configured hooks manually with:

```bash
uv run pre-commit run --all-files
```

The pre-commit hooks check file hygiene, TOML/YAML syntax, merge conflict markers, Ruff linting, and Ruff formatting.

This does not replace the standard local check sequence. Before committing meaningful work, still run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Installed Git Hook

After setting up the repository, install the pre-commit Git hook once:

```bash
uv run pre-commit install
```

After installation, the hook runs automatically on `git commit`.

If the hook modifies files, review the changes, stage them again, and rerun the checks before committing.

## Push Policy

Use small, intentional commits and push only after local checks pass.

The normal direct-to-`main` flow is:

```bash
git status
git add <files>
git status
git diff --cached
git commit -m "<type>: <message>"
git log --show-signature -1
git push origin main
```

Do not blindly run:

```bash
git add .
```

unless you have already inspected `git status` and confirmed every untracked or modified file is safe to stage.

Before pushing, confirm:

* the commit is scoped
* the commit message uses an approved prefix
* the commit is signed
* local checks pass
* private files are not staged
* generated files are not staged unless intentionally required
* `docs/private/` is not tracked

After pushing, verify:

* the commit appears on GitHub
* GitHub shows the commit as `Verified`
* GitHub Actions pass once CI exists

## Safe Staging

Prefer staging explicit files:

```bash
git add README.md pyproject.toml tests/unit/test_import_unit.py
```

Use patch staging when only part of a file should be committed:

```bash
git add -p
```

Use all-file staging only after review:

```bash
git status
git diff
git add .
git diff --cached
```

## Push Target

The normal push target is:

```bash
git push origin main
```

For the first push from a new clone, use:

```bash
git push -u origin main
```

## Push Failure Policy

If a push fails, do not force-push by default.

First inspect the error.

If the remote branch has new commits, fetch and rebase or fast-forward carefully:

```bash
git fetch origin
git status
git pull --ff-only origin main
```

Only use force push when there is an explicit, reviewed reason, such as cleaning a private pre-publication repository before launch.

Never force-push release tags without an explicit release-policy decision.

## Versioning Policy

This project uses Semantic Versioning.

Version format:

```text
MAJOR.MINOR.PATCH
```

During early development, the project uses `0.x` versions.

## Planned Version Path

The planned early version path is:

```text
0.0.1  placeholder package/name-reservation release
0.1.0  first usable public release
0.1.x  patch fixes for 0.1.0
0.2.0  next backward-compatible feature release
```

## `0.0.1` Placeholder Release

Version `0.0.1` is reserved for an optional placeholder release.

Purpose:

* reserve the `api-client-kit` name on PyPI
* link the PyPI package to the GitHub repository
* clearly mark the package as work in progress
* avoid implying production readiness

Version `0.0.1` should not be presented as a usable production package.

## `0.1.0` First Public Release

Version `0.1.0` is the first intended usable public release.

It should include the first stable package foundation for:

* sync and async client foundations
* request and response primitives
* structured errors
* redaction helpers
* auth providers
* retry and backoff support
* rate-limit interfaces
* pagination helpers
* observability hooks
* examples
* public documentation
* CI and release workflow

## Patch Releases

Patch releases are for fixes that do not add major new public features.

Examples:

```text
0.1.1
0.1.2
0.1.3
```

Use patch releases for:

* bug fixes
* documentation corrections
* packaging fixes
* CI/release workflow fixes
* small compatibility fixes
* safe internal refactors

Patch releases should not introduce large new public APIs.

## Minor Releases

Minor releases are for backward-compatible feature additions.

Examples:

```text
0.2.0
0.3.0
```

Use minor releases for:

* new auth providers
* new retry/rate-limit helpers
* new pagination helpers
* new observability hooks
* new examples
* backward-compatible public API additions

## Breaking Changes

While the project is in `0.x`, public APIs may still evolve.

Even during `0.x`, breaking changes should be intentional, documented, and called out in the changelog.

After a stable `1.0.0` release, breaking changes should require a major version bump.

## Version Source

The package version is defined in:

```text
pyproject.toml
```

The runtime package exposes the same version through:

```python
api_client_kit.__version__
```

When preparing a release, update both if the project still stores the version in both places.

A future task may centralize the version source to avoid duplication.

## Tag Policy

Release tags use this format:

```text
vMAJOR.MINOR.PATCH
```

Examples:

```text
v0.0.1
v0.1.0
v0.1.1
v0.2.0
```

Tags should correspond exactly to the package version.

For example:

| Package version | Git tag  |
| --------------- | -------- |
| `0.0.1`         | `v0.0.1` |
| `0.1.0`         | `v0.1.0` |
| `0.1.1`         | `v0.1.1` |
| `0.2.0`         | `v0.2.0` |

## When to Tag

Create a tag only for an intentional release.

Do not tag normal development commits.

Do not tag documentation-only commits unless they are part of a release.

Do not tag CI/tooling commits unless they are part of a release.

## Tag Creation

Before creating a tag:

* confirm the version is correct in `pyproject.toml`
* confirm the runtime package version matches, if applicable
* confirm `CHANGELOG.md` is updated
* run local checks
* verify CI passes
* confirm the release commit is pushed

Create the tag from the release commit:

```bash
git tag v0.1.0
```

Push the tag:

```bash
git push origin v0.1.0
```

Or push all intended tags:

```bash
git push origin main --tags
```

Use targeted tag pushes when possible to avoid pushing accidental local tags.

## Signed Tags

Signed tags are preferred when the signing workflow is available.

SSH-signed or GPG-signed tags may be used depending on the maintainer environment.

If signed tags are configured, create a signed tag:

```bash
git tag -s v0.1.0
```

If signed tags are not configured yet, normal lightweight tags are acceptable for early pre-release work, but release documentation should clearly state which tag type was used.

## Tag Safety

Never reuse a released tag.

Never move a public release tag unless there is an explicit emergency correction and the impact is understood.

If a tag was created locally by mistake and not pushed, delete it locally:

```bash
git tag -d v0.1.0
```

If a tag was pushed by mistake, stop and review before deleting or replacing it.

## Planned Early Tags

Planned early tags:

```text
v0.0.1  optional placeholder release
v0.1.0  first usable public release
v0.1.1  first patch release if needed
v0.2.0  next backward-compatible feature release
```

## Release Process

The full release checklist lives in:

```text
docs/release.md
```

Use that document for version bumps, changelog updates, local checks, CI verification, tags, PyPI verification, and GitHub releases.

## Private Files

Private files must never be committed.

Do not stage or commit:

* `.env`
* API keys
* tokens
* private keys
* SSH config
* PyPI credentials
* GitHub credentials
* local machine paths
* private notes
* private Codex logs
* files under `docs/private/`

Before committing, confirm private files are not tracked:

```bash
git ls-files docs/private
```

Expected output: nothing.

## Current Policy Summary

Current branch policy:

```text
default branch: main
development model: trunk-based
direct commits to main: allowed while solo-maintained
short-lived branches: optional for risky work
long-lived branches: discouraged
signed commits: expected
local checks before push: expected
CI verification after push: required once CI exists
```
