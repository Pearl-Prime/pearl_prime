# Catalog Duration Audit — Planned vs Actual

**PROJECT_ID:** proj_state_convergence_20260328  
**Subsystem:** core_pipeline, ei_v2  
**Audit date:** 2026-04-10  
**WPM assumption:** 150 words/minute (audiobook narration), per audit charter.  
**Method:** Measure `artifacts/catalog/full_catalog.csv` planning fields; count F1 variant words in `registry/*.yaml`; run `scripts/run_pipeline.py` renders and count words in emitted `book.txt` / `budget.json`.  

---

## STARTUP_RECEIPT (session)

```
STARTUP_RECEIPT
AGENT:              Pearl_PM + Pearl_Dev + Pearl_Architect
TASK:               Full duration audit — catalog plans vs registry + pipeline output
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline, ei_v2
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; docs/DOCS_INDEX.md; artifacts/coordination/ACTIVE_PROJECTS.tsv; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv; artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv; specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md; specs/PHOENIX_V4_5_WRITER_SPEC.md; specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md (§1–3); config/duration/duration_registry.yaml; config/format_selection/format_registry.yaml
READ_PATH_COMPLETE: yes (governing coordination + architecture + CDIS spec + duration + format registries)
WRITE_SCOPE:        artifacts/audit/CATALOG_DURATION_AUDIT.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       Duration fixes; registry YAML edits; pipeline code; config changes; merging PRs without `gh pr diff N --stat | tail -1` check
BLOCKERS:            none
READY_STATUS:       ready
```

---

## Executive Summary

| Finding | Detail |
|--------|--------|
| **Catalog row count** | **8,287** data rows (source: `wc -l` on `artifacts/catalog/full_catalog.csv` → 8,288 lines including header). *Note: Some older docs cite ~12,483 rows; this checkout is **8,287**.* |
| **Format mix** | `short_book_30`: **6,141** (74.1%); `micro_book_15`: **1,183** (14.3%); `standard_book`: **963** (11.6%). Source: Python `Counter` on `runtime_format_id`. |
| **`duration_minutes` in catalog?** | **No.** Columns are planning-only: `estimated_word_count`, `estimated_chapters`, `runtime_format_id` (verified: no `duration_minutes` field in CSV header). |
| **Registry F1 vs `short_book_30` gate (4,500–5,500 words)** | **1 / 15 topics GREEN** in-band (`sleep_anxiety` 4,899 F1 words). **1 / 15 YELLOW high** (`grief` 7,979 F1 — over 5,500). **13 / 15 YELLOW low** (F1 3,765–4,435 words — under 4,500). Source: script over `registry/*.yaml` (F1 = first variant per section). |
| **Registry F1 vs `standard_book` gate (9,000–11,000 words)** | **0 / 15 GREEN.** All topics **RED** vs minimum (largest F1 still 7,979 &lt; 9,000). Source: same registry measurement. |
| **Sample renders (12-ch registry path)** | **Anxiety ~5,033 words (`wc -w`)** → **in** `short_book_30` band. **Burnout ~4,817 words** → **in** band. **Grief ~7,235 words** → **above** 5,500 (**too long** vs `short_book_30` max at 150 WPM). Sources: pipeline stdout + `budget.json` + `wc -w` on `book.txt` (see §4). |
| **Plan `runtime_format_id` in registry mode** | Compiled plans showed **`runtime_format_id: null`** — word-count gate may **skip** (`word_count_gate` in `phoenix_v4/rendering/book_renderer.py` when range missing). |
| **CDIS / EI v2 disconnect** | `duration_fit` scores against **`config/duration/duration_registry.yaml`** keys such as `audiobook_micro`, not `short_book_30`. Catalog + renderer use **`config/format_selection/format_registry.yaml`**. No automatic crosswalk in `phoenix_v4/quality/ei_v2/duration_fit.py`. |

---

## Duration Targets (authoritative sources)

### A. Runtime book targets (word budget + nominal minutes)

Source: `config/format_selection/format_registry.yaml` (`runtime_formats`).

| `runtime_format_id` | `duration_minutes` (config) | `word_range` [min, max] | Minutes @150 WPM from word range |
|---------------------|----------------------------|-------------------------|----------------------------------|
| `micro_book_15` | 15 | [2500, 3000] | ~17–20 |
| `micro_book_20` | 20 | [3000, 4000] | ~20–27 |
| `short_book_30` | 30 | [4500, 5500] | ~30–37 |
| `standard_book` | **55** | [9000, 11000] | **~60–73** |
| `extended_book_2h` | 120 | [18000, 22000] | ~120–147 |
| `deep_book_4h` | 240 | [36000, 44000] | ~240–293 |
| `deep_book_6h` | 360 | [52000, 58000] | ~347–387 |

