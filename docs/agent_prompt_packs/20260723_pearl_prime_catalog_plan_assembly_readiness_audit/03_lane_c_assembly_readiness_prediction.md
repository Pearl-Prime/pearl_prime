EXECUTE

You are Pearl_Prime, running Lane C: **catalog-scale assembly-readiness
prediction.** This is the core of the operator's ask: "look at a robust number of
plans and audit assembly — but don't assemble." You are extending the 07-22 audit
(`artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md`) from 3 sample
cells to a real catalog-scale sample, using Lane A's plan inventory
(`artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_a_plan_inventory/REPORT.md`)
as your sampling frame. **You do not render or assemble a single new book in this
lane.** You predict, from static evidence, what assembly would produce if run.

STARTUP_RECEIPT
AGENT:              Pearl_Prime
TASK:               Predict assembly readiness (bestseller register capacity, research_fit bind status, cohesion risk, atom depth) for a robust catalog-scale sample of PLANNED (not yet rendered) cells, without rendering any of them
PROJECT_ID:         none — ws_pp_catalog_audit_lane_c_20260723
SUBSYSTEM:          core_pipeline; pearl_prime
AUTHORITY_DOCS:     artifacts/qa/pearl_prime_pipeline_audit_20260722/AUDIT_REPORT.md (full — this lane extends its Axis 1-3 methodology); docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md; CLAUDE.md Bestseller Quality Anti-Drift Doctrine
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/**
OUT_OF_SCOPE:       any run_pipeline.py / build_epub.py invocation (# CI-ALLOWLIST: legacy-registry-ok — prose prohibition, not a production invocation); any composer/gate CODE edit; config/source_of_truth/** (read-only)
PROVENANCE:         research: pearl_prime_pipeline_audit_20260722 (methodology + Axis 1-3 findings this extends); lane_a_plan_inventory (sampling frame) | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md (4-layer taxonomy — mandatory framing for every verdict in this lane) | builds_on: atom_coverage_audit.py, check_research_fit_honesty.py, check_book_story_authored.py, register_gate.py (existing tools, read/dry-run only) | inventory: EXTENDS
BLOCKERS:           gated on lane-a-plan-inventory-merged signal (see prerequisite check)
READY_STATUS:       gated

## Prerequisite gate check (verify before starting)

Confirm `lane-a-plan-inventory-merged=<sha>` exists (merged PR or
`ACTIVE_WORKSTREAMS.tsv` row for `ws_pp_catalog_audit_lane_a_20260723` = completed).
If Lane A is genuinely BLOCKED (not just slow), you may substitute its raw
evidence/plan-listing (even unmerged, on its pushed branch) as your sampling frame
— note this substitution explicitly in your DISCOVERY REPORT rather than silently
proceeding as if A had merged.

## Live-state reconciliation

`git fetch origin`; re-derive tip (authoring anchor
`244955eaa01ddd9093001d184b41ba71e2a84a2b`, 2026-07-23 — do not trust as current).
Re-read Lane A's actual merged REPORT.md for the real per-brand plan inventory
rather than any number stated in this prompt.

## DISCOVERY REPORT (required)

1. Read Lane A's `REPORT.md` in full. Note especially: which persona×topic×engine
   cells are PLANNED at all (any brand), and which brands/personas the 07-22 audit
   already flagged as thin (`corporate_managers` = zero story_atoms despite being
   the EPUB workhorse persona; the 6 personas with ANY `story_atoms/anchored/`
   bank: `educators`, `first_responders`, `gen_z_professionals`, `healthcare_rns`,
   `millennial_women_professionals`, `working_parents`).
2. Confirm the read-only tools available for prediction without rendering:
   `scripts/inventory/atom_coverage_audit.py` (CANONICAL.txt presence — bank
   exists, not consumption); presence/absence of
   `story_atoms/<persona>/anchored/<topic>/<engine>/` directories (consumption
   capability); `config/planning/chapter_thesis_bank.yaml` topic-overlay coverage
   (currently 8 topics per the 07-22 audit — cohesion-risk proxy); whether
   `check_research_fit_honesty.py` / `check_book_story_authored.py` can run
   against a PLANNED (unrendered) cell at all, or only against an already-rendered
   `book.txt` — if the latter, your "prediction" for unrendered cells must be
   inferred from bank presence/absence, not a live gate run, and you must say so.

## Mission

Draw a **robust, brand-diverse sample** — not just the 3 cells the 07-22 audit
already covered. Target: at least 2 persona×topic×engine cells per brand-archetype
identified by Lane A (Waystream + at least 4 non-Waystream brands spanning
different personas), smoke (2-3 cells) → pilot (10-15 cells) → scale (as many as
your evidence tools support cheaply — this is static analysis, not rendering, so
scale should be large; do not artificially cap it below what `atom_coverage_audit.py`
and directory presence checks can cover in one pass across the full plan set).

For every sampled cell, predict and record:

| Field | How derived (read-only) |
|---|---|
| CANONICAL.txt atom bank present? | `atoms/<persona>/<topic>/<engine>/CANONICAL.txt` exists (per atom_coverage_audit.py) |
| story_atoms character bank present? | `story_atoms/<persona>/anchored/<topic>/<engine>/` exists |
| Predicted research_fit bind status | BOUND (both present) / UNBOUND-thin (canonical present, story_atoms absent) / UNKNOWN (neither present — would likely hard-fail InsufficientVariantsError) |
| Thesis-bank coverage | topic-overlay present in chapter_thesis_bank.yaml, or falls to intent→engine baseline (cohesion-risk flag) |
| Predicted acceptance-layer ceiling | per the scorecard: UNBOUND cells cap at "structurally clear" even if register_gate would PASS; cells with neither bank likely never reach a renderable state |

Produce `.../lane_c_assembly_readiness/REPORT.md` with:

1. The full sample table above.
2. **Catalog-scale rollup**: of everything planned (per Lane A's count), what
   fraction predicts to each ceiling (structurally-clear-only / would-likely-hard-
   fail / has-both-banks-so-authored-candidate-possible)? This is the number the
   operator actually asked for — "is our plan and assembly idea working" at scale,
   not just on 3 cells.
3. **Where the ceiling is worst**: name the specific brands/personas most exposed
   (build on the 07-22 finding that the workhorse persona `corporate_managers` has
   zero story_atoms — is this the worst case, or are there others equally or more
   exposed once you look catalog-wide?).
4. Explicit acknowledgment of what this lane did NOT verify (it predicts from
   static bank presence; it does not confirm a cell would actually pass
   `chapter_flow`/`book_quality` gates the way the 07-22 audit's live re-scored
   samples showed even BOUND cells can still Reject — cite `healthcare_rns ×
   burnout` seed 43006 as the cautionary precedent: bound ≠ shippable).

## DO NOT

- Do not render, assemble, or invoke any pipeline entry point that produces a new
  book file.
- Do not report a predicted BOUND status as "shippable" — bound is necessary, not
  sufficient (see healthcare_rns 43006 precedent above).
- Do not silently cap your sample below what static tooling can cheaply cover —
  if you stop early, name the exact reason (time/tool limit) in the report, not
  silently.

## Landing contract

MERGED (branch `agent/pp-catalog-audit-lane-c-20260723`, PR, checks green, squash,
signal `lane-c-assembly-readiness-merged=<sha>`, branch deleted) or BLOCKED with
evidence + handoff + NEXT_ACTION.

## Cleanup ledger

No worktree. Branch deleted after merge.

## Handoff

`artifacts/coordination/handoffs/pp-catalog-audit-lane_c_2026-07-23.md`

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Prime
TASK:           Lane C — catalog-scale assembly-readiness prediction
COMMIT_SHA:     <full SHA>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_c_assembly_readiness/REPORT.md + evidence/
FILES_READ:     <Lane A report + 07-22 audit + tools actually run>
PROVENANCE:     research: pearl_prime_pipeline_audit_20260722; lane_a_plan_inventory | documents: PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md | builds_on: atom_coverage_audit.py, check_research_fit_honesty.py, check_book_story_authored.py | inventory: EXTENDS
STATUS:         <completed / partial / blocked>
HANDOFF_TO:     Lane F (synthesis)
NEXT_ACTION:    <specific>
SIGNAL:         lane-c-assembly-readiness-merged=<sha>
```
