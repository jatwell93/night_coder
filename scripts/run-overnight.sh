#!/usr/bin/env bash
set -euo pipefail

# Canonical wrapper for systemd user service (`night-coder-run.service`).
# Copy/sync this file to ~/night_coder/scripts/run-overnight.sh on the VPS.

export PATH="${HOME}/.opencode/bin:${HOME}/.local/bin:${HOME}/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

REPO_ROOT="${HOME}/night_coder"
export SCENARIO_CATALOG_PATH="${REPO_ROOT}/docs/superpowers/pilot/scenarios"
LOG_STAMP=$(date -u +"%Y%m%dT%H%M%SZ")

echo "[run-overnight] === Starting overnight run ${LOG_STAMP} ==="

if ! command -v ntm &>/dev/null; then
  echo "[run-overnight] ABORT: ntm not found on PATH. Guardrail layer missing." >&2
  exit 1
fi

if [[ ! -d "${SCENARIO_CATALOG_PATH}" ]]; then
  echo "[run-overnight] ABORT: SCENARIO_CATALOG_PATH does not exist: ${SCENARIO_CATALOG_PATH}" >&2
  exit 1
fi

echo "[run-overnight] Launching guarded run workflow"
doppler run -- python "${REPO_ROOT}/src/cli/run_overnight.py" --json

echo "[run-overnight] === Run complete ==="