*Observation:* `standard_book` **nominal `duration_minutes: 55`** disagrees with the **word_range** (~60–73 min @ 150 WPM). The **word range is what `word_count_gate` enforces** when `runtime_format_id` is set.

*Charter note:* External copy often cites ~15k–22.5k words for “100–150 min” standard audiobooks. **This repo’s enforced band for `standard_book` is 9,000–11,000 words** — document as a **product/planning choice**, not an industry benchmark.

### B. CDIS `duration_registry.yaml` (EI v2 / platform modality)

Source: `config/duration/duration_registry.yaml`. Intent-scoped; units **minutes** for audiobook family entries.

| Format key (CDIS) | Intent | Min | Optimal | Max | Words @150 WPM (optimal) |
|-------------------|--------|-----|---------|-----|---------------------------|
| `audiobook_micro` | discovery | 15 | **25** | 45 | **~3,750** |
| `audiobook_micro` | therapeutic | 45 | **90** | 120 | **~13,500** |
| `audiobook_micro` | deep_engagement | 360 | **480** | 720 | **~72,000** |
| `audiobook_standard` | therapeutic | 300 | **360** | 480 | **~54,000** |
| `audiobook_deep` | therapeutic | 480 | **600** | 720 | **~90,000** |

**These rows do not substitute for `short_book_30` / `standard_book`** without an explicit mapping layer. Today, **`score_duration_fit()`** expects `content_meta["format"]` to match **`duration_registry.yaml`** keys, not catalog `runtime_format_id`.

### C. Therapeutic dose (modalities)

Source: `config/duration/therapeutic_dose_rules.yaml`: e.g. **narrative_transport** `minimum_effective_dose_minutes: 30`, `optimal_dose_minutes: 45` — aligns **loosely** with a **~30 min** SKU but does not set word counts.

---

## Catalog Planning Analysis

**Source:** `artifacts/catalog/full_catalog.csv`, Python aggregation (2026-04-10).

### Format distribution

| `runtime_format_id` | Rows |
|---------------------|------|
| `short_book_30` | 6,141 |
| `micro_book_15` | 1,183 |
| `standard_book` | 963 |

**No rows** in this file use `deep_book_4h`, `deep_book_6h`, or `extended_book_2h` (distribution count = 0 for those IDs).

### `estimated_word_count` vs `format_registry.yaml`

| Format | Avg catalog range (lo–hi) | Implied min @150 WPM | `format_registry` `word_range` |
|--------|---------------------------|----------------------|--------------------------------|
| `micro_book_15` | 2,500–3,000 | ~17–20 min | [2500, 3000] — **aligned** |
| `short_book_30` | 4,500–5,500 | ~30–37 min | [4500, 5500] — **aligned** |
| `standard_book` | 9,000–11,000 | ~60–73 min | [9000, 11000] — **aligned** |

At **planning** level, the catalog **matches** `format_registry` word bands.

---

## Registry Content Measurement (15 topics)

**Method:** For each `registry/<topic>.yaml`, sum **word count of variant `F1` only** (first variant in each section’s `variants` list). **Source files:** `registry/*.yaml`.

| Topic | F1 words | Chapters | Sections | Variants | ~min @150 WPM |
|-------|----------|----------|----------|----------|----------------|
| somatic_healing | 3,765 | 12 | 90 | 324 | 25 |
| imposter_syndrome | 3,885 | 12 | 90 | 324 | 26 |
| social_anxiety | 3,913 | 12 | 90 | 324 | 26 |
| depression | 4,037 | 12 | 90 | 324 | 27 |
| courage | 4,105 | 12 | 90 | 324 | 27 |
| anxiety | 4,201 | 12 | 90 | 324 | 28 |
| financial_anxiety | 4,203 | 12 | 90 | 324 | 28 |
| burnout | 4,245 | 12 | 90 | 324 | 28 |
| self_worth | 4,277 | 12 | 90 | 324 | 29 |
| compassion_fatigue | 4,305 | 12 | 90 | 324 | 29 |
| overthinking | 4,411 | 12 | 90 | 324 | 29 |
| boundaries | 4,435 | 12 | 90 | 324 | 30 |
| sleep_anxiety | 4,899 | 12 | 90 | 324 | 33 |
| financial_stress | 4,005 | 12 | 90 | 324 | 27 |
| **grief** | **7,979** | 12 | 90 | **203** | **53** |

**Section / variant tally (user-requested samples):**  
- `registry/grief.yaml`: **12** chapters, **90** sections, **203** variants (excerpt lines 1–30 reviewed).  
- `registry/anxiety.yaml`: **12** chapters, **90** sections, **324** variants (excerpt lines 1–30 reviewed).

