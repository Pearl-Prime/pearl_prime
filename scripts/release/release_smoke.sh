#!/usr/bin/env bash
# Release smoke: a lightweight real-path check before rollback verification.
# Evidence: writes artifacts/release/release_smoke_evidence.json
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

EVIDENCE_DIR="${REPO_ROOT}/artifacts/release"
mkdir -p "$EVIDENCE_DIR"
EVIDENCE="${EVIDENCE_DIR}/release_smoke_evidence.json"

write_failure() {
  local step="$1"
  local error="${2:-}"
  if [ -n "$error" ]; then
    echo "{\"step\":\"${step}\",\"passed\":false,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"error\":\"${error}\"}" > "$EVIDENCE"
  else
    echo "{\"step\":\"${step}\",\"passed\":false,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$EVIDENCE"
  fi
}

if [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
  PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "{\"step\":\"python\",\"passed\":false,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"error\":\"python_not_found\"}" > "$EVIDENCE"
  echo "No Python interpreter found."
  exit 1
fi

echo "Running production readiness gates..."
if ! PYTHONPATH=. "$PYTHON_BIN" scripts/run_production_readiness_gates.py; then
  write_failure "production_readiness_gates"
  exit 1
fi

echo "Running rigorous system test (skip sim)..."
if ! PYTHONPATH=. "$PYTHON_BIN" scripts/ci/run_rigorous_system_test.py --skip-sim --strict; then
  write_failure "rigorous_system_test"
  exit 1
fi

echo "Running small release canary..."
if ! PYTHONPATH=. "$PYTHON_BIN" scripts/ci/run_canary_100_books.py --n 3; then
  write_failure "release_canary"
  exit 1
fi

echo "{\"step\":\"release_smoke\",\"passed\":true,\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$EVIDENCE"
echo "Release smoke complete. Evidence: $EVIDENCE"
