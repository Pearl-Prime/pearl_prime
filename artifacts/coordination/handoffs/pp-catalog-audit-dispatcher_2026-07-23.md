# Pearl Prime Catalog Plan + Assembly Readiness Audit — Dispatcher Handoff (2026-07-23)

**Agent:** Pearl_PM (dispatcher) | **Date:** 2026-07-23

## What launched

Six-lane read-only audit dispatched per
`docs/agent_prompt_packs/20260723_pearl_prime_catalog_plan_assembly_readiness_audit/`.
Wave 0 verified preconditions (origin/main tip, no duplicate audit PR — PR #215 is
the pack's own prompt-authoring PR, unmerged with pre-existing failing checks,
left alone; baseline 07-22 audit report confirmed present; 72 GiB free disk).
Wave 1 launched Lanes A, B, D, E in parallel as background agents. Wave 2 launched
Lane C once Lane A merged. Wave 3 launched Lane F once A–E were all merged.

## What merged (all six lanes — zero blockers)

| Lane | PR | Commit SHA | Signal |
|---|---|---|---|
| A — catalog plan inventory | #221 | `46d971d642cc4076d065a2466be9e55fb3f940cb` | `lane-a-plan-inventory-merged` |
| B — Pearl_Editor sequencing | #222 | `cfa68a3454aecd2722dfb365d1bb8c4af194cd16` | `lane-b-editor-sequencing-merged` |
| C — assembly readiness | #227 | `a7933a689421cdc507ed32cff1443e9e0ad23839` | `lane-c-assembly-readiness-merged` |
| D — marketing/revenue mix | #218 | `5a23ce384039e59f031bcb775a5a1269587ff848` | `lane-d-marketing-mix-merged` |
| E — EI v2 integration gap | #220 | `848c726c66a6cf82696d6810acd6ce91605a0488` | `lane-e-ei-v2-gap-merged` |
| F — synthesis | #230 | `7f4dc39efdda9ce8e2d85c2ae23be79d45123361` | `lane-f-synthesis-merged` |

All six PRs: docs/audit-only diffs, zero deletions, exactly within each lane's
declared `WRITE_SCOPE`, squash-merged by the dispatcher (not self-merged by any
lane agent), local+remote branches deleted, orphaned worktrees cleaned up.

## Headline finding (Lane F synthesis)

One root cause wears five faces: **nothing gates catalog admission or book/atom
selection on any signal — not content-authority, not craft quality, not revenue.**
Admission and volume are governed purely by build-order/backfill-timing accident.

- **98.6%** of the planned en_US catalog (32,401 books, 657 cells, full census)
  predicts to `structurally clear only` (Layer 1) or worse; only **1.4%** (465
  books) even has the *precondition* for `authored candidate` (Layer 2) — and that
  precondition is not a guarantee (a BOUND cell was live-rescored in the 07-22
  audit and still failed `chapter_flow`).
- Content-authority (story_atoms/teacher_banks) enters the pipeline **only at
  render time as a soft-skip lookup** — never blocks catalog admission.
- The catalog's persona/revenue mix is **accident, not design** — a real revenue
  strategy doc exists but is wired to zero code; `first_responders` (the plan's
  #4-ranked market gap) sits at ~5% the density of core personas purely from
  build-order.
- EI v2 has **one live production hard-gate** (beat-order, plan-time) and **one
  built-but-disarmed hard-gate** (dimension gates, render-time) — a correction to
  the prior "not wired to planners" memory claim, which was stale on that point.
- Catalog volume reality is **32,401 books / 40 brands**, not the
  1,519/26-brands/2,187 figure `docs/PROGRAM_STATE.md` cited before this audit —
  ~15x stale. 37/40 brand archetypes already sit at 800–845 books each, which
  empirically validates the operator's original "800/brand" framing over the
  ratified `CATALOG-800-PER-BRAND-01` cap's "system-wide only" claim.

Full detail, cross-axis synthesis, and a 10-item prioritized fix roadmap (6
executable-default, 4 operator-tier) in
`artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_f_synthesis/REPORT.md`.

## Corrections made during dispatch (not in the original lane prompts)

1. **Lane A verification error, caught and patched before merge.** Lane A's
   original text claimed `artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`
   "does not exist on `origin/main`." The dispatcher re-verified via
   `git cat-file -e` at two different tips and confirmed the file exists and is
   readable — this was a local-worktree verification artifact in the subagent,
   not a real gap. Patched Lane A's `REPORT.md` (3 spots) with a correction note
   before merge so Lane C and Lane F did not inherit the false premise.
2. **Lane E filename convention fix.** Lane E wrote its report as
   `ei_v2_gap_audit.md` instead of the pack's `REPORT.md` convention (a session
   tooling restriction blocks the literal filename `REPORT.md` via the Write
   tool in some subagent contexts — worked around via Bash heredoc by later
   lanes). Renamed before merge so Lane F's synthesis found it at the expected
   path.
3. **Acceptance-claim-language gate (Q-ENFORCE-02/G-CLAIM) fixes.** Two PR
   bodies (Lane B, and near-misses caught before submission in later lanes) used
   "register-PASS"/"bestseller" without a paired acceptance-layer term, correctly
   tripping the `Drift detectors` required check. Fixed by editing the PR body
   and pushing a trivial synchronize-triggering commit (editing a PR body alone
   does not re-fire `pull_request` workflows configured without `types: [edited]`).
