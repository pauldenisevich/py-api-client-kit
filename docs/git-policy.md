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
