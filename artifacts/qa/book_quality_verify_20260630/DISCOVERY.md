# Discovery Report — Assembled-Book Quality Verification

**Date:** 2026-06-30 · **Agent:** Pearl_Research + Pearl_Editor · **Mode:** GPU-free, read-only on books

## Book set inventoried

| Source | Count | Notes |
|--------|------:|-------|
| `artifacts/wave_proof/draft/` | 8 | Full 12-chapter spine renders; **clean** (no HOOK placeholder stubs); EI v2 reports on disk |
| `artifacts/pearl_prime/pilot_10/` (#3605) | 9 | Full spine; **3 blocked** on HOOK atom placeholder leakage |
| `artifacts/epub/` | 13 | Teacher-mode micro-EPUBs (~5–6k words, single chapter) |
| `artifacts/epubs/way_stream_sanctuary/` | 1 | Register-PASS canonical (`corporate_managers × burnout`) |
| `artifacts/wave_proof/epubs/` | 8 | EPUB mirrors of draft set (deduped — draft prose used for scoring) |

**Total verified:** 31 assembled artifacts → **24 distinct persona×topic cells** after deduping EPUB mirrors.

**Gap-fill assembly:** Not required. Coverage spans 8 personas × 6 topics on full spine; teacher set adds 10 teachers × 7 topics. High-volume cells (`corporate_managers × burnout`, `gen_z_professionals × anxiety/burnout`) are covered.

## EI v2 dimension → operator dimension mapping

| Operator ask | EI v2 dimensions | Rollup rule | Pass bar |
|--------------|------------------|-------------|----------|
| **Bestseller** | `marketability` + `content_uniqueness` + composite | mean of three | ≥ 0.5 (`llm_cohesive_bestseller_tester.py` `EI_V2_DIMENSION_THRESHOLD`) |
| **Cohesive flow** | `cohesion` + `chapter_journey` + `emotional_coherence` | mean of three | ≥ 0.5 deterministic; **Tier-1 read may override to CONCERN** |
| **Engaging** | `engagement` + `listen_experience` | mean of two | ≥ 0.5 |
| **Marketing-fit** | `marketability` + `marketing_lexicons` token overlap + listing promise check | mean(marketability, lexicon) + subtitle keyword match vs `en_US_catalog.csv` | ≥ 0.5 + delivers-promise YES/PARTIAL |

**Rubric source:** `scripts/ci/llm_cohesive_bestseller_tester.py` lines 39–45 (`EI_V2_DIMENSIONS`, `EI_V2_DIMENSION_THRESHOLD = 0.5`). Scoring engine: `scripts/ci/run_ei_v2_rigorous_eval.py::evaluate_chapter` (same heuristics as pipeline render gate). **No Ollama / no GPU invoked.**

## Prior art reused

- Plan-scale repetition census: `artifacts/qa/plan_scale_qa_sweep_20260630/REPETITION_CENSUS.json` — universal MEDIUM thesis repetition, 128-cell engine-keyed reuse confirmed.
- Pilot #3605 placeholder diagnosis: `artifacts/pearl_prime/pilot_10/PILOT_10_REVIEW_PACKAGE.md` §10.
- Leakage: `phoenix_v4.rendering.book_renderer.clean_for_delivery` + `delivery_contract_gate`.

## Listing SSOT

`artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv` — title, subtitle, topic, persona per cell. Teacher-mode EPUBs have no catalog row (teacher_id in filename, not persona).
