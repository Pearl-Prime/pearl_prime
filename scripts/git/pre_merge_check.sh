#!/usr/bin/env bash
# Pre-merge safety check — run before merging ANY PR
# Usage: bash scripts/git/pre_merge_check.sh <PR_NUMBER>
#
# MANDATORY for all agent sessions. See CLAUDE.md rule 0.
# Added after PR #245 incident (20,006 files deleted by squash merge).
#
# 2026-05-06: rewrote to use `gh pr view --json files` instead of
# `gh pr diff --stat` / `--name-status` (those flags were removed in
# recent gh CLI versions). Behavior unchanged.
#
# 2026-07-23: added a live CI-status gate (PR #191 incident — a session
# merged a PR while reporting "all governance checks pass" when in fact
# most checks, including Core tests and Release gates, had not finished
# running, and one (parse-sweep) had already failed. Neither this script
# nor pr_governance_review.py had ever looked at check-run status — this
# was the missing mechanism. This script blocks on any check still
# pending; it warns (does not hard-block) on completed failures, since
# some workflows on this repo run chronically red for reasons unrelated
# to a given PR's diff — but it always prints the real per-check status,
# so a caller can no longer claim "all checks pass" without that claim
# being visibly contradicted right above it.

set -euo pipefail

PR_NUMBER="${1:?Usage: $0 <PR_NUMBER>}"

echo "=== Pre-merge safety check for PR #${PR_NUMBER} ==="

# Pull all per-file metadata in one API call. The `files` field returns
# per-file additions, deletions, and changeType (ADDED/MODIFIED/REMOVED/
# RENAMED/COPIED). additions/deletions are total numeric counts.
JSON=$(gh pr view "$PR_NUMBER" --json additions,deletions,files 2>/dev/null)

ADDITIONS=$(echo "$JSON" | jq -r '.additions')
DELETED_LINES=$(echo "$JSON" | jq -r '.deletions')
FILES_CHANGED=$(echo "$JSON" | jq -r '.files | length')
FILES_DELETED=$(echo "$JSON" | jq -r '[.files[] | select(.changeType == "REMOVED")] | length')

echo "Diff stats: ${FILES_CHANGED} file(s), +${ADDITIONS}/-${DELETED_LINES}"
echo "Files changed: $FILES_CHANGED"
echo "Files deleted: $FILES_DELETED"
echo "Lines deleted: $DELETED_LINES"

# Safety gates
if [ "$FILES_DELETED" -gt 50 ]; then
    echo ""
    echo "⛔ BLOCKED: PR #${PR_NUMBER} deletes ${FILES_DELETED} files (threshold: 50)"
    echo "Top deleted directories:"
    echo "$JSON" | jq -r '.files[] | select(.changeType == "REMOVED") | .path' \
        | cut -d/ -f1 | sort | uniq -c | sort -rn | head -10
    echo ""
    echo "DO NOT MERGE without explicit owner approval."
    exit 1
fi

if [ "$FILES_CHANGED" -gt 500 ]; then
    echo ""
    echo "⚠️  WARNING: PR #${PR_NUMBER} changes ${FILES_CHANGED} files. Review carefully before merging."
fi

echo ""
echo "=== Live CI status for PR #${PR_NUMBER} ==="

# statusCheckRollup mixes two shapes: Actions check-runs (status/conclusion)
# and legacy commit statuses (state only, no status/conclusion) — normalize
# both into one {name, bucket} shape before deciding pending vs. failing.
CHECKS_JSON=$(gh pr view "$PR_NUMBER" --json statusCheckRollup 2>/dev/null)
NORMALIZED=$(echo "$CHECKS_JSON" | jq -c '[.statusCheckRollup[]? | {
    name: (.name // .context // "unknown"),
    bucket: (
      if (.status // "") != "" then
        (if .status == "COMPLETED" then
          (if (.conclusion == "FAILURE" or .conclusion == "TIMED_OUT" or .conclusion == "CANCELLED") then "failure" else "done" end)
         else "pending" end)
      else
        (if .state == "PENDING" or .state == "EXPECTED" then "pending"
         elif .state == "FAILURE" or .state == "ERROR" then "failure"
         else "done" end)
      end
    )
  }]' 2>/dev/null || echo '[]')

PENDING_NAMES=$(echo "$NORMALIZED" | jq -r '.[] | select(.bucket == "pending") | .name')
FAILING_NAMES=$(echo "$NORMALIZED" | jq -r '.[] | select(.bucket == "failure") | .name')

echo "$NORMALIZED" | jq -r '.[] | "  " + .name + ": " + .bucket'

if [ -n "$PENDING_NAMES" ]; then
    echo ""
    echo "⛔ BLOCKED: check(s) still running on PR #${PR_NUMBER}:"
    echo "$PENDING_NAMES" | sed 's/^/  - /'
    echo ""
    echo "Wait for these to complete before merging. Do not merge on pending checks."
    exit 1
fi

if [ -n "$FAILING_NAMES" ]; then
    echo ""
    echo "⚠️  WARNING: check(s) failing on PR #${PR_NUMBER}:"
    echo "$FAILING_NAMES" | sed 's/^/  - /'
    echo ""
    echo "Before merging: confirm each failure above either (a) reproduces on"
    echo "main independent of this PR's diff, or (b) is fixed by this PR."
    echo "Do NOT report \"all checks pass\" or \"governance checks pass\" while"
    echo "any check above is failing — name the failing check(s) explicitly"
    echo "in the merge decision instead."
fi

echo ""
echo "✅ Pre-merge check passed for PR #${PR_NUMBER}"
