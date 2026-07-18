# Duration matrix pilot — RESULTS_V2 (wc metrics + baseline diff)

- **Persona:** `gen_z_professionals`
- **Topics:** grief (trauma arc), anxiety, somatic_healing (somatic arc)
- **Formats:** `micro_book_15`, `micro_book_20`, `short_book_30`, `standard_book`, `extended_book_2h`, `deep_book_4h`, `deep_book_6h`
- **Pipeline:** spine, `--quality-profile draft`, `--render-book`
- **Git:** metrics captured against `main` @ **79045e2ca1** (see `results.json` → `git_main_at_capture`)
- **Word count:** **`wc -w` on `book.txt`** (machine source of truth for this document)
- **Machine-readable:** `artifacts/pilots/duration_matrix/results.json`

## A. Full 21-cell table

| Topic | Tier (runtime) | Target words (min–max) | Actual words (`wc -w`) | % of min | Sections (≥50% / total) | Injection gaps | Chapter flow |
|---|---|---:|---:|---:|---|---:|---|
| grief | micro (~15m) (`micro_book_15`) | 2500–3000 | 4135 | 165.4% | 37/49 | 0 | FAIL (2/12) |
| grief | short (~20m) (`micro_book_20`) | 3000–4000 | 4157 | 138.6% | 37/49 | 0 | FAIL (2/12) |
| grief | standard (~30m) (`short_book_30`) | 4500–5500 | 8009 | 178.0% | 38/78 | 0 | FAIL (1/12) |
| grief | extended (~1h) (`standard_book`) | 9000–11000 | 12160 | 135.1% | 80/142 | 0 | PASS (0/12) |
| grief | deep (~2h) (`extended_book_2h`) | 18000–22000 | 22361 | 124.2% | 108/157 | 0 | PASS (0/12) |
| grief | immersive (~4h) (`deep_book_4h`) | 36000–44000 | 31492 | 87.5% | 65/157 | 0 | PASS (0/12) |
| grief | full (~6h) (`deep_book_6h`) | 52000–58000 | 39902 | 76.7% | 62/157 | 0 | PASS (0/12) |
| anxiety | micro (~15m) (`micro_book_15`) | 2500–3000 | 3583 | 143.3% | 39/51 | 0 | PASS (0/12) |
| anxiety | short (~20m) (`micro_book_20`) | 3000–4000 | 7231 | 241.0% | 55/88 | 0 | PASS (0/12) |
| anxiety | standard (~30m) (`short_book_30`) | 4500–5500 | 9098 | 202.2% | 43/88 | 0 | PASS (0/12) |
| anxiety | extended (~1h) (`standard_book`) | 9000–11000 | 13632 | 151.5% | 106/155 | 0 | PASS (0/12) |
| anxiety | deep (~2h) (`extended_book_2h`) | 18000–22000 | 24426 | 135.7% | 86/169 | 0 | PASS (0/12) |
| anxiety | immersive (~4h) (`deep_book_4h`) | 36000–44000 | 35692 | 99.1% | 79/169 | 0 | PASS (0/12) |
| anxiety | full (~6h) (`deep_book_6h`) | 52000–58000 | 42080 | 80.9% | 65/169 | 0 | PASS (0/12) |
| somatic_healing | micro (~15m) (`micro_book_15`) | 2500–3000 | 6102 | 244.1% | 26/67 | 0 | PASS (0/12) |
| somatic_healing | short (~20m) (`micro_book_20`) | 3000–4000 | 7034 | 234.5% | 23/67 | 0 | PASS (0/12) |
| somatic_healing | standard (~30m) (`short_book_30`) | 4500–5500 | 8065 | 179.2% | 20/67 | 0 | PASS (0/12) |
| somatic_healing | extended (~1h) (`standard_book`) | 9000–11000 | 12883 | 143.1% | 69/156 | 0 | PASS (0/12) |
| somatic_healing | deep (~2h) (`extended_book_2h`) | 18000–22000 | 18754 | 104.2% | 84/156 | 0 | PASS (0/12) |
| somatic_healing | immersive (~4h) (`deep_book_4h`) | 36000–44000 | 24209 | 67.2% | 61/156 | 0 | PASS (0/12) |
| somatic_healing | full (~6h) (`deep_book_6h`) | 52000–58000 | 26655 | 51.3% | 39/156 | 0 | PASS (0/12) |

