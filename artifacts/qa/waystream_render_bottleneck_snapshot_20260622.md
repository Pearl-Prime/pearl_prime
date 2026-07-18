# Waystream Render Bottleneck Snapshot

**Date stamp:** `20260622` (2026-06-22; repo YYYYMMDD convention)  
**Main SHA:** `e853dc227ed260d11ba558b874f4ee173cb86d95`  
**Parent spec:** [docs/specs/WAYSTREAM_EPUB_RENDER_OPTIMIZATION_V1_PLAN.md](../../docs/specs/WAYSTREAM_EPUB_RENDER_OPTIMIZATION_V1_PLAN.md)

---

## Rendered book counts

| Metric | Count |
|--------|------:|
| Dirs under `artifacts/rendered/waystream_batch/` | 66 |
| `book.txt` files | 61 |
| `job.json` files | 51 |
| Ready plans (`_needs_authoring: false`) | 800 |
| `batch_epub_state.json` ok | 778 |
| `batch_epub_state.json` pipeline_fail | 22 |
| Production `quality_profile` in rendered dirs | 19 |
| Debug `quality_profile` in rendered dirs | 45 |
| Register gate non-PASS in rendered dirs | 0 |

---

## Batch failure breakdown (22 pipeline_fail)

| Category | Count | Personas |
|----------|------:|----------|
| EXERCISE strict-canonical (SOLUTION-01) | 7 | entrepreneurs |
| `InsufficientVariantsError` (REFLECTION <3) | 14 | gen_alpha_students |
| Other atom/content gaps | 2 | first_responders |
| Other | 1 | healthcare_rns |

**Sample stderr (entrepreneurs):**

```
[PRODUCTION GATE] EXERCISE-BANK-RESOLUTION-01 strict-canonical: 24 EXERCISE slot(s)
resolved via practice_library fall-through.
```

**Sample stderr (gen_alpha_students):**

```
InsufficientVariantsError: atom inventory too thin: gen_alpha_students/anxiety/REFLECTION
has 1 variant(s), need >= 3 (SPEC-739-THRESHOLD-01).
```

---

## Sample job.json / quality_summary (3 books)

| book_id suffix | quality_profile | gates | outcome |
|----------------|-----------------|-------|---------|
| `corporate_managers__anxiety__comparison` | production | all PASS/WARN | EPUB ok; register PASS |
| `gen_alpha_students__overthinking__false_alarm` | debug | SKIPPED | hold: phrase density |
| `entrepreneurs__burnout__grief` | — | never reached | pipeline_fail pre-render |

---

## MANUSCRIPT_PASS_INVENTORY

Full-book or per-chapter scans in spine render path (`scripts/run_pipeline.py` `_run_spine_pipeline_mode`).

| # | Pass | Location | Full-book scan |
|---|------|----------|----------------|
| 1 | `clean_for_delivery` | run_pipeline:1081 | yes |
| 2 | `strengthen_rendered_spine_manuscript` | run_pipeline:1087 | per-chapter |
| 3 | `clean_for_delivery` | run_pipeline:1092 | yes |
| 4 | `strengthen_rendered_spine_manuscript` | run_pipeline:1097 | per-chapter |
| 5 | `dedupe_scene_furniture_book` | run_pipeline:1105 | yes |
| 6 | `_clamp_book_to_word_ceiling` | run_pipeline:1167 | yes |
| 7–13 | `ensure_chapter_flow_cues` (×7) | run_pipeline:1181–1329 | per-chapter + gate eval |
| 14 | `_reduce_scene_anchor_density` (≤4 iter) | run_pipeline:1198 | yes ×4 |
| 15 | `_scene_anchor_density_violations` | run_pipeline:1208 | yes (check) |
| 16 | `strengthen_register_craft_output` | run_pipeline:1249 | yes (10 sub-passes) |
| 17–35 | Repair loop: F7×8, F13×5, F4×5, F1×2, orphan×6, floor×2 | run_pipeline:1258–1333 | yes each |
| 36+ | Post-render gates (production) | run_pipeline:1372+ | yes ×8 gates |

**GATE_TIMING:**

| Gate | Pre-render strengthen | Post-render evaluate |
|------|----------------------|---------------------|
| F1, F4, F6, F7, F13 | yes (`register_output_strengthen`) | yes (`register_gate`) |
| F2, F3, F5, F11, F12 | no | yes |
| chapter_flow | yes (`ensure_chapter_flow_cues`) | yes |
| scene_anchor_density | yes (reducer + inline check) | report only |
| book_pass | no | yes |

---

## Workers default (verified on main)

```python
# scripts/release/batch_waystream_epubs.py:51
DEFAULT_WORKERS = min(8, os.cpu_count() or 4)
```

---

## PR #1850 anchor

Merge commit: `648f20d1cf4a113d94904cbd0c9bb55012f5282d` — register composer gate fixes (F1/F4/F6/F7/F13 strengthen loop). Do not re-author; restore from this SHA if drift.
