# Composer Cohesion Restore — finishing the de-injection to the pre-injector floor

**Author:** Pearl_Prime (git-first drift-recovery, composer-cohesion lane)
**Date:** 2026-07-03
**Grounds on:** `docs/BESTSELLER_QUALITY_ARCHAEOLOGY_2026-07-03.md` (#4590)
**Bar:** the pre-injector **0–5% beat-line band** AND a book that **reads cohesive** —
NOT an F14 PASS at 22% (that is gate-passing, the archaeology's explicit warning).

---

## TL;DR

The #4590 archaeology proved the restore was incomplete: current `main` still renders
~32% beat-lines (byte-identical to the `365fd19cc3` injector era), and the g1-residual
branch only reached 22% — still ~5–8× the pre-injector 0–5% floor. This change **finishes
the de-injection** and returns the composer floor to the pre-injector band.

Residual 22% decomposed (real-cell breakdown, `scratchpad/beatline_source.py`):

| Source | share of residual beat-lines | fix |
|---|---|---|
| within-slot bridges (OPD-109) rendered as standalone paragraphs | ~55% | **fold** into the neighbor narrative paragraph |
| formulaic practice-intros ("Now we're going to do a X practice.") | ~15% | **fold** into the exercise they introduce |
| bare Title-Case section titles counted as body | ~12% | **mark** as real `##` headings |
| genuine short atoms stamped standalone | ~17% | the honest clean-anthology floor (line-edit lane for flagships) |

The fix is the **gate-sanctioned** F14 remediation — `register_gate._route_suggested_lanes`
routes F14 to *"stop emitting standalone one-line beats between atoms; **fold them into
neighbor paragraphs**."* It restores the pre-injector composer's "atoms woven into flowing
paragraphs" behavior instead of one-atom-per-paragraph line-stacking. Deterministic, no LLM,
**no gate threshold touched**.

---

## What landed (all in `phoenix_v4/rendering/register_output_strengthen.py`, wired into the spine render path)

1. **Deprescribe kill-switch** (g1-residual) — `spine_deprescribe_inject_enabled()` (default
   OFF): surplus F7 prescribed-action paragraphs are **dropped**, not replaced with standalone
   one-line comfort filler. `PHOENIX_SPINE_DEPRESCRIBE=1` re-enables the legacy injector.
2. **Adjacent-inject de-stack** (g1-residual) — `destack_adjacent_inject_paragraphs()`
   (default ON, `PHOENIX_INJECT_DESTACK=0` off).
3. **Standalone-inject FOLD** (Phase-2) — `fold_standalone_inject_paragraphs()` (default ON,
   `PHOENIX_INJECT_FOLD=0` off): weaves each surviving standalone bridge / practice-intro
   FORWARD into the narrative paragraph it introduces (BACKWARD if none follows), collapses
   consecutive injects, and marks bare Title-Case section titles `##`
   (`PHOENIX_SECTION_HEADING_MARK=0` off).
4. **Post-fold F7 re-cap** — folding a practice-intro into its exercise can tip that paragraph
   into F7 prescribed-action classification, so `_final_cap_f7` runs once more AFTER the fold
   (drop-mode on spine — **never re-inject filler**). Keeps the F7 per-chapter invariant.

---

## PROOF — same cell, same seed, injector-era kill-switches vs. this branch's defaults

Scored with the **real** `register_gate` F14 calc (`scratchpad/f14_score.py`), full register
verdict on the rendered book. Baseline = `PHOENIX_SPINE_DEPRESCRIBE=1 PHOENIX_INJECT_DESTACK=0
PHOENIX_INJECT_FOLD=0 PHOENIX_SECTION_HEADING_MARK=0` (reproduces the injector era in-place).

| Cell (topic × persona × engine) | BASELINE (injector-era) | FIX (this branch) |
|---|---|---|
| burnout × gen_z_professionals × watcher | 35.2% (199/565) **HARD_FAIL** F14 | **5.9%** (17/289) WARN |
| burnout × gen_z_professionals × overwhelm | 34.6% (176/509) **HARD_FAIL** F14 | **4.5%** (12/269) WARN |
| burnout × healthcare_rns × watcher | 34.4% (190/553) **HARD_FAIL** F14 | **4.7%** (13/275) WARN |
| burnout × entrepreneurs × overwhelm | 37.1% (241/649) **HARD_FAIL** F14 | **7.5%** (25/332) WARN |

Reference band (from #4590, recomputed by the same gate): pre-injector renders `qa_book_6h`
= **4.0%**, `anxiety_baseline` / `adi_da_self_worth` = **0.0%**; hand-seam FINAL = **2.8%**.

3/4 cells land in the pre-injector 0–5% band; `entrepreneurs` at 7.5% is the **honest content
frontier** (more genuine short atoms, NOT bridges) — routed to the flagship line-edit lane, NOT
papered over with filler. Every cell drops from ~35% HARD_FAIL to WARN (F14 passes), and **no
cell regressed to an F7/HARD_FAIL** — the post-fold re-cap holds.

### Chapter-1 read (burnout × gen_z_professionals × watcher, FIX) — reads cohesive

Bridges are now woven into flowing paragraphs; the section title is a real heading:

> ## This Is Not Tiredness
>
> You closed Slack at 11:47 PM and the closing did not register as relief. The unread count
> dropped to zero and your chest did not…
>
> The mechanism behind this pattern is small and stubborn. You are not less than you were; you
> are measuring an empty tank against a full one.
>
> Rest at this stop. You do not have to march past it. Sit with where that comparison is
> unfair. The person you are remembering was running on full reserves…

Compare the injector-era render of the same beat (stacked standalone one-liners):

> The mechanism behind this pattern is small and stubborn.
>
> Quiet the explanation. Watch the small switch flip.
>
> Some of your tiredness is the watching, not the doing.

---

## Honest frontier (the archaeology's core warning, upheld)

- **No gate lever re-tuned.** F4 closing-pool / F6 pre-gate / F2.D split-count / the F13-dwell
  proxy are untouched. F14 thresholds untouched. The fix removes the beat-emitting paths; the
  gate is unchanged.
- **F7 was NOT masked-then-exposed here** — it was briefly *created* by the fold (practice-intro
  merged into an exercise) and resolved by the post-fold re-cap in drop-mode. Filler was never
  re-added.
- **The residual ~4–7% is genuine short atoms**, the clean-anthology floor. A de-injected stitch
  composer reaches clean-anthology cohesion; hand-seam register (2.8%) still requires the
  per-chapter line-edit lane (`project_bestseller_prose_ceiling`). Catalog scale ≠ hand-seam;
  pick flagships.

## Reproduce

```bash
# score any book by the real gate
PYTHONPATH=. python3 scratchpad/f14_score.py <book.txt>
# A/B a cell (baseline kill-switches vs. defaults)
# CI-ALLOWLIST: legacy-registry-ok — docs reproduce snippet (injector-era A/B demo), not an executed bestseller build; the chord flags ARE present on the continuation lines below
PHOENIX_SPINE_DEPRESCRIBE=1 PHOENIX_INJECT_DESTACK=0 PHOENIX_INJECT_FOLD=0 \
PHOENIX_SECTION_HEADING_MARK=0 python3 scripts/run_pipeline.py \
  --topic burnout --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__burnout__watcher__F006.yaml \
  --pipeline-mode spine --quality-profile production --exercise-journeys \
  --no-job-check --skip-quality-gates --render-book --render-dir /tmp/baseline
```
