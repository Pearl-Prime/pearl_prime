#!/usr/bin/env bash
# Preflight before push: block direct push to main, block orphan branches.
# Run manually before git push or install as a pre-push hook.
set -e
branch=$(git rev-parse --abbrev-ref HEAD)
remote="${1:-origin}"
# OPD numbering — surface current max on origin/main so new entries don't collide
git fetch origin main --quiet 2>/dev/null || true
max_opd=$(git show origin/main:artifacts/coordination/operator_decisions_log.tsv 2>/dev/null \
  | awk -F'\t' '/^OPD-[0-9]+\t/ {n=$1; sub(/^OPD-/, "", n); if (n+0 > max) max=n+0} END {print max}')
if [ -n "$max_opd" ] && [ "$max_opd" -gt 0 ]; then
  echo "ℹ️  Current max OPD on origin/main: OPD-${max_opd} — next new OPD should be OPD-$((max_opd + 1))"
fi
if [[ "$branch" == "main" || "$branch" == "master" ]]; then
  if git rev-parse --verify "$remote/main" &>/dev/null || git rev-parse --verify "$remote/master" &>/dev/null; then
    echo "Direct push to main is not allowed. Use a PR." >&2
    exit 1
  fi
fi
base=$(git merge-base HEAD "$remote/main" 2>/dev/null || git merge-base HEAD "$remote/master" 2>/dev/null || true)
if [[ -z "$base" ]]; then
  echo "Branch has no history in common with main. Create branch from origin/main." >&2
  exit 1
fi
# Disk guard — soft-warn only (do not block push; block worktree add separately)
repo_root="$(git rev-parse --show-toplevel)"
disk_guard="${repo_root}/scripts/git/disk_guard.py"
if [[ -f "$disk_guard" ]]; then
  if ! PYTHONPATH="${repo_root}${PYTHONPATH:+:${PYTHONPATH}}" python3 "$disk_guard" --warn-only; then
    echo "⚠️  Disk guard: low free space (push preflight continues; avoid git worktree add until remediated)." >&2
  fi
fi
echo "Preflight OK."
