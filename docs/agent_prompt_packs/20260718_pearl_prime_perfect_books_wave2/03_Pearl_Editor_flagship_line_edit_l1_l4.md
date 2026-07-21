# 03 — Wave 1.5: Flagship Line-Edit L1–L4 → first true `system working` (Pearl_Editor)

EXECUTE. This is **the actual flagship register lever** (spec §3.D / §5 step 4) — the
lane that earns Layer-3 `system working`. It is line-editing, NOT composer work. Do
not stop at summary/plan. Turn ends only on the signal below or one concrete BLOCKER.

GATE CHECKS (signals, not narrative):
1. `grep "perfect-books-wave2-substrate=" artifacts/qa/perfect_books_wave2_20260718/SUBSTRATE_LOCK.md` returns a value.
2. `grep "perfect-books-wave2-bankfill=" artifacts/coordination/handoffs/perfect_books_wave2_bankfill_2026-07-18.md` returns a full SHA (banks filled — this lane is SERIAL after Lane 02; both write atom banks).
Either absent ⇒ STOP.

```
STARTUP_RECEIPT
AGENT: Pearl_Editor (lane 03)
TASK: Run ONTGP line-edit on 3 designated flagship cells (Ch1/mid/last), fix via atom rewrite + seam paragraphs + chapter-open (NOT composer), earn ONTGP_VERDICT.md=PASS, promote winning seams into banks
SUBSYSTEM: teacher_mode + core_pipeline (flagship line-edit lane) (authority: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.D; artifacts/qa/flagship_line_edit/README.md)
AUTHORITY_DOCS: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.D (L1–L4) + §0 acceptance contract; docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md; docs/BESTSELLER_DRIFT_ROOT_CAUSE_2026-07-02.md; CLAUDE.md anti-drift doctrine
WRITE_SCOPE: artifacts/qa/flagship_line_edit/<date>/ (ONTGP verdicts + edited manuscripts + evidence); atoms/** seam/rewrite edits ONLY for the 3 designated cells; artifacts/qa/perfect_books_wave2_20260718/lane03/
OUT_OF_SCOPE: composer/topology (banned lever); register_gate/F16/DEF4 code; frozen flagship goldens (gen_z×anxiety CANONICAL_FLAGSHIP_*) + atoms feeding them; other cells' banks; hot coordination files
PROVENANCE:
  research:  ANALYSIS_REPORT.md "strong local prose + weak whole-book cohesion" finding (§7) — the exact gap line-edit closes
  documents: PEARL_PRIME_PERFECT_BOOKS_SPEC.md §3.D + the line-edit README scaffold
  builds_on: the bank-filled cells from Lane 02 + the flagship read method that already earned PROVEN-AT-BAR on gen_z×anxiety (hand-seamed atoms read as bestseller)
  inventory: EXTENDS (seams promoted to reusable atoms L4; nothing removed)
BACKGROUND_SAFE: no   RESUME_SURFACE: artifacts/qa/flagship_line_edit/<date>/ + offline ref
```

## DISCOVERY REPORT

1. Read `artifacts/qa/flagship_line_edit/README.md` (the Wave-1 scaffold) — follow
   its dir structure + `ONTGP_VERDICT.md` shape. EXTEND it; do not invent a parallel.
2. Confirm the 3 cells (Q-W2-CELLS-01): default `corporate_managers×burnout×overwhelm`
   + 2 machine-clean, bank-filled cells from Lane 02's handoff (distinct personas;
   NEVER the frozen gen_z×anxiety golden). Verify each renders Layer-1 PASS + DEF4=0
   from Lane 02's evidence before editing.
3. Reconcile: does an `ONTGP_VERDICT.md` already exist for any cell? If PASS →
   RECONCILE, skip it.

## MISSION (L1–L4)

- **L1** Render each of the 3 cells with the four-piece chord
  (`--pipeline-mode spine --quality-profile production --exercise-journeys --render-book`).
