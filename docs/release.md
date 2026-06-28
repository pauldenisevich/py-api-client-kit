# Release Process

This document defines the release process for `api-client-kit`.

A release is only complete when the version, changelog, checks, CI, tag, PyPI package, and GitHub release are all verified.

## Release Types

Planned early releases:

```text
0.0.1  placeholder package/name-reservation release
0.1.0  first usable public release
0.1.x  patch fixes for 0.1.0
0.2.0  next backward-compatible feature release
```

## Pre-Release Requirements

Before preparing a release, confirm:

* the release scope is complete
* the working tree is clean
* no private files are tracked
* no secrets are present
* the README is accurate for the release
* documentation is updated
* examples work, if examples exist
* `CHANGELOG.md` is ready to update
* local checks pass
* CI passes

Check the working tree:

```bash
git status
git ls-files docs/private
```

Expected:

```text
git status
→ clean or only intentional release files changed

git ls-files docs/private
→ no output
```

## Version Bump

Update the package version in:

```text
pyproject.toml
```

If the runtime package exposes the version directly, update it there too:

```text
api_client_kit/__init__.py
```

The two versions must match.

Example for `0.1.0`:

```text
pyproject.toml              → version = "0.1.0"
api_client_kit/__init__.py  → __version__ = "0.1.0"
```

A future task may centralize the version source to avoid duplication.

## Changelog Update

Update:

```text
CHANGELOG.md
```

Move relevant items from:

```text
Unreleased
```

to the release version section.

Example:

```text
## 0.1.0 - YYYY-MM-DD
```

The changelog should clearly describe what changed in the release.

For placeholder releases such as `0.0.1`, the changelog must clearly state that the release is for package-name reservation and is not production-ready.

## Local Checks

Run the full local check sequence:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run pytest --cov=api_client_kit --cov-report=term-missing
uv run python -m build
```

Validate package artifacts:

```bash
uv run twine check dist/*
```

If any check fails, stop and fix the issue before continuing.

## Release Commit

After updating the version and changelog, create a release commit:

```bash
git status
git add pyproject.toml api_client_kit/__init__.py CHANGELOG.md
git diff --cached
git commit -m "release: v0.1.0"
git log --show-signature -1
```

Push the release commit:

```bash
git push origin main
```

Verify GitHub shows the commit as:

```text
Verified
```

## CI Verification

After pushing the release commit, verify GitHub Actions passes.

Do not tag the release until CI passes.

If CI fails:

* inspect the failure
* fix it in a scoped follow-up commit
* rerun local checks
* push the fix
* verify CI again

## Tag

Create the release tag from the verified release commit.

Example:

```bash
git tag v0.1.0
```

Push the tag:

```bash
git push origin v0.1.0
```

Use the version-specific tag, not a vague tag name.

Correct:

```text
v0.1.0
```

Incorrect:

```text
latest
release
stable
```

Use targeted tag pushes when possible to avoid pushing accidental local tags.

## Build Artifacts

Build artifacts are generated with:

```bash
uv run python -m build
```

Expected output:

```text
dist/
  api_client_kit-<version>.tar.gz
  api_client_kit-<version>-py3-none-any.whl
```

Validate artifacts before upload:

```bash
uv run twine check dist/*
```

## PyPI Publishing

Publishing should happen only after:

* local checks pass
* build artifacts are valid
* release commit is pushed
* CI passes
* the release tag is created and pushed
* the package version is correct

Long-term publishing should use PyPI Trusted Publishing through GitHub Actions.

Manual publishing may be used only when explicitly approved.

## PyPI Verification

After the package is published, verify that the expected package version exists on PyPI.

For example:

```text
api-client-kit==0.1.0
```

Then verify installation in a clean environment:

```bash
python -m venv /tmp/api-client-kit-release-check
source /tmp/api-client-kit-release-check/bin/activate
python -m pip install --upgrade pip
python -m pip install api-client-kit==0.1.0
python -c "import api_client_kit; print(api_client_kit.__version__)"
deactivate
rm -rf /tmp/api-client-kit-release-check
```

Expected output:

```text
0.1.0
```

## GitHub Release

Create a GitHub release for the tag.

The GitHub release should include:

* release version
* release date
* summary of changes
* installation command
* important limitations
* link to `CHANGELOG.md`
* PyPI package link once available

For pre-release or placeholder versions, mark the GitHub release appropriately.

`v0.0.1` should be marked as a pre-release if used only for package-name reservation.

## `0.0.1` Placeholder Release

Version `0.0.1` is optional.

Purpose:

* reserve the `api-client-kit` package name on PyPI
* link the package to the GitHub repository
* clearly mark the package as work in progress
* avoid implying production readiness

The `0.0.1` release should be treated as a placeholder/pre-release.

It should not be described as production-ready.

## `0.1.0` Public Release

Version `0.1.0` is the first intended usable public release.

Before releasing `0.1.0`, confirm:

* README is polished
* docs are complete enough for first users
* examples work
* tests pass
* CI passes
* coverage target is enforced
* package metadata is correct
* package builds correctly
* PyPI publishing works
* GitHub release notes are ready

## Release Completion Criteria

A release is complete only when:

* version is updated
* changelog is updated
* local checks pass
* build artifacts are valid
* release commit is signed
* release commit is pushed
* CI passes
* tag is created and pushed
* PyPI package is available
* clean install from PyPI works
* GitHub release exists
