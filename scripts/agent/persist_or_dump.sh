#!/usr/bin/env bash
# persist_or_dump.sh — Agent file persistence guard
#
# Usage: bash scripts/agent/persist_or_dump.sh <file1> [file2] ...
#
# 1. Verifies each file exists and is non-empty
# 2. Attempts git add + git commit
# 3. If commit fails, dumps full file contents to stdout for recovery
#
# Exit codes:
#   0 = all files committed successfully
#   1 = git failed — file contents dumped to stdout (recoverable)
#   2 = one or more files missing or empty (not recoverable)

set -euo pipefail

if [ $# -eq 0 ]; then
  echo "ERROR: No files specified."
  echo "Usage: bash scripts/agent/persist_or_dump.sh <file1> [file2] ..."
  exit 2
fi

MISSING=0
EMPTY=0
FILES=()

echo "══════════════════════════════════════"
echo "  PERSISTENCE GUARD — checking files"
echo "══════════════════════════════════════"

for f in "$@"; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
    MISSING=$((MISSING + 1))
  elif [ ! -s "$f" ]; then
    echo "EMPTY:   $f"
    EMPTY=$((EMPTY + 1))
  else
    size=$(wc -c < "$f")
    lines=$(wc -l < "$f")
    echo "OK:      $f (${size} bytes, ${lines} lines)"
    FILES+=("$f")
  fi
done

if [ $MISSING -gt 0 ] || [ $EMPTY -gt 0 ]; then
  echo ""
  echo "ERROR: ${MISSING} missing, ${EMPTY} empty files. Cannot persist."
  exit 2
fi

echo ""
echo "All ${#FILES[@]} files verified on disk."
echo ""

# --- Attempt git commit ---
echo "══════════════════════════════════════"
echo "  PERSISTENCE GUARD — attempting commit"
echo "══════════════════════════════════════"

# Clear stale lock
rm -f .git/index.lock 2>/dev/null || true

# Try to determine branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "Current branch: $BRANCH"

# Stage files
if git add "${FILES[@]}" 2>/dev/null; then
  echo "Staged ${#FILES[@]} files."
else
  echo "WARNING: git add failed. Falling through to file dump."
  # Fall through to dump
  git add "${FILES[@]}" 2>&1 || true
fi

# Attempt commit
COMMIT_MSG="wip: sandbox persistence commit — ${#FILES[@]} files"
if git commit -m "$COMMIT_MSG" 2>/dev/null; then
  SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  echo ""
  echo "══════════════════════════════════════"
  echo "  COMMITTED: $SHA on $BRANCH"
  echo "══════════════════════════════════════"
  echo ""
  echo "Files committed:"
  for f in "${FILES[@]}"; do
    echo "  ✓ $f"
  done
  echo ""
  echo "Pearl_GitHub can push this commit from a credentialed machine."
  exit 0
fi

# --- Git failed — dump file contents ---
echo ""
echo "WARNING: git commit failed. Dumping file contents for recovery."
echo ""
echo "══════════════════════════════════════════════════════════════════"
echo "  FILE DUMP — copy these to recover work"
echo "══════════════════════════════════════════════════════════════════"
echo ""

for f in "${FILES[@]}"; do
  echo "### FILE: $f"
  echo '```'
  cat "$f"
  echo '```'
  echo ""
done

echo "══════════════════════════════════════════════════════════════════"
echo "  END FILE DUMP"
echo "  ${#FILES[@]} files dumped. Paste into CLOSEOUT_RECEIPT or"
echo "  write directly to paths above on a machine with disk access."
echo "══════════════════════════════════════════════════════════════════"

exit 1