- **L2 ONTGP (human/Pearl_Editor — NOT a keyword proxy):** read Ch1, Ch5/6, and the
  last chapter. Score each ONTGP dimension PASS/WEAK/FAIL — inter-atom cohesion,
  chapter-open Orient, motif/tool ledger continuity, whole-book arc, seam visibility
  (exercise wrapper / shift phrase / foreign-persona bleed). Metric of record is
  **whole-book cohesion / F14 beat-share**, NOT register-PASS count. Write
  `ONTGP_VERDICT.md` with PASS/WEAK/FAIL per dimension + quoted evidence lines.
- **L3 Fix** WEAK/FAIL via **atom rewrite / seam paragraphs / chapter-open rewrite** —
  NOT composer retune (unless ONTGP *proves* a composer bottleneck, which requires an
  explicit finding, not a default). Re-render, re-ONTGP until PASS or a real blocker.
- **L4 Promote** the winning seams into reusable BANK atoms (so the gain is
  systemic, not a one-off manuscript patch), and record the atom edits.

A cell reaches `system working` ONLY with `ONTGP_VERDICT.md`=PASS on the sampled
chapters. That is this lane's ceiling. **Do NOT touch Layer 4** — blind-10 is the
operator's (Lane 05 preps it).

## SMOKE → PILOT → SCALE

Smoke: L1+L2 on Ch1 of cell #1 (one ONTGP dimension pass proven end-to-end). Pilot:
full L1–L4 on cell #1 → first `ONTGP_VERDICT.md`=PASS. Scale: cells #2 and #3.
Checkpoint ≤10 min (verdict-in-progress to the proof root); tee renders and poll;
three no-progress intervals ⇒ land the cells that reached PASS, mark the rest WEAK
with the blocker. Even 1 true `system working` cell is real progress — do not fake 3.

## DO NOT

- Do NOT tune the composer/topology as the register lever (§2 + CLAUDE.md — this
  instinct IS the drift). No dwell-beat / word-floor injectors. No gate-weakening.
- Do NOT edit the frozen goldens or atoms feeding them (run parity if unsure).
- Do NOT record ONTGP from a keyword/heuristic proxy — it must be a real read.
- Do NOT claim `bestseller register` / run or fake blind-10. No `git add -A`.

## LANDING + CLEANUP + HANDOFF

Land the `ONTGP_VERDICT.md`s + edited-manuscript evidence + promoted seam atoms via
the INDEX recipe onto `offline/perfect-books-wave2-lineedit-20260718` (or PR→merge if
github; G-CLAIM requires `system working` to carry the Layer-3 artifact path — it
does: the ONTGP_VERDICT.md). Explicit paths; diff-stat gate; run flagship parity if
any promoted atom could feed the goldens. Cleanup: render scratch removed/declared;
CLEANUP LEDGER in handoff. Handoff:
`artifacts/coordination/handoffs/perfect_books_wave2_lineedit_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_Editor_lane03
CELLS_ATTEMPTED=<3> SYSTEM_WORKING=<n with ONTGP_VERDICT.md=PASS>
ONTGP_VERDICTS=<paths under artifacts/qa/flagship_line_edit/<date>/>
FIX_METHOD=atom-rewrite/seam/chapter-open (composer untouched: confirm)
SEAMS_PROMOTED=<atom PRs/paths — L4>
COHESION_METRIC=<F14 beat-share / whole-book deltas, not register-PASS count>
FLAGSHIP_PARITY=<byte-identical yes/no>
ACCEPTANCE_LAYER=system working on <n> cells (Layer-3 artifact present); system stays authored candidate until operator blind-10
LANDED=<ref@full-sha | merge-sha>
CLEANUP_COMPLETE=yes
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_lineedit_2026-07-18.md
SIGNAL=perfect-books-wave2-lineedit=<full-sha>
NEXT_ACTION=Lane 05 assembles the operator blind-10 packet from these cells
```
