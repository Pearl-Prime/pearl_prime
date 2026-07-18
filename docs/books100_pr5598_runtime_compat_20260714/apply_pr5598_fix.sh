#!/usr/bin/env bash
set -euo pipefail

BASE_REPO="${1:-/Users/ahjan/phoenix_omega}"
WORKTREE="${2:-/Users/ahjan/phoenix_omega_worktrees/books100-pr5598-runtime-compat-20260714}"
REMOTE="${REMOTE:-origin}"
REMOTE_BRANCH="agent/books100-integration-parser-20260714"
LOCAL_BRANCH="local/pr5598-runtime-compat-20260714"
EXPECTED_HEAD="8eee1fdc80b01614edbacd3220c77183eeb35ca0"
MASS_RENUMBER_COMMIT="8eee1fdc80b01614edbacd3220c77183eeb35ca0"
BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_FILE="$BUNDLE_DIR/patches/pr5598_runtime_compat.patch"

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

command -v git >/dev/null || fail "git is required"
command -v python3 >/dev/null || fail "python3 is required"
[ -d "$BASE_REPO/.git" ] || fail "Base repo not found at $BASE_REPO"
[ ! -e "$WORKTREE" ] || fail "Worktree path already exists: $WORKTREE"

git -C "$BASE_REPO" fetch "$REMOTE" "$REMOTE_BRANCH" main
REMOTE_HEAD="$(git -C "$BASE_REPO" rev-parse "$REMOTE/$REMOTE_BRANCH")"
[ "$REMOTE_HEAD" = "$EXPECTED_HEAD" ] || fail \
  "Remote branch moved. Expected $EXPECTED_HEAD, found $REMOTE_HEAD. Re-audit before applying."

mkdir -p "$(dirname "$WORKTREE")"
git -C "$BASE_REPO" worktree add --detach "$WORKTREE" "$REMOTE/$REMOTE_BRANCH"
cd "$WORKTREE"
git switch -c "$LOCAL_BRANCH"

# Drop the out-of-scope catalog-wide renumbering without rewriting history.
git revert --no-edit "$MASS_RENUMBER_COMMIT"

git apply --check "$PATCH_FILE"
git apply "$PATCH_FILE"

python3 -m py_compile \
  phoenix_v4/planning/canonical_atom_blocks.py \
  phoenix_v4/planning/pool_index.py \
  phoenix_v4/rendering/prose_resolver.py \
  phoenix_v4/planning/assembly_compiler.py \
  tests/planning/test_integration_canonical_parser.py

AVAILABLE_KIB="$(df -Pk "$WORKTREE" | awk 'NR==2 {print $4}')"
MIN_KIB=$((20 * 1024 * 1024))
[ "$AVAILABLE_KIB" -ge "$MIN_KIB" ] || fail \
  "Less than 20 GiB free at $WORKTREE; production-readiness gates were not run."

PYTHONPATH=. python3 -m pytest -q \
  tests/planning/test_integration_canonical_parser.py \
  tests/test_bestseller_editor_wiring.py::test_editor_report_fails_when_dimension_gates_block_delivery

PYTHONPATH=. python3 scripts/ci/check_canonical_atom_parse_sweep.py
PYTHONPATH=. python3 scripts/run_production_readiness_gates.py

git add \
  phoenix_v4/planning/pool_index.py \
  phoenix_v4/rendering/prose_resolver.py \
  tests/planning/test_integration_canonical_parser.py

git commit -m "fix(planning): keep legacy runtime duplicate-compatible"

printf '\nPrepared commits:\n'
git --no-pager log --oneline "$REMOTE/$REMOTE_BRANCH"..HEAD
printf '\nChanged files versus main:\n'
git diff --name-status "$REMOTE/main"...HEAD

if [ "${PUSH:-0}" = "1" ]; then
  git push "$REMOTE" "HEAD:$REMOTE_BRANCH"
  printf '\nPushed to %s/%s\n' "$REMOTE" "$REMOTE_BRANCH"
else
  printf '\nNot pushed. To update PR #5598 after reviewing:\n'
  printf '  git -C %q push %q HEAD:%q\n' "$WORKTREE" "$REMOTE" "$REMOTE_BRANCH"
fi
