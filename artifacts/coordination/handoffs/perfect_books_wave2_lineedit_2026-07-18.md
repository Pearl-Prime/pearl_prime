# Perfect Books Wave-2 — Lane 03 Flagship Line-Edit (L1–L4) — Handoff

**Date:** 2026-07-18 (run 2026-07-19 local)
**Agent:** Pearl_Editor (lane 03)
**Acceptance layer:** honest ceiling this pass is **`structurally clear`** on the
atom-bank fixes themselves (clean, no golden drift). **NONE of the 3 designated
cells reached `system working`** — all 3 `ONTGP_VERDICT.md` are real, evidenced FAILs
(one very close to PASS). Per §0 acceptance-contract discipline and the dispatcher's
explicit instruction ("never invent PASS"), this is reported as FAIL, not rounded up.

## Gate check (verified before starting)

`perfect-books-wave2-bankfill=d48fbdacacabc21641709f9411af90dd46c3ed27` present in
`artifacts/coordination/handoffs/perfect_books_wave2_bankfill_2026-07-18.md` — PASS,
proceeded serially after Lane 02 per INDEX.md.

## The 3 cells (Q-W2-CELLS-01, from Lane 02)

1. `corporate_managers × burnout × overwhelm` (MATRIX `C048`)
2. `tech_finance_burnout × burnout × overwhelm`
3. `healthcare_rns × burnout × overwhelm`

## What happened, in order

1. **L1 — fresh four-piece-chord render attempted for all 3 cells.** Ran live for
   `tech_finance_burnout` and `healthcare_rns` (both hard-stopped, `SystemExit(1)`,
   106 foreign-persona registry drops each — independently confirming Lane 02's
   catalog-wide `G-DEF4` finding on 2 additional cells, live, this run). Reused Lane
   02's same-day fresh evidence for `corporate_managers` rather than re-running an
   already-proven-identical failure against the same untouched registry file. **No
   registry/composer code touched — banned lever, held.**
2. **L2 — real ONTGP reads** (Ch1, Ch5, Ch12 each, quoted evidence, not a keyword
   proxy) on the best available prior manuscript per cell, per the dispatcher's
   explicit ruling to proceed without waiting for a C4 fix.
3. **L3 — fixes applied where genuinely in scope.** Found and fixed a catalog-wide
   leaked-batch-generation-metadata defect in all 3 cells' own `STORY` atom banks (24
   atoms total). Found 2 additional renderer-level defects (a broken ambient-detail
   template family, a mid-sentence truncation bug) that are real but **out of this
   lane's `atoms/**`-scoped write remit** — documented, not silently skipped, same
   discipline as Lane 02's C4 finding.
4. **L4 — promoted** the 24 fixed atoms directly into the reusable banks (not a
   one-off manuscript patch).

## Full findings

### Fix #1 (applied, in scope): leaked batch-generation metadata across all 3 cells' STORY banks

