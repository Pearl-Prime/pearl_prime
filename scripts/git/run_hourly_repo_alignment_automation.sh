#!/bin/bash
# Pearl Repo Align automation entrypoint.
#
# Runs hourly_repo_alignment from the real repo (live by default), then mirrors
# latest report aliases into the artifacts-only stable checkout.
#
# Default automation invocation (live):
#   bash scripts/git/run_hourly_repo_alignment_automation.sh --report-label automation
#
# Status-only verification:
#   bash scripts/git/run_hourly_repo_alignment_automation.sh --dry-run --report-label verification
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MIRROR_ROOT="${PEARL_REPO_ALIGN_MIRROR:-/Users/ahjan/.codex/automation-checkouts/pearl-repo-align-live}"
REPORT_SRC="$REPO_ROOT/artifacts/governance/repo_alignment"
REPORT_DST="$MIRROR_ROOT/artifacts/governance/repo_alignment"

cd "$REPO_ROOT"
bash scripts/git/hourly_repo_alignment.sh "$@"

mkdir -p "$REPORT_DST"
cp -f "$REPORT_SRC/latest_hourly_repo_alignment.json" "$REPORT_DST/"
cp -f "$REPORT_SRC/latest_hourly_repo_alignment.md" "$REPORT_DST/"
if [[ -f "$REPORT_SRC/latest_branch_census.json" ]]; then
  cp -f "$REPORT_SRC/latest_branch_census.json" "$REPORT_DST/"
fi

echo "Mirrored latest alignment artifacts (copy) to $REPORT_DST"
