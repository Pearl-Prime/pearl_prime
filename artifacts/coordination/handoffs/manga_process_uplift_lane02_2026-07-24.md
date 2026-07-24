# Handoff — Manga Process Uplift Lane 02 (US illustrated format research)

**Date:** 2026-07-24 · **Agent:** Pearl_Research (Lane 02) · **Wave:** 1
**Signal:** `us-illustrated-format-research-merged=<SHA>` (see closeout)

## What landed

1. **`artifacts/research/us_illustrated_self_help_format_study_2026-07-24.md`** (NEW —
   `NEW-ARTIFACT-JUSTIFIED`, confirmed absent 2026-07-24): 17-title comp corpus,
   format-norm bands per sub-format class (A gift / B doodle-strip / C graphic-essay /
   D graphic-medicine / E illustrated-prose), Circana-via-PW category signal
   (self-help +14.7% 2025), per-pilot-cell recommendations with confidence,
   Q-MPU-03 serialized secondary section. Every load-bearing number cited with
   source + access date.
2. **`config/manga/us_illustrated_pilot_cells.yaml`**: per-cell `format_parameters`
   blocks (page/trim/color/art:text/words-page/price/binding/structure), each
   `provenance: RESEARCHED` + source anchor; registry-level
   `format_parameters_status: RESEARCHED` + `format_study` pointer;
   `schema_version` 1.0.0 → 1.1.0. Additive only — verified against consumer
   `scripts/ci/check_western_lane_format.py` (reads only brand_id/topic/
   series_plan_stub + registry lane/master_format/cell-count; all unchanged).
3. **`docs/US_CATALOG_PLAN.md`**: dated addendum (edit in place, no fork) pointing at
   the study; corrects the two-comp "Illustrated Prose Hybrid" sketch in §3.

## For Lane 06 (series master plan contract) — planning-contract implications (Q-MPU-03)

Flagged, not specced (per Lane 02 DO-NOT):

- The illustrated lane's **book frame** needs page-count + total-word-mass targets in
  the planning contract (micro/light word classes for 4 of 5 cells; medium ONLY for
  `cognitive_clarity`), not chapter/episode counts inherited from manga.
- The **serialized frame** for this lane should model *Instagram strip cadence feeding a
  112–144pp book collection* (strip = atom, collection = book), NOT webtoon episodes.
  No Western wellness serial comp was found in webtoon-episode shape (study §6).
- Structure conventions per class (study §2d) are contract-relevant: class A gift books
  have NO chapters (4–8 movements); forcing a chapter contract onto the
  `healing_ground` cell would violate the researched format.
- Only `healing_ground` is hardcover-first; only `cognitive_clarity` carries a real
  prose word mass (18–28k). Cross-cell rule in study §4.

## Known gaps / follow-ups

- **Untracked authority doc:** `artifacts/qa/US_ILLUSTRATED_SELF_HELP_PILOT_2026-07-08.md`
  is referenced as Authority by `us_illustrated_pilot_cells.yaml` and
  `western_cartoon_styles.yaml` on origin/main but exists only as an untracked local
  file on the shared checkout (recreated 2026-07-19 for D-4 closure, never committed).
  Out of Lane 02 scope; someone should land it or repoint the Authority lines.
- Study row 8 (Anxiety Is Really Strange) page count is LOW confidence (32 vs ~80pp
  source conflict); resolve via JKP catalog if it ever becomes load-bearing.
- Words-per-page and art-density bands are informed estimates (MED confidence) —
  upgrade path is physical/`Look Inside` page sampling on 3–4 corpus titles.
- Trim estimates marked "class (est.)" in study §1a could be firmed with publisher
  tip-sheets; the five sourced trims are sufficient for the §2e norm bands.

## Cleanup ledger

- Scratchpad working set `…/scratchpad/lane02/` + temp index `…/scratchpad/lane02.index`:
  session-scoped, auto-cleaned; nothing written into the shared working tree.
- Shared checkout untouched (plumbing pattern off `origin/main^{tree}` throughout;
  branch parked on `agent/bestseller-atom-flow-lanes-20260721` was never switched).
- Two superseded checkpoint commits (3b06e21d, 0ba2d1c7 — pre-#313-merge parents)
  abandoned unpushed after re-rooting onto 88573e23; final chain is 2 commits.
- No stranded branches: `agent/us-illustrated-format-research-20260724` deleted on
  merge (see closeout).