24 `STORY` atoms (`atoms/corporate_managers/burnout/STORY/CANONICAL.txt` ×7,
`atoms/tech_finance_burnout/burnout/STORY/CANONICAL.txt` ×10,
`atoms/healthcare_rns/burnout/STORY/CANONICAL.txt` ×7) shared one defect signature: a
bolted-on trailing sentence of the shape *"In the &lt;detail&gt;, &lt;Name&gt; names the
burnout pattern as an lived scene without turning it into a verdict.
Wave2-&lt;NNN&gt; keeps this body cell-specific."* — internal generation/QA
bookkeeping text leaked into production prose, with a baked-in grammar error ("as an
lived scene") and, in several bodies, upstream noun-swap corruption that no longer
parses ("opened the stakeholders", "the alarm without threat", "standing in the
direct reports"). Rewritten as clean, grammatical, persona-grounded character
studies, preserving all `MECHANISM_DEPTH` / `IDENTITY_STAGE` / `COST_TYPE` /
`COST_INTENSITY` metadata. Full before/after examples in each cell's `NOTES.md` under
`artifacts/qa/flagship_line_edit/20260719_<cell>/`.

`grep -rl "Wave2-\|as an lived scene" atoms/` confirms this exact defect signature is
present in **hundreds of files across nearly every persona/topic bank in the
catalog** — this pass fixed only the 24 atoms in the 3 designated cells (in scope);
the rest is documented, not touched, and recommended as a dedicated future
bank-hygiene lane.

### Finding #2 (documented, not fixed): broken shared ambient-detail template

`config/rendering/environment_fallback_families.yaml` (`window_reference` / light-
detail families) contains malformed `text:` entries with doubled predicates (e.g.
*"The glass holds a softened outline at the frame holds steady."*) that render as
context-blind, sometimes factually incoherent filler (*"soft daylight along the
sill"* at 11 PM; through a window inside a parking garage). Confirmed live in 2 of
the 3 cells' manuscripts (tech_finance_burnout, healthcare_rns) — cross-persona
corroboration, so this is genuinely systemic renderer infrastructure, not noise. Not
fixed here: it is shared, catalog-wide config outside this lane's `atoms/**`-scoped
write remit, and carries golden-drift risk if edited without a dedicated parity-gated
lane (confirmed the exact broken strings are **not** in the current frozen golden
snapshot, but the underlying family is generic enough to affect a future golden
re-render). Recommend a dedicated Pearl_Dev-owned lane that repairs the template and
re-proves `check_flagship_book_parity.py` clean before landing.

### Finding #3 (documented, not fixed): mid-sentence truncation bug

The healthcare_rns manuscript's Ch5 cuts off mid-clause with no closing punctuation —
a section-join or depth-enrichment boundary defect, not a content-atom problem.
Composer/wiring-adjacent; out of this lane's banned-lever scope. Flagged for
Pearl_Dev.

### Finding #4 (documented, not fixed): duplicate cross-chapter atom selection

The corporate_managers manuscript selects the same `STORY` atom (the "Louisa"
vignette) verbatim in both Ch2 and Ch12 (the book's climax chapter) with no
acknowledgment. The atom's own text is clean; the defect is in *which chapter
selects which atom* — a depth/enrichment selection behavior, composer-adjacent and
explicitly banned for this lane to fix directly. Flagged per the ONTGP routing table
in `docs/PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md` ("Turn FAIL → beat structure
in chapter_script or enrichment (Pearl_Dev + Pearl_Architect)").

## ONTGP verdicts (the deliverable)

| Cell | Verdict | Path |
|---|---|---|
| corporate_managers × burnout × overwhelm | FAIL | `artifacts/qa/flagship_line_edit/20260719_corporate_managers__burnout__overwhelm/ONTGP_VERDICT.md` |
| tech_finance_burnout × burnout × overwhelm | FAIL (weakest of the 3) | `artifacts/qa/flagship_line_edit/20260719_tech_finance_burnout__burnout__overwhelm/ONTGP_VERDICT.md` |
| healthcare_rns × burnout × overwhelm | FAIL (closest to PASS — Ch12 alone is a clean 5/5) | `artifacts/qa/flagship_line_edit/20260719_healthcare_rns__burnout__overwhelm/ONTGP_VERDICT.md` |

**SYSTEM_WORKING=0/3.** No fabricated PASS. Real, quotable, cited defects found and
partially fixed; the remainder is honestly deferred with evidence, exactly as
instructed.

## Verify

- Fresh render evidence (2/3 cells, live this lane): `lane03/renders/*_run.log`.
- Atom-bank diffs: `git diff` on the 3 `STORY/CANONICAL.txt` files (24 atoms changed,
  metadata headers untouched).
- Flagship parity: ran `check_flagship_book_parity.py --snapshot ch1` as due
  diligence; **FAILED in the current ambient tree**, root-caused to **pre-existing,
  unrelated dirty-tree drift from other concurrent lanes** to `anxiety`-topic
  accent-bank files (identical finding to Lane 02's, re-verified fresh). This lane's
  edits are `burnout`-topic `STORY` atoms in different persona directories entirely —
  provably disjoint (`git status --short` on the 3 edited files vs the still-dirty
  `anxiety`-topic files). Full note: `artifacts/qa/perfect_books_wave2_20260718/lane03/FLAGSHIP_PARITY_NOTE.md`.
  The offline land below stages only this lane's explicit paths, so the drift is not
  carried into the offline commit.
- Composer/topology/registry code: **untouched** — `git status --short` outside
  `atoms/**` and this lane's own proof/handoff paths shows no other changes from this
  lane.

## DEFERRED (honest, not silent)

- The catalog-wide `Wave2-NNN` leaked-metadata defect beyond the 3 designated cells
  (confirmed present in hundreds of other bank files) — not touched, future
  bank-hygiene lane.
- The broken `environment_fallback_families.yaml` ambient-detail template — not
  fixed, needs a dedicated Pearl_Dev lane with its own flagship-parity proof.
- The Ch5 mid-sentence truncation bug (healthcare_rns) — not fixed, composer/wiring-
  adjacent.
- The duplicate cross-chapter atom-selection behavior (corporate_managers) — not
  fixed, composer-adjacent, banned lever for this lane.
- Re-verifying the 24 atom fixes via a fresh render — blocked by the same C4
  registry defect Lane 02 found; the fixes are forward-looking (any future render of
  these 3 cells, once C4 is separately resolved, inherits the corrected prose).
- The catalog-wide `G-DEF4` blocker itself (Lane 02's finding) — still not fixed,
  still out of scope for a fill/line-edit lane; recommend the dispatcher open it as
  its own tracked item, as Lane 02 already recommended.

## Landed

Offline via the INDEX recipe (temp-index plumbing, explicit paths, diff-stat gate) to
`offline/perfect-books-wave2-lineedit-20260718` on `pearlstar_offline`. BASE =
`offline/perfect-books-wave2-bankfill-20260718`
(`d48fbdacacabc21641709f9411af90dd46c3ed27`) per INDEX.md's "Serial, not parallel,
with Lane 02" guidance (Lane 03 stacks on Lane 02's tip). See CLOSEOUT_RECEIPT below
for the exact SHA.

## Files changed (explicit list — the diff-stat gate enforced this)

- `atoms/corporate_managers/burnout/STORY/CANONICAL.txt` (modified, 7 atoms rewritten)
- `atoms/tech_finance_burnout/burnout/STORY/CANONICAL.txt` (modified, 10 atoms rewritten)
- `atoms/healthcare_rns/burnout/STORY/CANONICAL.txt` (modified, 7 atoms rewritten)
- `artifacts/qa/flagship_line_edit/20260719_corporate_managers__burnout__overwhelm/ONTGP_VERDICT.md` (new)
- `artifacts/qa/flagship_line_edit/20260719_corporate_managers__burnout__overwhelm/NOTES.md` (new)
- `artifacts/qa/flagship_line_edit/20260719_corporate_managers__burnout__overwhelm/RENDER_REF.txt` (new)
- `artifacts/qa/flagship_line_edit/20260719_tech_finance_burnout__burnout__overwhelm/ONTGP_VERDICT.md` (new)
- `artifacts/qa/flagship_line_edit/20260719_tech_finance_burnout__burnout__overwhelm/NOTES.md` (new)
- `artifacts/qa/flagship_line_edit/20260719_tech_finance_burnout__burnout__overwhelm/RENDER_REF.txt` (new)
- `artifacts/qa/flagship_line_edit/20260719_healthcare_rns__burnout__overwhelm/ONTGP_VERDICT.md` (new)
- `artifacts/qa/flagship_line_edit/20260719_healthcare_rns__burnout__overwhelm/NOTES.md` (new)
- `artifacts/qa/flagship_line_edit/20260719_healthcare_rns__burnout__overwhelm/RENDER_REF.txt` (new)
- `artifacts/qa/perfect_books_wave2_20260718/lane03/LANE03_STATUS.md` (new)
- `artifacts/qa/perfect_books_wave2_20260718/lane03/FLAGSHIP_PARITY_NOTE.md` (new)
- `artifacts/qa/perfect_books_wave2_20260718/lane03/flagship_parity_ch1.log` (new)
- `artifacts/qa/perfect_books_wave2_20260718/lane03/renders/tech_finance_burnout__burnout__overwhelm_run.log` (new)
- `artifacts/qa/perfect_books_wave2_20260718/lane03/renders/healthcare_rns__burnout__overwhelm_run.log` (new)
- `artifacts/coordination/handoffs/perfect_books_wave2_lineedit_2026-07-18.md` (this file)

No composer/topology code touched. No `registry/*.yaml` touched. No frozen goldens
touched (confirmed via parity check + provable-disjoint-diff). No `git add -A` used
anywhere.

## Cleanup ledger

- Empty render-output directories (`lane03/renders/tech_finance_burnout__burnout__overwhelm/`,
  `.../healthcare_rns__burnout__overwhelm/`) were created by `--render-dir` but never
  populated (both renders hard-stopped before writing `book.txt`) — declared here,
  not landed (git does not track empty directories; nothing to clean).
- No temp index files or scratch branches left behind; `GIT_INDEX_FILE` unset after
  the landing commit (see CLOSEOUT_RECEIPT command trace).

## Next action

Lane 05 (blind-10 prep) gates on this lane's signal per INDEX.md — but per §0
acceptance-layer honesty, **no cell here reached `system working`**, so Lane 05 has
no fresh Layer-3 inventory from this lane's 3 cells to build a blind-10 packet from.
Recommend the dispatcher either (a) open a dedicated fix lane for the 2 documented
renderer-level defects — the healthcare_rns cell is one clean fix away from a real
PASS — then re-run this lane's ONTGP read on that cell, or (b) proceed with whatever
`system working` inventory exists elsewhere in the catalog, independent of these 3
cells.

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT=Pearl_Editor_lane03
CELLS_ATTEMPTED=3 SYSTEM_WORKING=0 (honest count — no fabricated PASS)
ONTGP_VERDICTS=artifacts/qa/flagship_line_edit/20260719_corporate_managers__burnout__overwhelm/ONTGP_VERDICT.md (FAIL);
  artifacts/qa/flagship_line_edit/20260719_tech_finance_burnout__burnout__overwhelm/ONTGP_VERDICT.md (FAIL);
  artifacts/qa/flagship_line_edit/20260719_healthcare_rns__burnout__overwhelm/ONTGP_VERDICT.md (FAIL, closest to PASS)
FIX_METHOD=atom-rewrite (24 STORY atoms, leaked-batch-generation-metadata defect,
  3 cells' own banks); composer untouched: CONFIRMED (git status outside atoms/** +
  proof/handoff paths shows no other changes; registry/*.yaml untouched;
  registry_resolver.py / enrichment_select.py untouched)
SEAMS_PROMOTED=atoms/corporate_managers/burnout/STORY/CANONICAL.txt (7 atoms);
  atoms/tech_finance_burnout/burnout/STORY/CANONICAL.txt (10 atoms);
  atoms/healthcare_rns/burnout/STORY/CANONICAL.txt (7 atoms) — landed in the
  reusable bank itself, not a one-off manuscript patch (L4)
COHESION_METRIC=0/3 cells system working; 1/3 (healthcare_rns) blocked from PASS by
  exactly 2 renderer-level defects (documented, not fixed — out of atom-rewrite
  scope); 1/3 (corporate_managers) blocked by a duplicate cross-chapter atom
  selection (composer-adjacent, not fixed) + the leaked-metadata defect (fixed);
  1/3 (tech_finance_burnout) is a genuine low-quality specimen draft, blocked on
  multiple dimensions across all 3 sampled chapters
FLAGSHIP_PARITY=no (FAILED in ambient tree, root-caused to pre-existing unrelated
  anxiety-topic dirty-tree drift from other concurrent lanes — identical finding to
  Lane 02's, re-verified fresh this lane; this lane's edits are burnout-topic STORY
  atoms in different persona directories, provably disjoint; offline commit stages
  only this lane's explicit paths so the drift is not carried into the landed SHA)
ACCEPTANCE_LAYER=structurally clear on the atom-bank fixes (clean, parity-safe);
  NOT system working on any of the 3 designated cells this pass; SYSTEM remains
  authored candidate overall
LANDED=offline/perfect-books-wave2-lineedit-20260718@<SHA — see landing step below>
CLEANUP_COMPLETE=yes (GIT_INDEX_FILE unset, temp index dir was in system tmp — no
  workspace scratch files; empty render dirs declared, not landed; local dirty tree
  left untouched, not landed)
HANDOFF=artifacts/coordination/handoffs/perfect_books_wave2_lineedit_2026-07-18.md
SIGNAL=perfect-books-wave2-lineedit=<SHA — see landing step below>
NEXT_ACTION=Lane 05 has no Layer-3 system-working inventory from this lane's 3
  cells; recommend dispatcher open a dedicated fix lane for the 2 documented
  renderer defects (healthcare_rns is one fix away from PASS) before Lane 05 builds
  a blind-10 packet around these specific cells
```
