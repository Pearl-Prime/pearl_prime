EXECUTE

You are Pearl_PM, dispatching the **Pearl Prime Catalog Plan + Assembly Readiness
Audit** (2026-07-23). Do not summarize state, do not produce a plan, do not end the
turn after any intermediate step. The turn ends only on a named signal or one
concrete BLOCKER with evidence. Do not ask the operator to merge routine
clean/green docs-only PRs — merge them yourself once required checks are terminal
green.

STARTUP_RECEIPT
AGENT:              Pearl_PM
TASK:               Dispatch 6-lane read-only audit of Pearl Prime catalog planning + assembly readiness
PROJECT_ID:         none (new audit program; open one in ACTIVE_PROJECTS.tsv if this becomes a standing lane)
SUBSYSTEM:          pearl_pm coordination; core_pipeline; pearl_prime; ei_v2; marketing
AUTHORITY_DOCS:     docs/agent_brief.txt; docs/PROMPT_ROUTER_OPERATING_MANUAL.md; docs/PROGRAM_STATE.md; docs/SESSION_UNITY_PROTOCOL.md; docs/DOCS_INDEX.md; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; this pack's INDEX.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/**; artifacts/coordination/handoffs/pp-catalog-audit-*.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (dispatcher rows only); docs/PROGRAM_STATE.md (Lane F only, after A-E merged)
OUT_OF_SCOPE:       any run_pipeline.py invocation that renders/assembles a NEW book (# CI-ALLOWLIST: legacy-registry-ok — prose prohibition, not a production invocation); any composer/register_gate/enrichment_select.py CODE edit; any live marketing copy or campaign write; any credential or GHL write
PROVENANCE:         research: this pack's INDEX.md + artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md (baseline it extends) | documents: docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md; CLAUDE.md Bestseller Quality Anti-Drift Doctrine; docs/PEARL_ARCHITECT_STATE.md caps PEARL-EDITOR-UPSTREAM-01 / BESTSELLER-INJECTIONS-MANDATORY-01 / CATALOG-800-PER-BRAND-01 | builds_on: pearl_prime_pipeline_audit_20260722 (Axis 1-3 findings) | inventory: EXTENDS (new audit artifacts only; no existing function touched)
BLOCKERS:           none known at authoring time; re-verify live
READY_STATUS:       ready

## Wave 0 — verify before fan-out

1. `git fetch origin && git rev-parse origin/main` — confirm the live tip. If it has
   moved past `244955eaa01ddd9093001d184b41ba71e2a84a2b`, re-read
   `docs/PROGRAM_STATE.md` and this pack's INDEX.md premises before proceeding;
   correct any stale claim you find rather than carrying it forward silently.
2. `gh pr list --state open --search "pearl prime catalog"` and
   `--search "assembly readiness"` — confirm no duplicate audit PR exists. PR #56
   (`docs(piper): Pearl Prime pipeline audit prompt`) is the prior prompt pack, not
   a duplicate of this one — leave it alone.
3. Confirm `artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md` still
   resolves on `origin/main` (it must — every lane below cites it as the baseline
   to extend, not re-derive).
4. Disk precheck: `df -h .` — proceed only if ≥20 GiB free (74 GiB free at
   authoring time; standard clean branches from `origin/main`, no worktrees needed
   for these lanes since none touch LFS-heavy render paths).
5. Open/verify `ACTIVE_WORKSTREAMS.tsv` rows for
   `ws_pp_catalog_audit_lane_{a,b,c,d,e,f}_20260723` (status `proposed` → flip to
   `active` as each lane launches). Serialize this TSV write — you are the only
   writer.

## Wave 1 — launch A, B, D, E in parallel (independent lanes)

Launch four agents concurrently, one per lane file in this directory:
`01_lane_a_catalog_plan_inventory.md`, `02_lane_b_editor_contract_sequencing.md`,
`04_lane_d_marketing_revenue_mix.md`, `05_lane_e_ei_v2_integration_gap.md`. Paste
each file's full contents verbatim as that agent's starting prompt. Do not
summarize or truncate them.

Poll each to a terminal state (MERGED or BLOCKED). Do not arm a watcher and end the
turn — poll to resolution. If one blocks, the other three continue; do not stall
the wave on a single blocked lane.

## Wave 2 — launch C once A is MERGED

C (`03_lane_c_assembly_readiness_prediction.md`) needs Lane A's catalog plan
inventory (the concrete list of planned persona×topic×engine×brand cells) to draw
its sample from. Gate check: `lane-a-plan-inventory-merged=<sha>` must exist on a
durable surface (the merged PR, or `ACTIVE_WORKSTREAMS.tsv`) before you launch C.
If A is BLOCKED, do not skip C — instead have C sample directly from the raw plan
artifacts A discovered (A's evidence dir still has value even if A's PR itself
blocked on something unrelated like a hot-file collision); note the substitution in
C's DISCOVERY REPORT.

## Wave 3 — launch F once A, B, C, D, E are all terminal

F (`06_lane_f_synthesis_report.md`) is the only lane that touches
`docs/PROGRAM_STATE.md`. Do not launch it until all five lanes have reported a
terminal state (MERGED or BLOCKED-with-evidence). Paste its full contents,
substituting in the five signal tokens / SHAs / evidence paths you collected.

## Merge authority

You may merge any lane's PR yourself once: required checks are terminal green,
`git diff --stat origin/main` shows only the intended new files under
`artifacts/qa/…` or `docs/…` (no unrelated deletions, no hot-file rewrites outside
Lane F's PROGRAM_STATE.md addition), and the PR is docs/audit-only (no runtime
code change). If a lane's diff touches anything outside its declared WRITE_SCOPE,
do not merge — report it as a BLOCKER instead of self-correcting via `--admin` or
skipped review.

## DO NOT

- Do not let any lane invoke `run_pipeline.py`, `build_epub.py`, or any renderer to produce a NEW book. <!-- CI-ALLOWLIST: legacy-registry-ok — prose prohibition, not a production invocation -->
  Static/predictive analysis and re-running EXISTING
  gate/audit scripts (`atom_coverage_audit.py`, `register_gate.py` against
  ALREADY-RENDERED artifacts on disk, `check_research_fit_honesty.py`) against
  already-produced evidence is fine; producing new render output is not.
- Do not treat a gate-PASS or a config's existence as "done" — every lane report
  must use the six-layer taxonomy from CLAUDE.md.
- Do not let Lane F declare "100%" or "bestseller" anywhere without the strict
  evidence chain in `agent_brief.txt` §15.
- Do not skip Wave 0 step 1's live re-fetch, even though this prompt already did it
  once at authoring time.

## Landing contract

Each lane: MERGED (PR opened from clean `origin/main` branch, checks green, squash
merged, signal emitted, branch deleted) or BLOCKED (one concrete blocker,
evidence/artifacts pushed to the lane's remote branch, handoff written, exact
NEXT_ACTION). No third state.

## Cleanup ledger (dispatcher)

- All lane branches merged-and-deleted or explicitly HOLD-declared with reason.
- No worktrees were created by this dispatcher (docs/qa-only lanes); confirm none
  were incidentally left by a sub-agent (`git worktree list`).
- `ACTIVE_WORKSTREAMS.tsv` rows for all 6 lanes reflect terminal status.

## Dispatcher handoff

Write `artifacts/coordination/handoffs/pp-catalog-audit-dispatcher_2026-07-23.md`
covering: what launched, what merged (SHAs), what blocked (evidence), the six
signal tokens found/emitted, and NEXT_ACTION if anything remains open.

## CLOSEOUT_RECEIPT (dispatcher)

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM
TASK:           Pearl Prime catalog plan + assembly readiness audit — dispatch
COMMIT_SHA:     <last dispatcher-authored commit SHA, or "no commits">
FILES_WRITTEN:  <handoff path; ACTIVE_WORKSTREAMS.tsv row updates; PROGRAM_STATE.md if Lane F merged>
FILES_READ:     <this pack's INDEX.md + all 6 lane files + PROGRAM_STATE.md + AUDIT_REPORT.md 07-22>
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722 | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md; PEARL_ARCHITECT_STATE.md caps | builds_on: 07-22 audit Axis 1-3 | inventory: EXTENDS
STATUS:         <completed / partial / blocked>
HANDOFF_TO:     <operator, or "none">
NEXT_ACTION:    <specific next step if not fully complete>
SIGNALS:        lane-a-plan-inventory-merged=<sha or BLOCKED>; lane-b-editor-sequencing-merged=<sha or BLOCKED>; lane-c-assembly-readiness-merged=<sha or BLOCKED>; lane-d-marketing-mix-merged=<sha or BLOCKED>; lane-e-ei-v2-gap-merged=<sha or BLOCKED>; lane-f-synthesis-merged=<sha or BLOCKED>
```
