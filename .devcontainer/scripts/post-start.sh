#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------
# Py-API-Client-Kit devcontainer post-start
# Runs each time the devcontainer starts.
# ------------------------------------------------

export PATH="/usr/local/bin:${HOME}/.local/bin:${PATH}"

WORKSPACE_DIR="${CONTAINER_WORKSPACE_FOLDER:-/workspaces/$(basename "$(pwd)")}"

cd "${WORKSPACE_DIR}"

# ------------------------------------------------
# Version/readiness checks
# ------------------------------------------------

PY_VER="$(python3 --version 2>/dev/null || python --version 2>/dev/null || echo 'N/A')"
UV_VER="$(uv --version 2>/dev/null || echo 'N/A')"
GIT_VER="$(git --version 2>/dev/null || echo 'N/A')"

# ------------------------------------------------
# SSH agent status
# ------------------------------------------------

SSH_AGENT_STATUS="not configured"
if [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "${SSH_AUTH_SOCK}" ]; then
  SSH_AGENT_STATUS="available at ${SSH_AUTH_SOCK}"
fi

# ------------------------------------------------
# Git workspace status
# ------------------------------------------------

GIT_STATUS_SUMMARY="not a git repository"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if [ -z "$(git status --short 2>/dev/null)" ]; then
    GIT_STATUS_SUMMARY="clean"
  else
    GIT_STATUS_SUMMARY="has local changes"
  fi
fi

# ------------------------------------------------
# Readiness banner
# ------------------------------------------------

echo ""
echo "──────────────────────────────────────────────"
echo "Py-API-Client-Kit devcontainer ready"
echo "- Workspace: ${WORKSPACE_DIR}"
echo "- Python: ${PY_VER}"
echo "- uv: ${UV_VER}"
echo "- Git: ${GIT_VER}"
echo "- SSH agent: ${SSH_AGENT_STATUS}"
echo "- Git status: ${GIT_STATUS_SUMMARY}"
echo "──────────────────────────────────────────────"
echo ""

# ------------------------------------------------
# Helpful next-step hints
# ------------------------------------------------

if [ ! -f "pyproject.toml" ]; then
  echo "pyproject.toml not found yet."
  echo "   This is expected before the project skeleton/tooling tasks are complete."
  echo ""
fi

if [ "${SSH_AGENT_STATUS}" = "not configured" ]; then
  echo "SSH agent is not available inside the devcontainer."
  echo "   GitHub SSH may not work until host SSH agent forwarding is configured."
  echo ""
fi
