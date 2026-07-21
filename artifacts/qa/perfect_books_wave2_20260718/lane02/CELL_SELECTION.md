# Lane 02 (Pearl_Editor) — Cell Selection (Q-W2-CELLS-01)

**Date:** 2026-07-18 (run 2026-07-19 local)
**Agent:** Pearl_Editor lane 02
**Acceptance layer honesty:** authored candidate ceiling only — no `system working` claim here (that is Lane 03's ONTGP job).

## Cells filled (3, all topic=`burnout`, engine=`overwhelm`, format=`F006`)

| # | Cell | MATRIX ref | Rationale |
|---|------|-----------|-----------|
| 1 | `corporate_managers × burnout × overwhelm` | `C048__corporate_managers__burnout__overwhelm` | Q-W2-CELLS-01 default; "#1923-proven shipping cell" |
| 2 | `tech_finance_burnout × burnout × overwhelm` | closest prior art: `C009__tech_finance_burnout__burnout__na` (persona has burnout topic + STORY pool on disk; `overwhelm` is the production-shape engine per `config/topic_engine_bindings.yaml`, `na` is not a bound engine) | Distinct persona; already has a well-stocked EXERCISE/STORY pool; shares `burnout` topic with cell 1 so the C3 accent-bank fill benefits both cells at once (topic-keyed banks, not persona-keyed) |
| 3 | `healthcare_rns × burnout × overwhelm` | closest prior art: `C002__healthcare_rns__burnout__na` (same engine-binding note as above) | Distinct persona (healthcare, not corporate/tech); same topic-keyed C3 benefit; healthcare_rns is also under-represented in the corpus (1 row) so filling it is diversity-positive |

All three avoid `gen_z_professionals × anxiety` (frozen golden, PROVEN-AT-BAR — explicitly excluded per dispatcher instructions).

## Why `topic=burnout` for all 3 (not 3 different topics)

`MATRIX.tsv` / `ANALYSIS_REPORT.md` show `corporate_managers` dominates the on-disk
corpus for `burnout`; picking 2 more **distinct-persona** cells on the **same topic**
lets one focused C3 accent-bank fill pass (`WISDOM_ESSENCE`, `AUTHOR_COMMENTARY` for
topic=`burnout`) serve all 3 cells at once — topic-keyed banks
(`EXTERNAL_STORY`/`CITED_EVIDENCE`/`WISDOM_ESSENCE`/`AUTHOR_COMMENTARY`, see
`phoenix_v4/planning/accent_planner.py::_build_pools_with_provenance`) are **not**
persona-keyed. This is the "mirror known-good pools, fill in place" instruction taken
literally: one topic, three personas, shared fill.

## `--engine na` vs `--engine overwhelm`

`config/topic_engine_bindings.yaml` binds `burnout` to `allowed_engines: [overwhelm,
watcher, grief, comparison]`; `na` is not a bound engine and fails tuple viability
(`NO_BINDING`, `NO_ARC`, `NO_STORY_POOL` — verified). `overwhelm` is the engine used by
the MATRIX SSOT's own cell 1 pick (`C048`) and is tuple-viable for all 3 personas
(see `tuple_viability_3cells.txt`), so all 3 cells use `overwhelm` for apples-to-apples
comparison and because arc files exist for that exact combination for all 3 personas
(`config/source_of_truth/master_arcs/{persona}__burnout__overwhelm__F006.yaml`).
