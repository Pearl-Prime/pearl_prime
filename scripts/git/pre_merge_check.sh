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
echo "✅ Pre-merge check passed for PR #${PR_NUMBER}"
