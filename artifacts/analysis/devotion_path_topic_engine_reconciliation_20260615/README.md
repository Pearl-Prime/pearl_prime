# devotion_path — topic × engine × arc coverage matrix (evidence base)

**Date:** 2026-06-15 · **Agent:** Pearl_Architect · **Purpose:** evidence base for the
topic×engine reconciliation decision (see
`docs/specs/DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC.md`).

This directory is the *forensic substrate* for the architecture call on the stood-down
devotion_path (Open Vessel Press / Sai Maa) en_US catalog. It is generated, not authored —
re-derivable from repo state at `origin/main` 863f7a65b.

## What the matrix proves

The 99 devotion_path book plans (`config/source_of_truth/book_plans_en_us/devotion_path__*.yaml`)
are `<11 personas> × {burnout, courage, imposter_syndrome} × {false_alarm, overwhelm, spiral}`.
The third axis — labeled "arc" in the plan filenames — is **the anxiety-family ENGINE triad
cross-applied to all three topics**. This violates the canonical rule in
`specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4`: *"Each topic has one engine"*, enforced by the
hard gate `config/topic_engine_bindings.yaml`.

### Engine-binding legality of the 99 catalog plans

| Verdict | Count | Meaning |
|---|---|---|
| `BUILDABLE_LEGAL` | **31** | arc exists **and** engine is binding-`allowed` for the topic → ship-eligible (still subject to the composer-coherence + production-gate fixes, see spec §6) |
| `BUILDS_BUT_ENGINE_ILLEGAL` | **5** | arc file exists but engine is in the topic's `forbidden_engines` (all 5 are `gen_z_student` F006 seed arcs) → EXCLUDE; building them violates engine-purity canon |
| `MISSING_ARC_ENGINE_LEGAL` | **2** | no arc, but the engine is binding-`allowed` (both `gen_z_student` courage cells) → author topic-native, stays legal |
| `MISSING_ARC_ENGINE_ILLEGAL` | **61** | no arc **and** the catalog engine is `forbidden` for the topic → do NOT author (would be illegal arcs); re-point the plan to a topic-native engine instead |
| **TOTAL** | **99** | |

Row-level detail: `catalog_plan_verdicts.tsv`.

### The decisive finding the stand-down handoff missed

The handoff reported "30/99 buildable" and framed Option (a) (re-scope to native engines) as a
*shrink* (99→~30). The matrix shows the opposite: **topic-native, engine-legal, arc-backed,
atom-backed capacity already authored = 85 cells.** The catalog simply points 68 of its 99 plans
at the wrong (anxiety-triad) engines instead of the topic-native engines that already have arcs.

| Topic | Binding-allowed engines (authored, atom-backed) | Native buildable cells |
|---|---|---|
| `burnout` | `overwhelm` (11/11), `watcher` (11/11), `grief` (11/11) | **33** |
| `courage` | `false_alarm` (10/11), `spiral` (10/11), `shame` (10/11) | **30** |
| `imposter_syndrome` | `shame` (11/11), `comparison` (11/11) | **22** |
| **TOTAL native capacity** | | **85** |

Per-cell detail: `topic_engine_coverage_matrix.tsv` (`native_buildable_cells` column).

(`gen_z_student` is the 11th persona; its courage native column is 10/11 because that persona's
courage arcs were authored as F003 seeds, not F006 — 1 cell short per courage engine.)

### Why Option (b) as literally framed is architecturally illegal

Of the 63 missing-arc plans, **61 sit on engines that the topic's `forbidden_engines` list bans**
(courage→overwhelm; burnout→{false_alarm, spiral}; imposter_syndrome→{false_alarm, overwhelm,
spiral}). Authoring those 61 arcs to "preserve the full 99 on the current engines" would manufacture
engine-illegal arcs and entrench the exact canon violation that caused the stand-down. Only **2** of
the 63 missing arcs (the `gen_z_student` courage cells) are on legal engines and worth authoring.

### Two orthogonal failures — do not conflate

1. **Engine-legality / arc-existence** (THIS matrix): the catalog points at forbidden engines and 63
   arcs are missing. Fixed by re-pointing plans (catalog_planning) — no prose work.
2. **Composer / atom-routing coherence** (NOT this matrix; separate lane #1589/#1590): even a
   binding-*legal* plan such as `corporate_managers__courage__false_alarm` (arc exists, engine
   allowed) rendered as anxiety prose with "courage" string-substituted, because the composer pulls
   `engine: false_alarm` atoms by engine key regardless of `topic: courage`. The arc YAML is
   correctly tagged (`topic: courage`, `engine: false_alarm`); the defect is downstream in atom
   selection. Re-pointing engines does NOT by itself fix this; it is a gating prerequisite tracked
   under the composer-frontier lane.

## Files

| File | Contents |
|---|---|
| `catalog_plan_verdicts.tsv` | 99 rows — per-plan persona/topic/catalog_engine/engine_binding_status/arc_exists/atom_dir/verdict |
| `topic_engine_coverage_matrix.tsv` | 21 rows — topic × engine grid with binding_status, personas-with-arc, atom-dirs, native_buildable_cells |
| `README.md` | this file |

## Inputs (re-derivation)

- Plans: `config/source_of_truth/book_plans_en_us/devotion_path__*.yaml` (99)
- Arcs: `config/source_of_truth/master_arcs/*.yaml` (530 total; keyed `<persona>__<topic>__<engine>__<format>`)
- Binding authority: `config/topic_engine_bindings.yaml` (`allowed_engines` / `forbidden_engines` per topic)
- Atoms: `atoms/<persona>/<topic>/`
- Canon: `specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md §4`

## Stand-down handoff (source)

`artifacts/release/2026-W25/devotion_path/HANDOFF_devotion_path_catalog_readiness_20260615.md`
+ `artifacts/release/2026-W25/devotion_path/READINESS_MANIFEST.tsv`
