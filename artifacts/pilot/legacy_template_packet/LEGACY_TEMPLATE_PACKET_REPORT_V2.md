# Legacy Template Packet V2 — With Extracted Templates

**Topic:** anxiety  
**Persona:** gen_z_professionals  
**Teacher:** ahjan  
**Runtime format:** standard_book  
**Legacy library id:** `v4_therapeutic`  
**Date:** 2026-04-11  

---

## Environment note (critical for interpreting totals)

The **published V1 report** (`LEGACY_TEMPLATE_PACKET_REPORT.md`) recorded **9,170** packet words with **0** legacy scaffolds in an environment where `template_expand/chapter_bridges_all.md` and full template trees were expected on disk.

**This workspace** did not contain vendor `template_expand/*.zip` archives or `chapter_bridges_all.md` at session start. To unblock the extraction and loader path, a **small** `template_expand/audiobook_template_v4.zip` was created from the existing repo fixture `tests/fixtures/legacy_template/minimal_v4/` (nested `chapter_NN/section_NN/variant_F1.yaml`), then extracted to `template_expand/_extracted/audiobook_template_v4/` per the Phase 1 shell recipe. **This proves the pipeline end-to-end; it is not a full 12×10 commercial V4 library.** Replace the zip with the real vendor archive and re-extract to measure production-scale density.

**V2 zip libraries:** Only the V4 archive was added here. **V2** zips (`v2_full`, `v2_bestseller`, `v2_somatic`, `v2_both`) were still absent from the workspace, so they remain `status: missing` in the index.

---

## Template extraction

| Library | Archive | Extracted dir | Files | Format | Chapters (dirs) | Section YAML files | Words (yaml, `wc -w`) | Avg words / section file |
|---------|---------|---------------|-------|--------|-----------------|---------------------|------------------------|---------------------------|
| v4_therapeutic | `template_expand/audiobook_template_v4.zip` | `template_expand/_extracted/audiobook_template_v4/` | 2 | YAML (`title`, `text` block) | 2 | 2 (sparse grid: ch1 sec1, ch2 sec3) | 162 | 81 |

**Naming convention (observed):** `chapter_{NN}/section_{NN}/variant_F1.yaml` (only `F1` present in this bootstrap tree).

---

## V1 vs V2 comparison

### Against the published V1 report (9,170 words)

| Metric | V1 (published) | V2 (this run) | Target (6h model) |
|--------|----------------|---------------|---------------------|
| Total packet words | 9,170 | **8,566** | 54,000 |
| Legacy sections using scaffold | 0 / 102 | **2 / 102** | 120 (full grid) |
| Avg words / section | ~90 | ~84 | ~450 |
| Thin sections (&lt;200 w) | 94 / 102 | **94 / 102** | 0 |
| Bridge inserts | 11 / 102 | **0 / 102** | (n/a) |

**Why V2 total is below published V1:** No `chapter_bridges_all.md` in this workspace → **no bridge** contribution. The meaningful scaffold signal is the **legacy_template** source count, not raw total words vs the old 9.17k figure.

### Apples-to-apples (same workspace, same bridges = none)

| Metric | Baseline (`--legacy-library v2_full`, all legacy empty) | V2 (`v4_therapeutic`, extracted) | Delta |
|--------|-----------------------------------------------------------|----------------------------------|-------|
| Total packet words | **8,412** | **8,566** | **+154** |
| Sections with `legacy_template` in `sources_used` | 0 | **2** | +2 |

**Conclusion:** Extracting and resolving YAML scaffolds **did** add measurable prose (+154 words here) and **non-zero** legacy usage (**2** sections: chapter 1 section 1 and chapter 2 section 3, matching the fixture layout). Section density did **not** materially approach the 54k / 450w-per-slot target; that gap is dominated by **format** (`standard_book`), enrichment budgets, and the **absence of a full 120-cell V4 tree**.

---

## Source breakdown (V2 pilot, `sources_used`)

| Source | Sections (count) | Avg packet words when this source appears |
|--------|------------------|-------------------------------------------|
| legacy_template | 2 | ~117 |
| enrichment | 51 | ~49 |
| depth_module | 51 | ~119 |
| bridge | 0 | — |

Composer uses the key **`legacy_template`** (not `legacy_v4_scaffold`).

---

## Quality check

- **Coherence:** The two loaded scaffolds are short fixture prose; they read as coherent therapeutic-adjacent placeholders, not clinical claims.
- **Composition:** Full chapter sections still read as **enrichment + depth**-driven; legacy appears only where `(chapter, section)` matches files on disk.
- **Stubs vs prose:** Fixture text is **real sentences**, not one-line stubs, but **volume** is far below production audiobook scaffolds.
- **Most useful library:** Only `v4_therapeutic` was available; V2 libraries were not extracted.

---

## Remaining gap

- **Words still needed to 54k:** ~45,434 from this run’s **8,566** packet total (same order of magnitude as V1 shortfall).
- **What would close it:** Not extraction alone — need **`deep_book_6h`** (or equivalent) per-slot targets, full vendor V4 (or V2) trees with **dense** YAML per slot, and/or deterministic expansion beyond registry pulls. Exercise journey (out of scope elsewhere) affects practice cadence, not slot word count by itself.
- **Mainline integration:** Extraction + loader **work**; proceed to **`deep_book_6h` format comparison** before defaulting the spine path in `run_pipeline.py`.

---

## Verdict

**Did extracting the zip (and pointing the index at `_extracted/audiobook_template_v4`) materially improve the output?**

- **Versus the published 9.17k figure:** **No** — fewer total words here because **bridges are absent** in this workspace.
- **Versus a same-workspace baseline with no legacy:** **Yes** — **+154** words and **2** sections with `legacy_template` where there were **0** before.

**Next:** Drop in full **vendor** `audiobook_template_v4.zip` (and optionally V2 zips), re-run Phase 1 extract, re-audit layout, and re-pilot with **`--format deep_book_6h`** when ready to compare honestly to **54k**.

---

## Evidence paths

- Pilot outputs: `artifacts/pilot/legacy_template_packet_v2/anxiety/`
- Same-workspace baseline: `artifacts/pilot/legacy_template_packet_v2/anxiety_baseline_v2full/`
- Index: `config/templates/legacy_template_index.yaml`
- Loader: `phoenix_v4/planning/legacy_template_loader.py`
