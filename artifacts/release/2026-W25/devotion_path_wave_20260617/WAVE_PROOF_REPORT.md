# devotion_path assembly wave — DRAFT proof (2026-06-17)

**Agent:** Pearl_Prime · **Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 · **Profile:** draft · **Mode:** `run_pipeline --pipeline-mode spine`
**Base:** clean origin/main (29c3fd76bc) + this PR's re-pointed devotion catalog. **No paid API. No covers (FLUX/PIL lane out of scope).**

## Wave design
8 cells = anchor persona `corporate_managers` × every re-pointed legal engine across the 3 topics
(burnout: overwhelm/watcher/grief · courage: false_alarm/spiral/shame · imposter_syndrome: shame/comparison).
This exercises all 8 legal engine slots the re-point introduces.

## Result — 3/8 assembled; 5/8 blocked by atom-coverage (out of scope)

| cell | built | words | flow | craft ONTGP | scene-density | book-pass | Pearl Prime gate |
|---|---|--:|---|--:|---|---|---|
| burnout / overwhelm | yes | 17910 | PASS | 0.51 | **FAIL** | PASS | **Hold** |
| burnout / watcher | yes | 18784 | FAIL | 0.50 | **FAIL** | PASS | **Reject** |
| burnout / grief | yes | 18982 | PASS | 0.51 | **FAIL** | PASS | **Hold** |
| courage / false_alarm | **NO** | — | — | — | — | — | EnrichmentGapError: TEACHER_DOCTRINE |
| courage / spiral | **NO** | — | — | — | — | — | EnrichmentGapError: TEACHER_DOCTRINE |
| courage / shame | **NO** | — | — | — | — | — | EnrichmentGapError: TEACHER_DOCTRINE |
| imposter_syndrome / shame | **NO** | — | — | — | — | — | EnrichmentGapError: TEACHER_DOCTRINE |
| imposter_syndrome / comparison | **NO** | — | — | — | — | — | EnrichmentGapError: TEACHER_DOCTRINE |

**Assembled: 3/8 (37.5%).** All 3 assembled books rendered full-length standard_books (~18k words)
with naming-engine titles (When Everything Is Too Much / Stepping Back from the Storm / The Weight You
Carry) + persona-named subtitles, and valid EPUBs (spine_length 3, only validator error = missing cover).

## Gate pass-rate (of the 3 that assembled)
- **Chapter flow:** 2/3 PASS · **Craft (ONTGP advisory):** 3/3 PASS (~0.50) · **Book-pass:** 3/3 PASS
- **Scene-anchor-density:** 0/3 PASS (all FAIL) → the **F-COHERENCE SCENE-atom scaffolding-repetition defect**
- **Overall Pearl Prime quality gate:** 0/3 ship-clean (2 Hold, 1 Reject)

## Why this is the EXPECTED gated outcome (not a defect of the re-point)
The re-pointed plans are structurally correct (engine-legal, arc-backed, naming-engine titles). The
two blockers are entirely in lanes this assembly is **gated behind** per
`DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md` §6/§8:
1. **F-COHERENCE (#1589/#1590/#1601):** SCENE atoms still contain mid-sentence injection artifacts
   (visible garbled SCENE prose) → scene-anchor-density FAIL on every book. Composer/atom lane (Pearl_Dev).
2. **Atom-coverage gap (TEACHER_DOCTRINE):** courage + imposter pools lack TEACHER_DOCTRINE slot content
   for these cells ("TEACHER_DOCTRINE ahjan-only") → hard EnrichmentGapError. Atom-bank lane.

Both are out of Pearl_Prime catalog_planning scope. Production assembly remains correctly GATED.

## Assembly backlog (to reach a shippable wave)
1. Land F-COHERENCE SCENE-atom repair (#1590) → clears scene-anchor-density.
2. Author TEACHER_DOCTRINE atoms for courage + imposter_syndrome (per persona) → unblocks 5/8 cells.
3. Decide B2 release-profile emission contract for a production (not draft) run.
4. Add covers (FLUX imagery + PIL text overlay) for KDP-valid EPUBs.
