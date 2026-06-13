#!/bin/bash
# Pearl_GitHub Hourly Health Check
# Run: bash scripts/git/health_check.sh
# Or schedule: crontab -e → 0 * * * * cd /path/to/phoenix_omega && bash scripts/git/health_check.sh >> logs/git_health.log 2>&1

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "═══════════════════════════════════════════"
echo "Pearl_GitHub Health Check — $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════"

ISSUES=0
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
fi

# 1. Branch state
echo ""
echo "--- Branch State ---"
BRANCH=$(git branch --show-current 2>/dev/null || echo "DETACHED")
echo "Current branch: $BRANCH"

if [ "$BRANCH" = "main" ]; then
  echo "WARNING: On main branch. Do not commit here."
  ISSUES=$((ISSUES + 1))
fi

if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] || [ -f .git/CHERRY_PICK_HEAD ] || [ -f .git/MERGE_HEAD ]; then
  echo "WARNING: Git operation in progress (merge/rebase/cherry-pick)."
  ISSUES=$((ISSUES + 1))
fi

# 2. Sync with origin
echo ""
echo "--- Remote Sync ---"
git fetch origin 2>/dev/null || echo "WARNING: Cannot reach origin"

MAIN_LOCAL=$(git rev-parse main 2>/dev/null || echo "none")
MAIN_REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "none")
if [ "$MAIN_LOCAL" != "$MAIN_REMOTE" ]; then
  echo "WARNING: Local main ($MAIN_LOCAL) != origin/main ($MAIN_REMOTE)"
  echo "  Run: git checkout main && git reset --hard origin/main"
  ISSUES=$((ISSUES + 1))
else
  echo "OK: Local main matches origin/main"
fi