**Compliance vs `short_book_30` [4500, 5500] on F1 alone**

| Status | Rule (audit charter) | Topics |
|--------|----------------------|--------|
| **GREEN** | Within [4500, 5500] | `sleep_anxiety` |
| **YELLOW (short)** | Below 4500 | 13 topics |
| **YELLOW (long)** | Above 5500 | `grief` |
| **RED (&lt;80% of 4500)** | &lt; 3,600 words | **none** |

**Compliance vs `standard_book` [9000, 11000] on F1 alone:** **all 15 → RED** (under 9,000 words).

**Words/chapter (illustrative):** F1 totals ÷ 12 ≈ **315–665** words/chapter depending on theme; **grief** is a **long-form outlier** vs template-generated packs.

---

## Pipeline Render Measurement (3 sample books)

**Constraint:** `scripts/run_pipeline.py` enforces **`job.json`** in the output workspace unless **`--no-job-check`** is passed (2026-04-10 behavior). Renders below used **`--no-job-check`** for a CI-style audit (stderr warns: testing only).

**Common flags:** `--render-book --quality-profile draft --no-generate-freebies --no-update-freebie-index`.

| Book | Arc file | Registry | `wc -w` `book.txt` | `budget.json` `word_count` | Catalog row for persona×topic (short_book_30) |
|------|-----------|----------|--------------------|-----------------------------|-----------------------------------------------|
| Grief | `config/source_of_truth/master_arcs/gen_z_professionals__grief__grief__F006.yaml` | `registry/grief.yaml` | **7,235** | **7,273** | `estimated_word_count` **4500-5500** (e.g. `catalog_id` CAT-69C6B1006576) — **91** rows for `gen_z_professionals` × `grief` |
| Anxiety | `config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml` | `registry/anxiety.yaml` | **5,033** | **4,904** | **4500-5500** (e.g. CAT-AB3ECC8A5F91) |
| Burnout | `config/source_of_truth/master_arcs/gen_z_professionals__burnout__overwhelm__F006.yaml` | `registry/burnout.yaml` | **4,817** | **4,693** | **0** catalog rows for `gen_z_professionals` × `burnout` (planning gap) |

**Arc note:** Master arcs declare **`chapter_count: 20`**, but the **registry defines 12 chapters** — the render path **stops at registry coverage** (12 chapters in `budget.json`).

**Plan metadata (`*.plan.json`):** `runtime_format_id` was **`null`** for all three; `output_contract.json` reports `"source": "section_registry"`. **Implication:** **`word_count_gate()`** treats missing runtime as **skip** (see `book_renderer.py` gate returns `status: skip` when `word_range` missing).

**Gap vs catalog `short_book_30` band [4500, 5500]:**

| Sample | Status |
|--------|--------|
| Anxiety | **GREEN** |
| Burnout | **GREEN** |
| Grief | **YELLOW (long)** — exceeds 5,500 by **~1.3k+** words |

**Teacher / exercise augmentation:** Rendered word counts **exceed** raw **F1** sums (e.g. anxiety F1 4,201 vs render ~5,033) — deltas credit **non-registry slots** (exercises, overlays, `library_34` fallbacks logged in stderr).

---

## `artifacts/production_run/`

**Listing:** Only `artifacts/production_run/PRODUCTION_QUALITY_REPORT.md` present (no `budget.json` / `book.txt` tree). Source: workspace glob 2026-04-10.

---

## How Duration Is Tracked in Code

**`scripts/run_pipeline.py`** (grep hits): pre-render **`check_word_budget`** from `phoenix_v4.planning.budget_check` against `format_registry.yaml` `word_range`; can **exit 1** before render if insufficient when `--render-book`. Post-render: **`render_book(..., enforce_word_count=...)`**; **`budget.json`** with `word_count` and per-chapter words.

**`phoenix_v4/rendering/book_renderer.py`:** **`word_count_gate`** uses **`config/format_selection/format_registry.yaml`** `runtime_formats[runtime_format_id].word_range`. **`build_budget_report`** / **`budget.json`** break down per-slot / per-chapter word estimates.

**`phoenix_v4/quality/ei_v2/duration_fit.py`:** Loads **`config/duration/duration_registry.yaml`**; compares `content_meta` duration/pages/panels to **min/opt/max** for **`format` + `intent`**; **not** wired to catalog `runtime_format_id`.

**`config/quality/ei_v2_config.yaml`:** `duration_fit` composite weight **0.20**; `hybrid.duration_fit_block_threshold: 0.44`.

---

## Compliance Matrix (sample × `short_book_30` catalog band)

