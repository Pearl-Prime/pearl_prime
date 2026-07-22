# Master Dispatch — Finish Outstanding Lanes (2026-07-22)

Paste this into a Pearl_PM (or general orchestrator) session to fan out the 4 lanes below.
Each lane file carries its own full execution contract (EXECUTE header, live-truth
reconciliation, MERGED-or-BLOCKED landing, CLOSEOUT_RECEIPT). Run **Lane 1 first and
alone** — it unblocks CI for everything else. Lanes 2–4 can run in parallel once Lane 1
lands (or in parallel with Lane 1 if the operator wants speed over sequencing, since none
of 2–4 touch `phoenix_v4/social` or `book_engine_policy`).

## Why these 4 lanes (live-verified 2026-07-22, not carried over from stale claims)

Re-checked every open PR and branch touched this session against current `origin/main`
and live CI (`gh pr list`, `gh pr checks`, `gh run view --log-failed`) before writing
this pack:

- **#49, #50, #42, #53, #55** are ALL still red on Core tests / Drift detectors /
  Release gates — same repo-wide `phoenix_v4.social` + `book_engine_policy` breakage
  reported earlier today, still unfixed on `origin/main`.
- **#53 and #55 collide**: both add `phoenix_v4/social/__init__.py` and
  `media_selector.py`. #55 (`agent/main-unbreak-missing-imports-20260722`) is narrowly
  scoped — just the two missing modules (`book_engine_policy.py` +
  `phoenix_v4/social/`). #53 (`agent/land-deterministic-social-metricool-payload-20260722`)
  bundles the same two module fixes together with ~26 unrelated files (social-schema
  spec, storyblocks licensing, manga doctrine config, flagship snapshots,
  `DATA_DICTIONARY.tsv`) — a governance-scope violation per this repo's own PR-size
  rules, not just messy. This needs untangling, not a blind merge of either.
- **#56 (new since this session's last check) has a REAL, different Core tests
  failure** — not the repo-wide one. `tests/brand_wizard/test_pages_assignment_lookup.py
  ::test_pages_assignment_lookup_prefers_canonical_brand_index` fails because
  `brand-wizard-app/functions/api/onboarding/assignment.js` lets R2 live-assignment
  data win over the canonical `brand_admin_brands.json` index. This is the exact bug
  described in an earlier `pearl_prime_followups_20260722/` handoff that claimed a fix
  but never actually pushed it (blocked on a `403 Resource not accessible by
  integration` from the GitHub app integration) — so the claimed fix never landed and
  the bug is still live in CI today. Confirmed via `gh run view --log-failed` on the
  #56 Core tests job (2026-07-22T02:17 run).
- **`agent/outfit-object-continuity`** has a real, tested, committed change
  (`61f9a8fb85`, 19 files, +1672/-8, 80 tests passing) sitting in a worktree that was
  never pushed and has no PR — confirmed `git ls-remote origin
  agent/outfit-object-continuity` returns nothing.
- **The social-media-audit prompt pack** (`docs/agent_prompt_packs/
  20260722_social_media_audit_100pct_plan/`) is written to disk but was never committed
  — the `.git/index.lock` that blocked it earlier is now gone, confirmed by
  `ls -la .git/index.lock` returning "No such file or directory".

## Lanes

1. [01_pearl_github_unbreak_main_ci_lane.md](01_pearl_github_unbreak_main_ci_lane.md) —
   resolve the #53/#55 collision, land the real fix on `main`, rebase #49/#50/#42 onto
   green CI. **Run this first — everything else is blocked behind it.**
2. [02_pearl_github_fix_brand_assignment_bug_lane.md](02_pearl_github_fix_brand_assignment_bug_lane.md) —
   fix the real R2-vs-canonical bug in `assignment.js` that's blocking #56 and was
   never actually landed despite an earlier claim.
3. [03_pearl_github_land_outfit_continuity_lane.md](03_pearl_github_land_outfit_continuity_lane.md) —
   push the already-committed, already-tested outfit/object continuity work and open
   its PR.
4. [04_pearl_github_commit_social_audit_pack_lane.md](04_pearl_github_commit_social_audit_pack_lane.md) —
   commit the social-media-audit prompt pack (docs-only, index lock now clear) and,
   once Lane 1 lands, resolve the #53/#55-adjacent social-schema payload it names.

Paste each lane file into its own agent session, or paste this whole file into a lead
agent capable of dispatching sub-sessions.
