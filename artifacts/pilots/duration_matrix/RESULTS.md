# Duration matrix pilot — spine pipeline

- Branch tooling: `scripts/pilot/run_duration_matrix_pilot.py`
- Persona: `gen_z_professionals`
- Topics: grief (trauma), anxiety, somatic_healing (somatic)
- Formats: seven `runtime_formats` from `config/format_selection/format_registry.yaml`

## Escalation rule

Flag to **TEAM A (beatmap / injection)** when actual word count is below **80%** of the registry minimum (`word_range[0]`) for that runtime format.

## Results

| Topic | Tier (runtime) | Target words (min–max) | Actual words | Sections filled (≥50% slot target) | Injection gaps | Gate (chapter flow) |
|---|---|---:|---:|---|---:|---|
| grief | micro (~15m) (`micro_book_15`) | 2500–3000 | 3330 | 37/49 | 0 | FAIL |
| grief | short (~20m) (`micro_book_20`) | 3000–4000 | 3330 | 37/49 | 0 | FAIL |
| grief | standard (~30m) (`short_book_30`) | 4500–5500 | 4428 | 32/61 | 0 | FAIL |
| grief | extended (~1h) (`standard_book`) | 9000–11000 | 8353 | 25/75 | 0 | FAIL |
| grief | deep (~2h) (`extended_book_2h`) | 18000–22000 | 10749 | 15/86 | 0 | FAIL |
| grief | immersive (~4h) (`deep_book_4h`) | 36000–44000 | 10749 | 12/86 | 0 | FAIL |
| grief | full (~6h) (`deep_book_6h`) | 52000–58000 | 10749 | 12/86 | 0 | FAIL |
| anxiety | micro (~15m) (`micro_book_15`) | 2500–3000 | 2779 | 39/51 | 0 | FAIL |
| anxiety | short (~20m) (`micro_book_20`) | 3000–4000 | 3501 | 44/60 | 0 | FAIL |
| anxiety | standard (~30m) (`short_book_30`) | 4500–5500 | 4771 | 36/70 | 0 | FAIL |
| anxiety | extended (~1h) (`standard_book`) | 9000–11000 | 8344 | 15/86 | 0 | FAIL |
| anxiety | deep (~2h) (`extended_book_2h`) | 18000–22000 | 11563 | 20/100 | 0 | FAIL |
| anxiety | immersive (~4h) (`deep_book_4h`) | 36000–44000 | 11563 | 17/100 | 0 | FAIL |
| anxiety | full (~6h) (`deep_book_6h`) | 52000–58000 | 11563 | 17/100 | 0 | FAIL |
| somatic_healing | micro (~15m) (`micro_book_15`) | 2500–3000 | 2262 | 18/46 | 0 | FAIL |
| somatic_healing | short (~20m) (`micro_book_20`) | 3000–4000 | 2992 | 17/51 | 0 | FAIL |
| somatic_healing | standard (~30m) (`short_book_30`) | 4500–5500 | 4003 | 15/53 | 0 | FAIL |
| somatic_healing | extended (~1h) (`standard_book`) | 9000–11000 | 5781 | 10/63 | 0 | FAIL |
| somatic_healing | deep (~2h) (`extended_book_2h`) | 18000–22000 | 6884 | 11/67 | 0 | FAIL |
| somatic_healing | immersive (~4h) (`deep_book_4h`) | 36000–44000 | 6884 | 11/67 | 0 | FAIL |
| somatic_healing | full (~6h) (`deep_book_6h`) | 52000–58000 | 6884 | 11/67 | 0 | FAIL |

## Runs below 80% of registry minimum (TEAM A)

- **grief** / `extended_book_2h`: actual 10749 < 80% of minimum target 18000 (59.7% of min).
- **grief** / `deep_book_4h`: actual 10749 < 80% of minimum target 36000 (29.9% of min).
- **grief** / `deep_book_6h`: actual 10749 < 80% of minimum target 52000 (20.7% of min).
- **anxiety** / `extended_book_2h`: actual 11563 < 80% of minimum target 18000 (64.2% of min).
- **anxiety** / `deep_book_4h`: actual 11563 < 80% of minimum target 36000 (32.1% of min).
- **anxiety** / `deep_book_6h`: actual 11563 < 80% of minimum target 52000 (22.2% of min).
- **somatic_healing** / `standard_book`: actual 5781 < 80% of minimum target 9000 (64.2% of min).
- **somatic_healing** / `extended_book_2h`: actual 6884 < 80% of minimum target 18000 (38.2% of min).
- **somatic_healing** / `deep_book_4h`: actual 6884 < 80% of minimum target 36000 (19.1% of min).
- **somatic_healing** / `deep_book_6h`: actual 6884 < 80% of minimum target 52000 (13.2% of min).

## Observations (EI V2 / systems read)

- **Chapter flow:** all 21 runs reported `chapter_flow` **FAIL** (12/12 chapters) — consistent with session handoff known spine gap; `quality_summary.json` stays PASS in `--quality-profile draft` because failures are non-blocking.
- **Word-count plateau:** For **grief** and **anxiety**, `extended_book_2h` / `deep_book_4h` / `deep_book_6h` share the same delivered word count per topic. **somatic_healing** shows the same three-way tie in this run — runtime format is not scaling total prose into the long bands yet (beatmap / enrichment / compose path).
- **Injection placeholders:** no `[*INJECTION*]` tokens observed in delivered `book.txt` for this matrix (count 0).

## Machine-readable output

Per-run metrics: `artifacts/pilots/duration_matrix/results.json`.
Each cell directory contains `book.txt`, `budget.json`, `plan.json`, `chapter_flow_report.json`, `quality_summary.json`.

