# VERIFY-3 PROOF — HOOK-stub rebuild (Book #4: corporate_managers × burnout)

- **Date:** 2026-06-14
- **Branch:** `agent/gold-reference-7tier-redirect-20260530`
- **Goal:** Prove HOOK placeholder stubs are gone + spot-check cross-persona bleed, by rebuilding
  the one book that exhibits BOTH DEFECT 5 (24 HOOK stubs) and DEFECT 7 (12 foreign gen_z hook lines).
- **Baseline:** `artifacts/pearl_prime/pilot_10/04_corporate_managers__burnout/book.txt`
- **Rebuilt:** `artifacts/pearl_prime/fix_wave_rebuild_20260614/hook/book.txt`
- **Status: PARTIAL.** Cross-persona bleed (Lane C) and the truncation orphan are FIXED; the
  own-persona HOOK placeholder stub is NOT fixed (guard gap on a path the lane fix did not cover).

---

## Build provenance

Canonical spine CLI (Tier-1, NO paid LLM API — spine compose is local/template):

```
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic burnout --persona corporate_managers \
  --arc config/source_of_truth/master_arcs/corporate_managers__burnout__overwhelm__F006.yaml \
  --pipeline-mode spine --runtime-format standard_book \
  --chapter-architecture-version 2 --teacher ahjan --seed pilot_v1 \
  --quality-profile production --render-book \
  --render-dir <DIR> --out <DIR>/plan.json \
  --locale en-US --atoms-root atoms --atoms-model legacy \
  --exercise-journeys --enforce-scene-gate --no-job-check --no-generate-freebies
```

- **Arc choice:** `corporate_managers__burnout__overwhelm__F006.yaml`. The task header assumed a
  `__spiral__` arc, but **no `corporate_managers__burnout__spiral__F006.yaml` exists.** Ground truth
  for book #4's arc is `PILOT_10_REVIEW_PACKAGE.md:98` → `corporate_managers__burnout__overwhelm__F006.yaml`
  (engine=`overwhelm`, angle INVISIBLE_COST). plan.json/budget confirm angle_id=INVISIBLE_COST, 12 ch.
- **Exit code:** 1 — this is the EXPECTED word-budget overshoot signal (book IS built; see word_budget below),
  NOT a build failure. `book.txt` rendered (22,848 words, 12 chapters).

### Pre-build blocker fixed (git-first drift recovery — NOT a lane fix)

The first build attempt **hard-failed before render** at the tuple-viability gate with
`Tuple viability: NO_STORY_POOL` (no `book.txt`). Root cause: today's 14:39 auto-backup commit
`5445e27c7` (a 1,661-file mass mutation) corrupted atom headers across the atoms tree — it promoted
bare empty-atom lines (`RECOGNITION v02`) to `## RECOGNITION v02` headers **without** the required
`path:`/`BAND:` metadata, so `_parse_canonical_txt` raised `ValueError` and the STORY pool resolved
empty. This is the "546 corrupted atom-file headers" frontier in project memory, manifested as a
parse-breaking regression that landed AFTER the 09:08 pilot build.

- Pilot-era (08:36, `947b2c0cd`) `atoms/corporate_managers/burnout/overwhelm/CANONICAL.txt` parses
  cleanly → 28 atoms. HEAD raised → 0 atoms → NO_STORY_POOL.
- **Fix (scoped to one file):** restored that single atom file to its clean pilot-era blob via
  `git show 947b2c0cd:<path> > <path>` (blob write, not `git checkout` — main tree has a persistent
  index.lock; blob write sidesteps it and only touches the working tree the build reads). Verified
  28 atoms / VIABLE before re-build. The 1,661-file backup commit and the lane fixes were NOT touched.

### Lane-fix state (confirmed present on branch HEAD, committed — `git status` clean)

- DEFECT 5 HOOK placeholder guard: `phoenix_v4/rendering/chapter_composer.py:54-64`
  (`_PLACEHOLDER_BRACKET_RE` + `_is_placeholder_text`).
- DEFECT 4/7 cross-persona registry fix: `phoenix_v4/planning/enrichment_select.py:555-628`
  (persona-aware registry read) + `_REGISTRY_PLACEHOLDER_RE` (`:578-581`, applied at `:1499/:1529/:3000`).
- DEFECT 6 word bound: `_load_runtime_word_bounds('standard_book')` = **(9000, 22000)** (corrected ceiling).
- Both placeholder regexes were unit-checked against the literal stub
  `[Persona-specific hook for corporate_managers × burnout]` → both `.match()` = True. Guard logic is
  present and correct; the gap is **where** it is applied (see DEFECT 5 below).

---

## Defect matrix (BASELINE → REBUILT)