# 3. Distance from origin/main
echo ""
echo "--- Distance from origin/main ---"
if [ "$BRANCH" != "DETACHED" ]; then
  COUNTS=$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo "? ?")
  BEHIND=$(echo "$COUNTS" | awk '{print $1}')
  AHEAD=$(echo "$COUNTS" | awk '{print $2}')
  echo "Behind: $BEHIND | Ahead: $AHEAD"

  if [ "$AHEAD" != "?" ] && [ "$AHEAD" -gt 30 ]; then
    echo "CRITICAL: $AHEAD commits ahead — push-guard will block (max 30)"
    echo "  Likely cause: branched from codex/* instead of origin/main"
    echo "  Fix: cherry-pick to clean branch from origin/main"
    ISSUES=$((ISSUES + 1))
  fi

  if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "DETACHED" ] && [[ "$BRANCH" == agent/* ]] && [ "$BEHIND" != "?" ] && [ "$BEHIND" -gt 0 ]; then
    echo "WARNING: Agent branch is behind origin/main by $BEHIND commit(s)."
    echo "  Agent branches should usually start clean from origin/main (0 behind)."
    ISSUES=$((ISSUES + 1))
  fi
fi

# 4. Uncommitted changes
echo ""
echo "--- Uncommitted Changes ---"
DIRTY=$(git status -s 2>/dev/null | wc -l | tr -d ' ')
echo "Changed files: $DIRTY"
if [ "$DIRTY" -gt 50 ]; then
  echo "WARNING: $DIRTY uncommitted files. Consider committing or stashing."
  ISSUES=$((ISSUES + 1))
fi
git status --short | sed -n '1,10p'

# 5. Lock files
echo ""
echo "--- Lock Files ---"
LOCKS_SEEN=0
# .git/index.lock — only warn once it has PERSISTED >60s (transient locks are
# normal here: Xcode/Spotlight run `git status` constantly). NEVER auto-remove.
if [ -f .git/index.lock ]; then
  LOCK_AGE=$(stat -f "%m" .git/index.lock 2>/dev/null || stat -c "%Y" .git/index.lock 2>/dev/null || echo "0")
  NOW=$(date +%s)
  LOCK_SECS=$(( NOW - LOCK_AGE ))
  LOCK_MINS=$(( LOCK_SECS / 60 ))
  if [ "$LOCK_SECS" -gt 60 ]; then
    echo "CRITICAL: .git/index.lock has persisted ${LOCK_SECS}s (~${LOCK_MINS}m)"
    echo "  A long-lived lock usually means a crashed git process. Do NOT remove blindly."
    echo "  If you have confirmed no git process is running: rm -f .git/index.lock"
    ISSUES=$((ISSUES + 1))
  else
    echo "OK: .git/index.lock present but transient (${LOCK_SECS}s old) — likely an in-flight git/Xcode status. Leave it."
  fi
  LOCKS_SEEN=1
fi
# Worktree locks — warn (do NOT remove) if any worktree is administratively locked.
if [ -d .git/worktrees ]; then
  while read -r wl; do
    [ -z "$wl" ] && continue
    WT_NAME=$(basename "$(dirname "$wl")")
    WT_REASON=$(tr -d '\n' < "$wl" 2>/dev/null)
    if [ -n "$WT_REASON" ]; then
      echo "WARNING: worktree '$WT_NAME' is locked (reason: $WT_REASON). Do NOT remove the lock; run 'git worktree unlock' deliberately."
    else
      echo "WARNING: worktree '$WT_NAME' is locked. Do NOT remove the lock; run 'git worktree unlock' deliberately."
    fi
    ISSUES=$((ISSUES + 1))
    LOCKS_SEEN=1
  done < <(find .git/worktrees -mindepth 2 -maxdepth 2 -name locked 2>/dev/null)
fi
if [ "$LOCKS_SEEN" -eq 0 ]; then
  echo "OK: No lock files"
fi

# 6. Push-guard pre-check (if on a non-main branch with commits)
echo ""
echo "--- Push-Guard Pre-Check ---"
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "DETACHED" ]; then
  if [ -n "$PYTHON_BIN" ] && [ -f scripts/git/push_guard.py ]; then
    PYTHONPATH=. "$PYTHON_BIN" scripts/git/push_guard.py --json 2>/dev/null && echo "OK: Push-guard would pass" || {
      echo "WARNING: Push-guard would BLOCK this push"
      ISSUES=$((ISSUES + 1))
    }
  else
    echo "SKIP: push_guard.py or python runtime not available on this branch"
  fi
else
  echo "SKIP: On main or detached"
fi

# 7. Stale agent branches
echo ""
echo "--- Stale Agent Branches ---"
while read -r b; do
  [ -z "$b" ] && continue
  LAST=$(git log -1 --format="%cr" "$b" 2>/dev/null || echo "unknown")
  DAYS=$(git log -1 --format="%ct" "$b" 2>/dev/null || echo "0")
  NOW=$(date +%s)
  AGE_DAYS=$(( (NOW - DAYS) / 86400 ))
  if [ "$AGE_DAYS" -gt 7 ]; then
    echo "  STALE: $b (last commit: $LAST)"
    ISSUES=$((ISSUES + 1))
  else
    echo "  OK: $b ($LAST)"
  fi
done < <(git for-each-ref --format='%(refname:short)' refs/heads/agent)

echo ""
echo "--- Upstream Health ---"
while IFS=$'\t' read -r ref track; do
  if echo "$track" | grep -q 'gone'; then
    echo "WARNING: $ref has gone upstream"
    ISSUES=$((ISSUES + 1))
  fi
done < <(git for-each-ref --format='%(refname:short)%09%(upstream:track)' refs/heads)

# 8. Large files check (new/modified files > 8MB)
echo ""
echo "--- Large Files Check ---"
while read -r f; do
  [ -z "$f" ] && continue
  if [ -f "$f" ]; then
    SIZE=$(wc -c < "$f" 2>/dev/null || echo "0")
    SIZE_MB=$((SIZE / 1048576))
    if [ "$SIZE_MB" -ge 8 ]; then
      echo "CRITICAL: $f is ${SIZE_MB}MB (push-guard limit: 8MB)"
      ISSUES=$((ISSUES + 1))
    fi
  fi
done < <(git diff --name-only 2>/dev/null)
echo "OK: No oversized staged files detected"

# Summary
echo ""
echo "═══════════════════════════════════════════"
if [ "$ISSUES" -gt 0 ]; then
  echo "RESULT: $ISSUES issue(s) found. Fix before pushing."
else
  echo "RESULT: All clear. Safe to proceed."
fi
echo "═══════════════════════════════════════════"

exit $ISSUES
