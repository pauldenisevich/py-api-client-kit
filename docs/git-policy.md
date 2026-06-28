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
