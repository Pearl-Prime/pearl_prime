#!/usr/bin/env bash
# Pre-merge safety check — run before merging ANY PR
# Usage: bash scripts/git/pre_merge_check.sh <PR_NUMBER>
#
# MANDATORY for all agent sessions. See CLAUDE.md rule 0.
# Added after PR #245 incident (20,006 files deleted by squash merge).

set -euo pipefail

PR_NUMBER="${1:?Usage: $0 <PR_NUMBER>}"

echo "=== Pre-merge safety check for PR #${PR_NUMBER} ==="

# Get diff stats
STATS=$(gh pr diff "$PR_NUMBER" --stat 2>/dev/null | tail -1)
echo "Diff stats: $STATS"

# Count deletions
DELETED=$(gh pr diff "$PR_NUMBER" 2>/dev/null | grep '^-' | grep -v '^---' | wc -l | tr -d ' ')
FILES_CHANGED=$(gh pr diff "$PR_NUMBER" --stat 2>/dev/null | grep -c '|' || echo 0)
FILES_DELETED=$(gh pr diff "$PR_NUMBER" --name-status 2>/dev/null | grep -c '^D' || echo 0)

echo "Files changed: $FILES_CHANGED"
echo "Files deleted: $FILES_DELETED"
echo "Lines deleted: $DELETED"

# Safety gates
if [ "$FILES_DELETED" -gt 50 ]; then
    echo ""
    echo "⛔ BLOCKED: PR #${PR_NUMBER} deletes ${FILES_DELETED} files (threshold: 50)"
    echo "Top deleted directories:"
    gh pr diff "$PR_NUMBER" --name-status 2>/dev/null | grep '^D' | cut -f2 | cut -d/ -f1 | sort | uniq -c | sort -rn | head -10
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