## B. Before / after (baseline vs this matrix)

Baseline word counts are reproduced from the **pre-fix** duration matrix (`artifacts/pilots/duration_matrix/RESULTS.md` history, pilot-reported counts; for this corpus they align with `wc -w` within rounding). Baseline chapter flow was **FAIL** for **all 21** cells (handoff: **12/12** chapters failing per cell).

| Topic | Format | Baseline wc | New wc | Delta | Baseline gate | New gate |
|---|---|---:|---:|---:|---|---|
| grief | micro_book_15 | 3330 | 4135 | +805 | FAIL (12/12) | FAIL (2/12) |
| grief | micro_book_20 | 3330 | 4157 | +827 | FAIL (12/12) | FAIL (2/12) |
| grief | short_book_30 | 4428 | 8009 | +3581 | FAIL (12/12) | FAIL (1/12) |
| grief | standard_book | 8353 | 12160 | +3807 | FAIL (12/12) | PASS (0/12) |
| grief | extended_book_2h | 10749 | 22361 | +11612 | FAIL (12/12) | PASS (0/12) |
| grief | deep_book_4h | 10749 | 31492 | +20743 | FAIL (12/12) | PASS (0/12) |
| grief | deep_book_6h | 10749 | 39902 | +29153 | FAIL (12/12) | PASS (0/12) |
| anxiety | micro_book_15 | 2779 | 3583 | +804 | FAIL (12/12) | PASS (0/12) |
| anxiety | micro_book_20 | 3501 | 7231 | +3730 | FAIL (12/12) | PASS (0/12) |
| anxiety | short_book_30 | 4771 | 9098 | +4327 | FAIL (12/12) | PASS (0/12) |
| anxiety | standard_book | 8344 | 13632 | +5288 | FAIL (12/12) | PASS (0/12) |
| anxiety | extended_book_2h | 11563 | 24426 | +12863 | FAIL (12/12) | PASS (0/12) |
| anxiety | deep_book_4h | 11563 | 35692 | +24129 | FAIL (12/12) | PASS (0/12) |
| anxiety | deep_book_6h | 11563 | 42080 | +30517 | FAIL (12/12) | PASS (0/12) |
| somatic_healing | micro_book_15 | 2262 | 6102 | +3840 | FAIL (12/12) | PASS (0/12) |
| somatic_healing | micro_book_20 | 2992 | 7034 | +4042 | FAIL (12/12) | PASS (0/12) |
| somatic_healing | short_book_30 | 4003 | 8065 | +4062 | FAIL (12/12) | PASS (0/12) |
| somatic_healing | standard_book | 5781 | 12883 | +7102 | FAIL (12/12) | PASS (0/12) |
| somatic_healing | extended_book_2h | 6884 | 18754 | +11870 | FAIL (12/12) | PASS (0/12) |
| somatic_healing | deep_book_4h | 6884 | 24209 | +17325 | FAIL (12/12) | PASS (0/12) |
| somatic_healing | deep_book_6h | 6884 | 26655 | +19771 | FAIL (12/12) | PASS (0/12) |

## C. Blocker status checklist

| # | Criterion | Status |
|---|-----------|--------|
| 1 | All 21 cells have **0** injection gaps | **PASS** |
| 2 | All long-format triples (2h / 4h / 6h) show **distinct** `wc -w` per topic (no plateau) | **PASS** |
| 3 | Every `deep_book_6h` cell achieves **≥80%** of registry minimum **52,000** words (≥ **41,600**) | **FAIL** — grief **39,902**; somatic_healing **26,655**; anxiety **42,080** passes |
| 4 | Chapter flow: **≥18/21** runs pass (failed chapters expressed as **x/12** in table) | **PASS** (**18/21** PASS) |
| 5 | Short formats (micro / short / standard) remain **within** registry `word_range` **[min, max]** | **FAIL** — all **9** cells are **above** the declared maximum (over-delivery vs `format_registry.yaml`) |

