EXECUTE

You are Pearl_Research, running Lane E: **EI v2 integration-gap audit.** The
operator wants "Enlightened Intelligence v2" genuinely wired into the planning +
assembly system, not just referenced. Prior memory claims EI v2 is "a scorer, not
an engine" — EMA weighted-sum, no GA, not wired to planners. This lane verifies
that claim live against current code, then produces a concrete, scoped wiring
proposal. Read-only audit + a written proposal — this lane does NOT implement the
wiring itself (that's an operator-tier architecture decision per the scale of
change implied).

STARTUP_RECEIPT
AGENT:              Pearl_Research
TASK:               Verify current EI v2 wiring status (scorer vs engine; wired to planner or not) and produce a scoped proposal for making it a real input to planning/assembly decisions
PROJECT_ID:         none — ws_pp_catalog_audit_lane_e_20260723
SUBSYSTEM:          ei_v2
AUTHORITY_DOCS:     artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv (ei_v2 row — owner Pearl_Research, authority_doc phoenix_v4/quality/ei_v2/, config config/quality/ei_v2_config.yaml); docs/DOCS_INDEX.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_e_ei_v2_gap/**
OUT_OF_SCOPE:       phoenix_v4/quality/ei_v2/** (read-only — do not edit any module); phoenix_v4/planning/** (read-only — do not wire anything in this lane); config/quality/ei_v2_config.yaml (read-only)
PROVENANCE:         research: memory claim "EI v2 = scorer not engine, EMA weighted-sum, NO GA, not wired to planners" — VERIFY, do not assume true; it may be stale | documents: whatever spec governs ei_v2 (search for it — SUBSYSTEM_AUTHORITY_MAP.tsv points at the code dir itself as authority_doc, which is unusual; confirm whether a real EI v2 spec exists elsewhere, e.g. docs/specs/*EI*V2* or docs/research/*) | builds_on: existing phoenix_v4/quality/ei_v2/ modules (list: cross_encoder_reranker.py, hybrid_selector.py, duration_fit.py, dimension_gates.py, emotion_arc_validator.py, semantic_dedup.py, domain_embeddings.py, manga_dialogue_gates.py, tts_readability.py, marketing_lexicons.py, visual_therapeutic.py, ei_warnings.py, safety_classifier.py, research_lexicons.py, llm_callback.py, learner.py) | inventory: EXTENDS (audit + proposal only; no code change)
BLOCKERS:           none known; re-verify live
READY_STATUS:       ready

## DISCOVERY REPORT (required)

1. Read every file in `phoenix_v4/quality/ei_v2/` at least at the function-
   signature/docstring level; read `dimension_gates.py`, `emotion_arc_validator.py`,
   and `learner.py` in full (these are the modules most likely to answer
   "scorer vs engine"). Read `config/quality/ei_v2_config.yaml` in full.
2. Grep the codebase for every CALL SITE that imports from `phoenix_v4.quality.
   ei_v2` — this is the ground truth for "wired" vs "referenced only". For each
   call site found, note: is it called during PLANNING (before a book is queued),
   during ASSEMBLY/render (post-hoc scoring of already-composed content), or only
   in a standalone QA/audit script (never in the production render path)?
3. Find any existing spec/research doc for "EI v2" / "Enlightened Intelligence"
   beyond the code itself — search `docs/`, `specs/`, `docs/research/` for
   "ei_v2", "EI V2", "Enlightened Intelligence". If genuinely none exists beyond
   scattered code comments, that absence is itself a finding (a scoring system
   with no authority doc, which is unusual for this repo's governance model).
4. Cross-reference the 07-22 audit's sample table — it reports an `ei_v2` score
   (e.g. "ei_v2 0.62") for the Waystream EPUB batch. Find where that number comes
   from in the code — confirm whether it's a single composite scalar (weighted-sum
   scorer) or a genuine multi-signal gate with hard-fail capability, and whether
   it runs at plan time, render time, or post-hoc audit time only.

## Mission

Produce `.../lane_e_ei_v2_gap/REPORT.md`:

1. **Verified current-state verdict**: confirm or correct the "scorer not engine,
   not wired to planners" claim with actual call-site evidence (file:line for
   every call site found). State plainly whether EI v2 currently has ANY
   hard-fail / gating power anywhere in the production path, or is purely
   informational.
2. **What "genuinely wired in" would concretely mean** — lay out 2-3 real options
   at different investment levels, e.g.:
   - (a) minimal: EI v2's existing dimension scores become a HARD gate in
     `register_gate.py` (analogous to F14) instead of informational-only:
   - (b) medium: EI v2 signals feed `catalog_planner.py` / plan-time cell
     selection (e.g., don't plan a cell whose predicted EI v2 dimensions would
     fail) — this is the "engine" reading of the operator's ask;
   - (c) larger: EI v2's `learner.py` becomes a genuine feedback loop (its name
     implies this was the intent) — verify if `learner.py` currently does
     anything with feedback data or is a stub, and what wiring it for real would
     require.
   For each option, name the files that would need to change, the blast radius,
   and whether it's executable-default work or needs an operator-tier ratification
   (given `docs/PEARL_ARCHITECT_STATE.md`'s registry/cap-entry discipline, a
   change of this scope likely needs a new cap entry — say so).
3. **Recommended default** — pick one of the options above as the recommended
   next step, with rationale, per Router Operating Principle §2 (decide
   autonomously, recommend a default, let the operator ratify or override).

## DO NOT

- Do not edit any `phoenix_v4/quality/ei_v2/*` file.
- Do not wire anything into the planner or register_gate in this lane — proposal
  only, this is architecture-change-scale work requiring its own dedicated
  implementation lane after operator sign-off.
- Do not claim EI v2 is "not real" or "fake" — it has real modules; the finding is
  about wiring/gating power, not existence.

## Landing contract

MERGED (branch `agent/pp-catalog-audit-lane-e-20260723`, PR, checks green, squash,
signal `lane-e-ei-v2-gap-merged=<sha>`, branch deleted) or BLOCKED with evidence +
handoff + NEXT_ACTION.

## Cleanup ledger

No worktree. Branch deleted after merge.

## Handoff

`artifacts/coordination/handoffs/pp-catalog-audit-lane_e_2026-07-23.md`

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Research
TASK:           Lane E — EI v2 integration-gap audit + wiring proposal
COMMIT_SHA:     <full SHA>
FILES_WRITTEN:  artifacts/qa/pearl_prime_catalog_assembly_audit_20260723/lane_e_ei_v2_gap/REPORT.md + evidence/
FILES_READ:     <ei_v2 modules + config + call sites actually traced>
PROVENANCE:     research: memory claim VERIFIED/CORRECTED (state which) | documents: <any EI v2 spec found, or "NONE found" | builds_on: phoenix_v4/quality/ei_v2/* (unchanged) | inventory: EXTENDS
STATUS:         <completed / partial / blocked>
HANDOFF_TO:     Lane F (synthesis) + operator (for the wiring-option ratification)
NEXT_ACTION:    <specific>
SIGNAL:         lane-e-ei-v2-gap-merged=<sha>
```
