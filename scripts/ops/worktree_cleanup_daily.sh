#!/bin/bash
# scripts/ops/worktree_cleanup_daily.sh
#
# Daily auto-cleanup of stale local worktrees.
# Called by ~/Library/LaunchAgents/com.ahjan.phoenix_omega.worktree_cleanup.plist
#
# Auto-deletes ONLY worktrees that match strict safety rules:
#   SAFE = (pushed=synced AND uncommit=0)
#        OR (pushed=LOCAL_ONLY AND merged-to-main=yes AND uncommit=0)
#
# NEVER touches:
#   - current worktree
#   - main repo (/Users/ahjan/phoenix_omega)
#   - any uncommit > 0
#   - LOCAL_ONLY with merged=no  (unpushed work)
#   - diverged from origin
#
# Before each deletion, tag-archives the branch:
#   git tag archive/<branch>-<date> <sha>
#   git push origin archive/<branch>-<date>
#
# Logs every run to: artifacts/cleanup_logs/YYYY-MM-DD.log (appended)
#
# Exit codes:
#   0 = success (or nothing to clean)
#   1 = audit script missing or repo not found
#   2 = no worktree list available

export PATH=/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin
set -u

REPO_ROOT="${PHOENIX_OMEGA_REPO:-/Users/ahjan/phoenix_omega}"
AUDIT_SCRIPT="${REPO_ROOT}/scripts/ops/worktree_cleanup_audit.sh"
LOG_DIR="${REPO_ROOT}/artifacts/cleanup_logs"
DATE_STAMP=$(date -u +%Y-%m-%d)
LOG_FILE="${LOG_DIR}/${DATE_STAMP}.log"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

mkdir -p "$LOG_DIR"

# Logging helper
log() { echo "[$(date -u +%H:%M:%S)] $*" | tee -a "$LOG_FILE"; }

log "═══════════════════════════════════════════════════════"
log "Phoenix Omega — Daily Worktree Cleanup"
log "Started:  $TS"
log "Repo:     $REPO_ROOT"
log "═══════════════════════════════════════════════════════"

# Preconditions
if [ ! -d "$REPO_ROOT/.git" ] && [ ! -f "$REPO_ROOT/.git" ]; then
  log "ERROR: $REPO_ROOT is not a git repo"
  exit 1
fi

if [ ! -x "$AUDIT_SCRIPT" ]; then
  log "ERROR: audit script not found or not executable: $AUDIT_SCRIPT"
  exit 1
fi

cd "$REPO_ROOT" || { log "ERROR: cannot cd to $REPO_ROOT"; exit 1; }

# Refresh remotes once at the top so audit + tag-archive use fresh state
log "Fetching origin..."
git fetch --prune --quiet origin 2>&1 | tee -a "$LOG_FILE" || log "WARN: git fetch failed (continuing with cached state)"

# Run the audit (read-only — produces /tmp/wt_cleanup.{verify,keep}.txt)
log "Running audit..."
"$AUDIT_SCRIPT" > /tmp/wt_daily_audit.stdout 2>&1
log "Audit complete."

if [ ! -s /tmp/wt_cleanup.verify.txt ]; then
  log "ERROR: verify file empty or missing"
  exit 2
fi

# Build the loose-rule SAFE list (synced+clean OR LOCAL_ONLY+merged+clean)
# Skip locked worktrees from auto-cleanup — locked = operator-explicit (or live session)
# even though many are technically safe. Daily run stays conservative.
# (For locked cleanup, operator runs scripts/ops/worktree_cleanup_audit.sh manually.)
SAFE_LIST=$(/usr/bin/awk -F'|' '
  NR>1 {
    pushed=$7; uncommit=$6; merged=$8; locked=$9; path=$10; branch=$3; sha=$4;
    if (locked=="locked") next;
    if (uncommit != "0") next;
    if (pushed=="synced") { print path "|" branch "|" sha; next }
    if (pushed=="LOCAL_ONLY" && merged=="yes") { print path "|" branch "|" sha; next }
  }
' /tmp/wt_cleanup.verify.txt)

if [ -z "$SAFE_LIST" ]; then
  log "Nothing to clean today. ✓"
  log "═══ END ═══"
  exit 0
fi

SAFE_COUNT=$(echo "$SAFE_LIST" | wc -l | tr -d ' ')
log "SAFE candidates (auto-cleanable): $SAFE_COUNT"

DELETED=0
ARCHIVED=0
FAILED=0

while IFS='|' read -r path branch sha; do
  [ -z "$path" ] && continue
  short_sha=$(echo "$sha" | cut -c1-7)
  log "→ $branch ($short_sha) :: $path"

  # Race-condition guard: re-verify clean RIGHT NOW (audit may be stale by
  # minutes if a live session in the worktree has been writing artifacts).
  if [ -d "$path" ]; then
    live_uncommit=$(git -C "$path" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [ "$live_uncommit" != "0" ]; then
      log "   SKIP: re-check shows $live_uncommit uncommitted line(s) — left in place"
      FAILED=$((FAILED+1))
      continue
    fi
  fi

  # Tag-archive: only if branch is not detached and we have a real ref
  if [ "$branch" != "(detached)" ] && [ -n "$branch" ]; then
    archive_tag="archive/${branch//\//-}-${DATE_STAMP}"
    # Skip if archive tag already exists (idempotent)
    if git -C "$REPO_ROOT" rev-parse --verify "refs/tags/${archive_tag}" >/dev/null 2>&1; then
      log "   archive tag ${archive_tag} exists — skipping tag creation"
    else
      if git -C "$REPO_ROOT" tag "${archive_tag}" "${sha}" 2>>"$LOG_FILE"; then
        log "   tagged: ${archive_tag}"
        # Push tag to origin (no-op if no network)
        if git -C "$REPO_ROOT" push origin "${archive_tag}" 2>>"$LOG_FILE"; then
          log "   pushed: ${archive_tag} → origin"
          ARCHIVED=$((ARCHIVED+1))
        else
          log "   WARN: tag push failed — local tag still exists"
        fi
      else
        log "   WARN: tag creation failed (sha may be missing locally) — skipping deletion for safety"
        FAILED=$((FAILED+1))
        continue
      fi
    fi
  fi

  # Remove the worktree (no --force; daily rule stays conservative)
  if git -C "$REPO_ROOT" worktree remove "$path" 2>>"$LOG_FILE"; then
    log "   removed worktree ✓"
    DELETED=$((DELETED+1))
  else
    log "   WARN: worktree remove failed (probably dirty — left in place)"
    FAILED=$((FAILED+1))
  fi
done <<< "$SAFE_LIST"

# Prune stale worktree refs
git -C "$REPO_ROOT" worktree prune 2>>"$LOG_FILE"

log "═══ Summary ═══"
log "Worktrees removed:    $DELETED"
log "Branches archived:    $ARCHIVED"
log "Failed (left alone):  $FAILED"
log "Remaining worktrees:  $(git -C "$REPO_ROOT" worktree list | wc -l | tr -d ' ')"
log "Disk free:            $(df -h "$REPO_ROOT" | tail -1 | awk '{print $4}')"
log "═══ END ($(date -u +%H:%M:%S)) ═══"
log ""

exit 0