## D. Spine-as-default recommendation

**NOT READY — do not flip spine to default on checklist alone.**

Specific gaps and rough effort (calendar time, one engineer familiar with spine / beatmap / flow gates):

| Gap | Evidence | Effort |
|-----|----------|--------|
| `deep_book_6h` **80%-of-min** bar | 2/3 topics under **41,600** words | **M–L** — grief needs ~**1.7k** words to clear 80% floor; somatic needs ~**15k** to clear floor (likely beatmap + enrichment + capped expansion, not Pearl_Writer alone) |
| Short-tier **registry band** compliance | 9/9 micro + `short_book_30` + `standard_book` cells **> max** | **M** — compression / length caps / or recalibrate registry bands for spine defaults |
| Grief **chapter flow** on shortest tiers | `micro_book_15`, `micro_book_20`, `short_book_30` still **FAIL** (**2/12**, **2/12**, **1/12**) | **S–M** — targeted flow remediation for short grief arcs |

**Conditional narrative:** Spine is **functionally dominant** on scaling, injection hygiene, and **majority** chapter-flow health; remaining work is **spec alignment** (short-tier maxima, 6h floor on somatic/grief) plus **narrow** grief short-format flow.

## E. Pearl_Writer live expansion (PR #398, `expand_thin_sections=True`)

**Dry-run reference:** `artifacts/pilots/pearl_writer_dryrun/dryrun_anxiety_standard_book.json`

- **~61.6%** of sections flagged expandable (**53/86**).
- Reference uplift on that artifact: **+11,667** words on a **8,015**-word baseline → **~+145.6%** total-book lift in that run (**8,015 → 19,682** projected), i.e. **~×2.45** if the same *shape* of expansion applied uniformly (not guaranteed across formats).

**Interpretive model (user-requested):** if **61.6%** of sections expand and expanded sections gain **+145%** words (**×2.45** on expanded mass only), a **uniform** word-mass blend implies an expected **×1.89** book-level multiplier (**0.384 + 0.616×2.45**). Treat as **order-of-magnitude** only — real gains depend on thin-section inventory and `target_words` caps.

### Cells still **below 80%** of **their** registry minimum

| Topic | Format | `wc -w` | Min target | 80% of min | Gap to 80% floor | Pearl_Writer note |
|---|---|---:|---:|---:|---:|---|
| grief | deep_book_6h | 39902 | 52000 | 41600 | **+1698** | Small gap — expansion likely sufficient **if** thin sections exist; must respect **58k** max |
| somatic_healing | deep_book_4h | 24209 | 36000 | 28800 | **+4591** | Expansion helpful; likely needs **additional** beatmap/enrichment if thin inventory is shallow |
| somatic_healing | deep_book_6h | 26655 | 52000 | 41600 | **+14945** | Large gap — expect **multi-track** work (beatmap + enrichment + capped Pearl_Writer), not expansion alone |

**Blended-model rough deltas** (×1.89 on current `wc -w`, for sizing only): grief +6h ≈ **+35.6k** words (would violate **max** without caps); somatic +4h ≈ **+21.6k**; somatic +6h ≈ **+23.8k**. Prefer **gap-to-80%** row for minimum closure targets; use dry-run **×2.45** ceiling only with explicit per-format calibration.

---

## CLOSEOUT (RESULTS_V2)

- **Verdict:** **NOT READY** for unconditional spine-as-default (checklist items **3** and **5** fail).
- **Next action:** (1) Recalibrate or enforce **short-format** `word_range` compliance. (2) Raise **`deep_book_6h`** delivered words for **grief** and **somatic_healing** (80% floor / full registry band as product requires). (3) Clear **grief** short-tier **chapter_flow** FAILs. After those, re-run this matrix and re-evaluate flipping default pipeline mode in `run_pipeline.py`.
