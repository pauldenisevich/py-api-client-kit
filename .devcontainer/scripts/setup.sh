#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------
# Py-API-Client-Kit devcontainer setup
# Runs once after the devcontainer is created/rebuilt.
# ------------------------------------------------

export PATH="/usr/local/bin:${HOME}/.local/bin:${PATH}"

WORKSPACE_DIR="${CONTAINER_WORKSPACE_FOLDER:-/workspaces/$(basename "$(pwd)")}"

echo "Py-API-Client-Kit devcontainer setup"
echo "Workspace: ${WORKSPACE_DIR}"
echo ""

cd "${WORKSPACE_DIR}"

# ------------------------------------------------
# Toolchain checks
# ------------------------------------------------

PYTHON_BIN="$(command -v python3 || command -v python || true)"
if [ -z "${PYTHON_BIN}" ]; then
  echo "❌ Python was not found in PATH."
  exit 1
fi

PY_VER="$("${PYTHON_BIN}" --version 2>/dev/null || echo 'N/A')"
echo "Python: ${PY_VER}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found; installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
  export PATH="/usr/local/bin:${HOME}/.local/bin:${PATH}"
fi

UV_VER="$(uv --version 2>/dev/null || echo 'N/A')"
echo "uv: ${UV_VER}"

GIT_VER="$(git --version 2>/dev/null || echo 'N/A')"
echo "Git: ${GIT_VER}"

# ------------------------------------------------
# Project dependency setup
# ------------------------------------------------
# During early Sprint 1, pyproject.toml may not exist yet.
# Once packaging is added, this will install/sync dev dependencies.
# ------------------------------------------------

if [ -f "pyproject.toml" ]; then
  echo ""
  echo "Installing project dependencies with uv..."

  if grep -q '^\[project.optional-dependencies\]' pyproject.toml \
    && grep -q '^dev[[:space:]]*=' pyproject.toml; then
    uv sync --extra dev
  else
    uv sync
  fi
else
  echo ""
  echo "pyproject.toml not found; skipping dependency sync."
  echo "   This is expected before the package skeleton/tooling tasks are complete."
fi

echo ""
echo "Devcontainer setup complete."
