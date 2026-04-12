# Duration matrix pilot — RESULTS V3 (spine-as-default gate)

## Provenance

- **Pipeline:** `scripts/pilot/run_duration_matrix_pilot.py` (`--pipeline-mode spine`, persona `gen_z_professionals`, `draft` quality profile).
- **Git HEAD:** `8c337eb661972aaab019ffe1bc3d16644b4452ae` (matches `origin/main` at run time).
- **Merged baseline:** [PR #403](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/403) (grief short-format chapter flow — runtime-aware flow profiles); [PR #404](https://github.com/Ahjan108/phoenix_omega_v4.8/pull/404) — both merge commits are ancestors of this HEAD.
- **Artifacts:** per-cell dirs under `artifacts/pilots/duration_matrix/<topic>/<runtime_format>/`; machine-readable metrics in `results.json`.
- **Run completed:** 2026-04-12 (full matrix ~21 sequential spine runs).

## Spine-as-default verdict

**BLOCKED — not ready for spine-as-default.**

**Reasons (must clear before defaulting spine):**

1. **Registry word band:** For most runtime formats, delivered `book.txt` word counts sit **above** `word_range` max on micro through extended tiers, and **below** min on `deep_book_4h` for grief and somatic_healing. Only a minority of cells land inside `[range_min, range_max]` (see per-cell table).
2. **Chapter flow gate:** Four of twenty-one cells report **non-zero** `failed_chapters` in `chapter_flow_report.json` (`grief` / `deep_book_6h`, `anxiety` / `deep_book_6h`, `somatic_healing` / `short_book_30`, `somatic_healing` / `deep_book_6h`). Target for this matrix is **0/N** failures per cell.
3. **Column rollup:** No format column passes **all three topics** on both word band and flow simultaneously (verification matrix below).

**What already clears the bar:** **Injection gaps** — zero `[*INJECTION*]`-style placeholders in every cell (`injection_gaps == 0`). Pipeline exits were **0** for all 21 runs.

---

## Verification matrix (column = runtime format)

Each cell is **✓** only if **all three topics** (grief, anxiety, somatic_healing) satisfy that row’s criterion for that format. Otherwise **✗**.

| Criterion | micro_book_15 | micro_book_20 | short_book_30 | standard_book | extended_book_2h | deep_book_4h | deep_book_6h |
|---|---|---|---|---|---|---|---|
| Word count (`range_min` ≤ actual ≤ `range_max`) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Flow gate (0 chapter failures vs report `chapter_count`) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |
| Injection gaps (0 leaked placeholders) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

Registry bands from `config/format_selection/format_registry.yaml`:  
micro_book_15 `[2500,3000]`, micro_book_20 `[3000,4000]`, short_book_30 `[4500,5500]`, standard_book `[9000,11000]`, extended_book_2h `[18000,22000]`, deep_book_4h `[36000,44000]`, deep_book_6h `[52000,58000]`.

---

## All 21 cells (detail)

Flow column shows `failed_chapters` / `chapter_count` from `chapter_flow_report.json` (target **0/N**). Word column shows actual count vs band.

| Topic | Format | Word band | Actual words | Word OK | Flow | Inj. OK |
|---|---|---:|---:|:---|:---|:---|
| grief | micro_book_15 | 2500–3000 | 3895 | ✗ | 0/12 ✓ | ✓ |
| grief | micro_book_20 | 3000–4000 | 4157 | ✗ | 0/12 ✓ | ✓ |
| grief | short_book_30 | 4500–5500 | 6454 | ✗ | 0/12 ✓ | ✓ |
| grief | standard_book | 9000–11000 | 11918 | ✗ | 0/12 ✓ | ✓ |
| grief | extended_book_2h | 18000–22000 | 22386 | ✗ | 0/12 ✓ | ✓ |
| grief | deep_book_4h | 36000–44000 | 31517 | ✗ | 0/12 ✓ | ✓ |
| grief | deep_book_6h | 52000–58000 | 59762 | ✓ | 10/12 ✗ | ✓ |
| anxiety | micro_book_15 | 2500–3000 | 3583 | ✗ | 0/12 ✓ | ✓ |
| anxiety | micro_book_20 | 3000–4000 | 5020 | ✗ | 0/12 ✓ | ✓ |
| anxiety | short_book_30 | 4500–5500 | 6610 | ✗ | 0/12 ✓ | ✓ |
| anxiety | standard_book | 9000–11000 | 12114 | ✗ | 0/12 ✓ | ✓ |
| anxiety | extended_book_2h | 18000–22000 | 23770 | ✗ | 0/12 ✓ | ✓ |
| anxiety | deep_book_4h | 36000–44000 | 35935 | ✗ | 0/12 ✓ | ✓ |
| anxiety | deep_book_6h | 52000–58000 | 59345 | ✓ | 3/12 ✗ | ✓ |
| somatic_healing | micro_book_15 | 2500–3000 | 3924 | ✗ | 0/12 ✓ | ✓ |
| somatic_healing | micro_book_20 | 3000–4000 | 4950 | ✗ | 0/12 ✓ | ✓ |
| somatic_healing | short_book_30 | 4500–5500 | 6448 | ✗ | 1/12 ✗ | ✓ |
| somatic_healing | standard_book | 9000–11000 | 11862 | ✗ | 0/12 ✓ | ✓ |
| somatic_healing | extended_book_2h | 18000–22000 | 18752 | ✓ | 0/12 ✓ | ✓ |
| somatic_healing | deep_book_4h | 36000–44000 | 24207 | ✗ | 0/12 ✓ | ✓ |
| somatic_healing | deep_book_6h | 52000–58000 | 55984 | ✓ | 6/12 ✗ | ✓ |

**Note:** This pilot’s `chapter_flow_report.json` reports `chapter_count: 12` for every cell (including micro formats). Flow results use `failed_chapters` / `chapter_count` from that file.

---

## Follow-ups (Team C / pipeline)

- **Word budget vs registry:** Tune spine compose/budget so short–standard runtimes stop overshooting `word_range` max, and `deep_book_4h` reaches min for all pilot topics.
- **Flow residual:** Resolve remaining `chapter_flow` FAIL cells (especially `deep_book_6h` across topics and `somatic_healing` / `short_book_30`).
- **Pilot script doc drift:** `RESULTS.md` still contains outdated narrative (e.g. “all 21 runs FAIL”); V3 reflects this run’s `results.json` only.