| # | Defect | Signature | Baseline | Rebuilt | Polarity | Result |
|---|--------|-----------|---------:|--------:|----------|--------|
| D5 | HOOK placeholder stub (ALL) | `[Persona-specific hook for` | 24 | 12 | drop→0 | PARTIAL (foreign half gone; own-persona half remains) |
| D5 | HOOK stub — own-persona | `[…corporate_managers × burnout]` | 12 | **12** | drop→0 | **NOT FIXED** |
| D7 | cross-persona bleed (foreign) | `[…gen_z_professionals × burnout]` | 12 | **0** | drop→0 | **FIXED** |
| D5 | TODO/TKTK/TBD/DRAFT | (case-insensitive) | 0 | 0* | drop | clean (*1 false hit = the word "drafting" in prose) |
| D7 | leaked atom-id label | `^(INTEGRATION|RECOGNITION|EMBODIMENT|TURNING_POINT|MECHANISM_PROOF) v\d+$` | 0 | **0** | →0 | clean (book #4 never had these; they live in 02/07/08) |
| D7 | leaked atom-id label (broad) | `^[A-Z_]+ v\d+$` | 0 | 0 | →0 | clean |
| D2 | truncation orphan (body-scan) | `sternum. still bracing.` | 16 | **0** | drop | **FIXED** |
| D2 | correct full form (success) | `sternum. That is the part still bracing` | 2 | **15** | appear | **FIXED** (orphans repaired into full sentences) |
| D2 | orphan tail (body-scan) | `to fix anything you find.` | 1 | 1 | drop | unchanged (1 legit embedded occurrence) |
| D1 | verbatim bridge | `What remains is the moment after the alarm fires` | 0 | 0 | drop | n/a (not present in book #4) |
| D1 | verbatim bridge | `What remains is the next ordinary moment` | 3 | 2 | drop | minor drop |
| D1 | data-bank success marker | `Ahead of you:` | 0 | 0 | appear | not reached (authored bank still bypassed) |

### Evidence snippets

- **D2 FIXED** — orphan repaired into full sentence:
  - baseline `:318` → `Start with the pressure under the sternum. still bracing.`
  - rebuilt  `:266` → `Start with the pressure under the sternum. That is the part still bracing.`
- **D7 FIXED** — foreign gen_z hook removed:
  - baseline `:10` → `[Persona-specific hook for gen_z_professionals × burnout]`
  - rebuilt  → (no match) — persona-aware registry fix dropped it.
- **D5 NOT FIXED** — own-persona stub still opens chapters:
  - rebuilt `:8` (Chapter 1, between title and body) → `[Persona-specific hook for corporate_managers × burnout]`

---

## Gate results

### Register gate (DEFECT 7 verify) — origin/main version (1269 lines), NOT the gutted branch copy (904 lines)

Both books re-scored with the **same** origin/main gate for a fair before/after
(`artifacts/pearl_prime/fix_wave_rebuild_20260614/_gate_mainver/phoenix_v4/quality/register_gate.py`).
Verdict HARD_FAIL iff any **F2** (severity HARD_FAIL); F7/F12/F13 are FAIL/WARN severity and do NOT
drive the verdict.

| Metric | Baseline (re-scored) | Rebuilt |
|--------|---------:|--------:|
| **verdict** | HARD_FAIL | **HARD_FAIL** |
| F2 (broken-slot, HARD_FAIL driver) | 27 | **20** |
| F1 | 56 | 61 |
| F4 (renderer artifact) | 3 | **1** |
| F7 | 12 | 12 |
| F13 (dwell starvation) | 5 | 7 |
| total findings | 106 | 104 |

- **Verdict unchanged (HARD_FAIL)** because F2 > 0 in both. But F2 dropped **27 → 20** and F4 **3 → 1**.
- **Zero leaked `^<TOKEN> v\d+$` lines** in the rebuilt book (success on that sub-criterion).
- The remaining 20 F2 are NOT the HOOK stubs (0 reference them) and NOT the DEFECT-2 sternum orphan
  (now 0). They are independent atom-prose seams: F2.B sentence-end-preposition ×10
  (e.g. "Here's a practice to work with."), F2.C lowercase-sentence-start ×9
  (mid-atom fragments), F2.D sub-4-word paragraph ×1.

### word_budget (DEFECT 6)

- Bound (branch) = **(9000, 22000)** — corrected ceiling confirmed.
- Gate word_count (`len(prose.split())`) = **22,848** > 22,000 → `book_pass_report.json` `failures: ['word_budget']`.
- Baseline (20,447) also failed word_budget. The rebuild is LARGER (removing the 12 foreign stubs +
  restoring 28 clean overwhelm STORY atoms produced more real prose), so it overshoots the ceiling by 848.
- **word_budget did NOT pass for this book** — it is a genuine overshoot (the exit-1 condition).

### book_pass / §9 gates (production build, automatic)

- Rebuilt `book_pass_report.json`: `status` fail, `failures: ['word_budget']` — the SOLE §9 failure
  (band_distribution, identity_stages, callback_completion, angle_journey_coherence,
  min_bestseller_structures_distinct all PASS). Same single-failure profile as baseline.

### scene gate

- Ran in-build via `--enforce-scene-gate` (production/blocking). Build proceeded to render → scene gate passed.

---

## Root-cause note for the unfixed DEFECT 5 (own-persona HOOK stub)

The HOOK atom source `atoms/corporate_managers/burnout/HOOK/CANONICAL.txt` ships the literal stub
`[Persona-specific hook for corporate_managers × burnout]` as the atom BODY for HOOK v02–v30
(only v01 has real prose: "Elena is at her kitchen table…"). The lane fix added placeholder
rejection on (a) the registry read path and (b) the composer slot-assembly — which is why the
**registry-sourced foreign gen_z bleed dropped to 0**. But the **own-persona** HOOK opening is
selected by `_try_persona_content` (`phoenix_v4/planning/enrichment_select.py:758-776`), which filters
atoms only by `atom_passes_book_governance` (metadata) and **returns `atom["content"]` with no
`_is_placeholder_text` / `_REGISTRY_PLACEHOLDER_RE` check** (`:772-776`). Its result feeds the spine
render outside `compose_chapter_prose`'s `:2421` HOOK guard, so the 6-word bracket survives.

**Remaining fix to close DEFECT 5 (Pearl_Dev):** add a placeholder-content reject in
`_try_persona_content` (skip pool atoms whose `content` matches `_REGISTRY_PLACEHOLDER_RE`, fall
through to the next variant / scene), OR have Pearl_Editor author real HOOK v02+ prose for
corporate_managers/burnout. Either kills the 12 own-persona stubs.
