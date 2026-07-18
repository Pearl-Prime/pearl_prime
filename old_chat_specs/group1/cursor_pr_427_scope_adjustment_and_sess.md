# PR #427 scope adjustment and SESSION_UNITY_PROTOCOL update
_Exported on 4/16/2026 at 19:26:05 GMT+8 from Cursor (3.1.15)_

---

**User**

PHOENIX OMEGA — TWO LANES: (A) Fix PR #427 scope (B) Land SESSION_UNITY_PROTOCOL router blurb

READ: docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_GOVERNANCE.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; CLAUDE.md preflight block.

══════════════════════════════════════════════════════════════════════
LANE A — Pearl_GitHub: PR #427 (ws_r2_html_tree_upload_20260415) — strip accidentals, then merge
══════════════════════════════════════════════════════════════════════
Goal: agent/r2-html-tree-upload should contain ONLY:
  scripts/storage/* (R2 HTML uploader + r2_upload_common + __init__),
  tests/test_upload_html_tree_to_r2.py,
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv row for ws_r2_html_tree_upload_20260415,
  and NOTHING ELSE unless owner explicitly wants run_pipeline.py book_quality_gate on this PR (default: remove it — belongs on content-bank or pipeline PR).

Steps:
1) Free disk (several GB) if git index/checkout still fails.
2) git fetch origin
3) git checkout agent/r2-html-tree-upload && git pull (or reset --hard origin/agent/r2-html-tree-upload to match GitHub head 9106dd1d2f if that is remote tip)
4) Remove from this branch (choose one):
   - git revert <bad_commit> if one commit introduced the bundle, OR
   - git restore --source=origin/main -- config/content_banks/ docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md scripts/run_pipeline.py
     (only if those files should match main and not be part of R2 PR)
5) git diff origin/main --stat — confirm no 9 YAMLs, no fragment spec, no stray run_pipeline unless intended
6) PYTHONPATH=. python3 scripts/git/push_guard.py; scripts/ci/preflight_push.sh; bash scripts/git/health_check.sh
7) Commit "fix(pr427): narrow scope to R2 HTML uploader + workstream row"; push
8) gh pr view 427 — confirm Files changed; gh pr diff 427 --stat | tail -1 (mass delete check)
9) Merge #427 when satisfied. Workers pearl-prime red: non-blocking per GITHUB_GOVERNANCE unless ruleset says otherwise — admin merge only per runbook.
10) Pearl_PM: After merge, ACTIVE_WORKSTREAMS — ws_r2_html_tree_upload_20260415 → completed; evidence_paths = merge SHA + PR URL.

CLOSEOUT A: merge SHA; confirm PR diff is R2-only.

══════════════════════════════════════════════════════════════════════
LANE B — Pearl_GitHub: SESSION_UNITY_PROTOCOL “Universal router” — one-file PR from clean main
══════════════════════════════════════════════════════════════════════
Goal: Single commit on origin/main: docs/SESSION_UNITY_PROTOCOL.md only — section after Quick Reference, “when to use”, link to ./agent_brief.txt (no full prompt duplicated).

Avoid dirty mega-tree:
  Option 1: New worktree (wait for checkout to finish or use sparse checkout if you use it):
    git worktree add /tmp/phoenix-session-docs origin/main
    cd /tmp/phoenix-session-docs
    Copy in ONLY the edited SESSION_UNITY_PROTOCOL.md from the messy workspace (cp path), OR re-apply the small patch by hand.
  Option 2: Stash -u on dirty branch, checkout main, cherry-pick or paste edit, commit, pop stash later.

Then:
  git checkout -b agent/session-unity-router-blurb origin/main
  # stage ONLY docs/SESSION_UNITY_PROTOCOL.md
  git add docs/SESSION_UNITY_PROTOCOL.md
  git commit -m "docs(session): link universal router prompt to agent_brief"
  push_guard; preflight_push; health_check; push; gh pr create — body short.

CLOSEOUT B: PR link + SHA.

══════════════════════════════════════════════════════════════════════
OUT OF SCOPE
══════════════════════════════════════════════════════════════════════
- Re-adding content banks or fragment spec on PR #427 unless opening a separate PR.
- Fixing Cloudflare Workers in this task unless owner asks.

Pearl_PM CLOSEOUT (when both done): two PRs or two SHAs noted; no duplicate workstream rows.

PHOENIX OMEGA — TWO LANES: (A) Fix PR #427 scope (B) Land SESSION_UNITY_PROTOCOL router blurb

READ: docs/SESSION_UNITY_PROTOCOL.md; docs/GITHUB_GOVERNANCE.md; docs/GITHUB_OPERATIONS_FRAMEWORK.md; CLAUDE.md preflight block.

══════════════════════════════════════════════════════════════════════
LANE A — Pearl_GitHub: PR #427 (ws_r2_html_tree_upload_20260415) — strip accidentals, then merge
══════════════════════════════════════════════════════════════════════
Goal: agent/r2-html-tree-upload should contain ONLY:
  scripts/storage/* (R2 HTML uploader + r2_upload_common + __init__),
  tests/test_upload_html_tree_to_r2.py,
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv row for ws_r2_html_tree_upload_20260415,
  and NOTHING ELSE unless owner explicitly wants run_pipeline.py book_quality_gate on this PR (default: remove it — belongs on content-bank or pipeline PR).

Steps:
1) Free disk (several GB) if git index/checkout still fails.
2) git fetch origin
3) git checkout agent/r2-html-tree-upload && git pull (or reset --hard origin/agent/r2-html-tree-upload to match GitHub head 9106dd1d2f if that is remote tip)
4) Remove from this branch (choose one):
   - git revert <bad_commit> if one commit introduced the bundle, OR
   - git restore --source=origin/main -- config/content_banks/ docs/CONTENT_FRAGMENT_VARIATION_WRITER_SPEC.md scripts/run_pipeline.py
     (only if those files should match main and not be part of R2 PR)
5) git diff origin/main --stat — confirm no 9 YAMLs, no fragment spec, no stray run_pipeline unless intended
6) PYTHONPATH=. python3 scripts/git/push_guard.py; scripts/ci/preflight_push.sh; bash scripts/git/health_check.sh
7) Commit "fix(pr427): narrow scope to R2 HTML uploader + workstream row"; push
8) gh pr view 427 — confirm Files changed; gh pr diff 427 --stat | tail -1 (mass delete check)
9) Merge #427 when satisfied. Workers pearl-prime red: non-blocking per GITHUB_GOVERNANCE unless ruleset says otherwise — admin merge only per runbook.
10) Pearl_PM: After merge, ACTIVE_WORKSTREAMS — ws_r2_html_tree_upload_20260415 → completed; evidence_paths = merge SHA + PR URL.

CLOSEOUT A: merge SHA; confirm PR diff is R2-only.

══════════════════════════════════════════════════════════════════════
LANE B — Pearl_GitHub: SESSION_UNITY_PROTOCOL “Universal router” — one-file PR from clean main
══════════════════════════════════════════════════════════════════════
Goal: Single commit on origin/main: docs/SESSION_UNITY_PROTOCOL.md only — section after Quick Reference, “when to use”, link to ./agent_brief.txt (no full prompt duplicated).

Avoid dirty mega-tree:
  Option 1: New worktree (wait for checkout to finish or use sparse checkout if you use it):
    git worktree add /tmp/phoenix-session-docs origin/main
    cd /tmp/phoenix-session-docs
    Copy in ONLY the edited SESSION_UNITY_PROTOCOL.md from the messy workspace (cp path), OR re-apply the small patch by hand.
  Option 2: Stash -u on dirty branch, checkout main, cherry-pick or paste edit, commit, pop stash later.

Then:
  git checkout -b agent/session-unity-router-blurb origin/main
  # stage ONLY docs/SESSION_UNITY_PROTOCOL.md
  git add docs/SESSION_UNITY_PROTOCOL.md
  git commit -m "docs(session): link universal router prompt to agent_brief"
  push_guard; preflight_push; health_check; push; gh pr create — body short.

CLOSEOUT B: PR link + SHA.

══════════════════════════════════════════════════════════════════════
OUT OF SCOPE
══════════════════════════════════════════════════════════════════════
- Re-adding content banks or fragment spec on PR #427 unless opening a separate PR.
- Fixing Cloudflare Workers in this task unless owner asks.

Pearl_PM CLOSEOUT (when both done): two PRs or two SHAs noted; no duplicate workstream rows.

---

**Cursor**

Executing both lanes: reading required docs, inspecting PR #427 and `SESSION_UNITY_PROTOCOL.md`, then applying fixes and creating the docs PR.



Continuing: checking fetch status, verifying `agent_brief.txt`, and executing both lanes.



Confirming remote tip `9106dd1d2f`. `docs/agent_brief.txt` exists (router stub). Stashing local changes, checking out the R2 branch, and restoring non-R2 files from `origin/main`.



Using a separate worktree for Lane A to avoid a long-running stash on the large repo.



Worktree failed (LFS smudge / disk). Working in the main clone: checking disk space and checking out the R2 branch.



Disk is full (~334 Mi free), which caused LFS/worktree failures. Freeing space and continuing.



Trying sparse checkout to limit working-tree files and avoid LFS smudge on assets. Checking whether we can switch branches safely:



Building the fix with a temporary index and `git restore --staged` only (no full checkout, no worktree writes) to avoid LFS and disk limits.



Investigating unexpected doc deletions vs `origin/main` and fixing the commit so the branch matches main except for the intended R2 files.



Restoring the two docs from `origin/main` and rebuilding a single fix commit.



Running preflight checks and pushing the branch.