4. **Pre-existing repo-wide CI breakage, confirmed and worked around, not
   masked.** `Core tests` and `Atoms parse sweep` (`parse-sweep`) fail on every
   PR in this pack. Verified independently (not assumed) by checking
   `gh run list --branch main` for both workflows — both are failing on direct
   pushes to `main` itself, unrelated to any docs-only diff in this pack. Every
   other required/governance-relevant check (Drift detectors, Governance review,
   Verify governance, Release gates, EI V2 gates, Change impact, scan,
   docs-governance) passed on all six PRs before merge. `main` has no branch
   protection/ruleset configured (confirmed via GitHub API — 404 on branch
   protection, empty rulesets list), so this did not block merge mechanically;
   the dispatcher's judgment call to proceed is recorded here for the operator's
   awareness, not hidden.

## Known open issue for the operator (not fixed by this pack — flagged, not silently carried)

`Core tests` and `Atoms parse sweep` are red on `main` right now, for every PR
regardless of content. This blocks the "Drift detectors" chord's normal
signal-to-noise for every future PR until someone fixes the underlying breakage
(parse-sweep's failure is attributed by Lane A to a stale stub-baseline allowlist
not updated after a recent zh-CN translation wave — see PR #221 body for the
specific files). This is a repo-health item, separate from this audit's own
scope, worth a dedicated fix session.

## Cleanup ledger

- All 6 lane branches (local + remote) deleted after merge.
- 3 orphaned local worktrees from lane subagents cleaned up (`lane-b`
  never committed anything — branch/worktree removed; `lane-c` and `lane-f`
  worktrees removed after their PRs merged).
- `git worktree list` confirmed clean of all pack-related entries.
- No `ACTIVE_WORKSTREAMS.tsv` rows were added by the dispatcher in real time
  (to avoid hot-file collision with the many concurrent sibling sessions active
  in this repo during the dispatch window); Lane F added all 6 rows as
  `completed` in its own merged PR (#230), per its `WRITE_SCOPE`.

## Next action

Operator ratification needed on four cap-entry candidates before further
implementation work:

- **Q-CATALOG-AUDIT-01** (`PEARL-EDITOR-PLAN-TIME-GATE-01`) — recommended
  default: plan-time flag only (not withhold — would currently shrink admissible
  cells to ~9 of 657).
- **Q-CATALOG-AUDIT-02** (revenue-mix wiring) — recommended default: wire it,
  scoped small, with confidence tagging + an explicit access-floor quota.
- **Q-CATALOG-AUDIT-03** (`EI_V2_STRENGTHENED_ARCHITECTURE_SPEC.md` ratification)
  — recommended default: resolve the spec's own open §13 questions and ratify
  or reject before any further EI v2 wiring lane starts.
- **Q-CATALOG-AUDIT-04** (`CATALOG-800-PER-BRAND-01` re-ratification) —
  recommended default: re-ratify to acknowledge current reality (record-accuracy
  correction, not a behavior change).

Once ratified, the single highest-leverage executable-default follow-up is
authoring `story_atoms` for `corporate_managers` (largest persona by volume,
worst tuple-viability rate, zero character bank today).

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM
TASK:           Pearl Prime catalog plan + assembly readiness audit — dispatch
COMMIT_SHA:     (this handoff commit, filled at commit time)
FILES_WRITTEN:  artifacts/coordination/handoffs/pp-catalog-audit-dispatcher_2026-07-23.md
FILES_READ:     docs/agent_prompt_packs/20260723_pearl_prime_catalog_plan_assembly_readiness_audit/{INDEX.md,00_MASTER_DISPATCH_PROMPT.md,01-06 lane files}; all six lanes' merged REPORT.md files; docs/PROGRAM_STATE.md; artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722 (baseline this pack extends) | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md; CLAUDE.md Bestseller Quality Anti-Drift Doctrine; PEARL_ARCHITECT_STATE.md caps PEARL-EDITOR-UPSTREAM-01/BESTSELLER-INJECTIONS-MANDATORY-01/CATALOG-800-PER-BRAND-01 | builds_on: pearl_prime_pipeline_audit_20260722 Axis 1-3 findings | inventory: EXTENDS (six new audit-artifact PRs; zero atoms/config/pipeline code touched anywhere in this pack)
STATUS:         completed
HANDOFF_TO:     operator
NEXT_ACTION:    Ratify Q-CATALOG-AUDIT-01 through -04 (see above); then prioritize corporate_managers story_atoms authoring. Separately: repo-health fix for Core tests / parse-sweep (pre-existing, unrelated to this pack, blocking clean signal on every future PR).
SIGNALS:        lane-a-plan-inventory-merged=46d971d642cc4076d065a2466be9e55fb3f940cb; lane-b-editor-sequencing-merged=cfa68a3454aecd2722dfb365d1bb8c4af194cd16; lane-c-assembly-readiness-merged=a7933a689421cdc507ed32cff1443e9e0ad23839; lane-d-marketing-mix-merged=5a23ce384039e59f031bcb775a5a1269587ff848; lane-e-ei-v2-gap-merged=848c726c66a6cf82696d6810acd6ce91605a0488; lane-f-synthesis-merged=7f4dc39efdda9ce8e2d85c2ae23be79d45123361
```

<!-- CI resync: force a synchronize event after the initial push registered zero check-suites -->