| Sample | Target words (catalog / format_registry) | Rendered words (`wc -w`) | Target min @150 WPM | Actual min @150 WPM | Gap |
|--------|--------------------------------------------|----------------------------|----------------------|------------------------|-----|
| Anxiety | 4,500–5,500 | 5,033 | 30–37 | ~33.6 | On target |
| Burnout | 4,500–5,500 | 4,817 | 30–37 | ~32.1 | On target |
| Grief | 4,500–5,500 | 7,235 | 30–37 | ~48.2 | **+~11 min** vs 37 min ceiling |

---

## Root Cause Analysis (RED / YELLOW)

| # | Cause | Evidence | Fix lever | Effort |
|---|--------|----------|-----------|--------|
| a | **Registry F1 prose is thin** for template topics — **~4k words / 12 chapters** vs **4.5k–5.5k** SKU | §Registry table | Expand variants (especially F1), lengthen sections, or add slots | **High** (content) |
| b | **Grief pack is dense** — F1 **7,979** words → **overshoots** micro/short targets if labeled `short_book_30` | Grief row + render | SKU split (micro vs full grief track) or separate `runtime_format_id` / pricing tier | **Medium** (planning + catalog) |
| c | **Arc `chapter_count` (20) ≠ registry (12)** — silent truncation | Master arc YAML vs `budget.json` chapter_count | Regenerate arcs to **12** or **expand registries** to 20 | **Medium** |
| d | **Registry mode drops `runtime_format_id`** — **no word gate** | `*.plan.json` + `book_renderer.word_count_gate` | Persist resolved `runtime_format_id` in registry compile; enforce band | **Low–medium** (code) |
| e | **EI v2 duration_fit taxonomy ≠ catalog** | `duration_fit.py` vs `duration_registry` keys | Map `runtime_format_id` → `audiobook_*` + intent; pass **seconds** from words×0.4 | **Medium** |
| f | **Burnout × persona catalog gap** | 0 rows `burnout` × `gen_z_professionals` | `catalog_generation_config` / kill rules review | **Low** (catalog gen) |
| g | **Exercise fallbacks (`library_34`)** inflate/deflate vs teacher-specific atoms | Pipeline stderr | Fill EXERCISE coverage in registries / teacher banks | **Medium** |

---

## Recommendations

| Priority | Item |
|----------|------|
| **P0** | **`standard_book` SKUs cannot be honored** by current 12-ch registry F1 totals (&lt;9k words). **Do not market** those catalog rows as 9k–11k manuscripts **until** render path proves ≥9k words or catalog is **downscoped**. |
| **P0** | **`runtime_format_id: null`** in registry renders → **no automated duration enforcement**. Wire format + gate for shippable builds. |
| **P1** | **Grief** content is **too long** for `short_book_30` if strict gate — risk of **SKU mismatch** vs catalog row **4.5k–5.5k**. |
| **P1** | Align **`duration_minutes`** on `standard_book` with **word_range** or document **55 min** as **listening-time target** with different WPM. |
| **P2** | **CDIS intent scoring** vs **commercial runtime SKUs** — add explicit **crosswalk** for EI v2 and analytics. |

---

## Fix Options (per charter)

| Option | When |
|--------|------|
| **A. Registry expansion** | Default path for **YELLOW-low** topics; raises F1 into **4.5k–5.5k** without tricks. |
| **B. Pipeline padding / expansion** | LLM or templated expansion to **hitting** `word_range` — **risk** to voice; needs QA. |
| **C. Adjust catalog targets** | If **therapeutically** and **commercially** you want shorter reads, **lower** `estimated_word_count` / change `runtime_format_id` (truth in advertising). |
| **D. Multi-registry / longer arcs** | For **`standard_book`**, **add chapters** or **second registry pass** to reach **9k+**. |

---

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_PM + Pearl_Dev + Pearl_Architect
TASK:           Catalog duration audit (plans vs registry vs render)
COMMIT_SHA:     (not embedded in blob; run `git rev-parse HEAD` on `agent/duration-audit` after pull)
FILES_WRITTEN:  artifacts/audit/CATALOG_DURATION_AUDIT.md; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; config/duration/*.yaml; config/catalog/catalog_generation_config.yaml; config/catalog_planning/canonical_*.yaml; config/format_selection/format_registry.yaml; config/quality/ei_v2_config.yaml; artifacts/catalog/full_catalog.csv; registry/grief.yaml; registry/anxiety.yaml; scripts/run_pipeline.py; phoenix_v4/rendering/book_renderer.py; phoenix_v4/quality/ei_v2/duration_fit.py; specs/CONTENT_DURATION_INTELLIGENCE_DEV_SPEC.md
STATUS:         completed
HANDOFF_TO:     Pearl_PM / owner (optional PR merge after preflight)
NEXT_ACTION:    If merging PR: run `gh pr diff <N> --stat | tail -1`; if deletions > 50 files, stop for owner approval.
```
