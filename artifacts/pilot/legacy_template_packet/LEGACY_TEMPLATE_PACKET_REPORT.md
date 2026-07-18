# Legacy Template Packet Pilot Report

**Topic:** anxiety  
**Persona:** gen_z_professionals  
**Teacher:** ahjan  
**Runtime format:** standard_book (spine pipeline; not the 6h `deep_book_6h` format)  
**Legacy library id:** `v4_therapeutic`  
**Date:** 2026-04-11  

This pilot stitches **section packets** (bridge → legacy YAML scaffold → enrichment → depth) after the existing spine → knob → beatmap → enrichment + depth pass. It does **not** change Pearl Prime defaults.

---

## Did the loader work?

| Library / path | Status on disk |
|----------------|----------------|
| `template_expand/audiobook_template_v4/` (directory) | **Missing** — only `audiobook_template_v4.zip` exists |
| `template_expand/_extracted/v4_therapeutic/` | **Missing** |
| `template_expand/chapter_bridges_all.md` | **Available** — parsed successfully |
| Python modules `01_hooks.py` … `05_teacherdoctrine.py` | **Available** (not used as YAML in this slice) |
| Other V2 zip archives | **Present as zips only** — not extracted |

**Sections with non-empty legacy YAML:** **0 / 102** (all `load_legacy_section` calls returned empty `text` with warning `library_path_missing:template_expand/audiobook_template_v4`).

The loader behaved as designed: **no crashes**, structured warnings on every section.

---

## Section composition

Counts are for **102 stitched slots** (12 chapters × base beatmap slots + depth-appended slots). This is **not** the 12×10=120 legacy grid; `standard_book` plus depth produced 102 rows in this run.

| Source | Sections using it | Avg words (full section text when this source appears in `sources_used`) |
|--------|-------------------|--------------------------------------------------------------------------|
| legacy_template | 0/102 | 0 (no YAML on disk) |
| enrichment | 51/102 | ~61 |
| bridge | 11/102 | ~100 (first slot of chapters 2–12; includes bridge + body) |
| depth_module | 51/102 | ~119 |

**Note:** Averages are **total packet word counts** for rows that list that source, not isolated token contributions from each block.

---

## Word count

- **Total (sum of section packets):** 9,170 words (**target for a 6h line: 54,000** — not claimed as achieved).
- **Gap to 54,000:** **44,830** words (~83% below target).
- **Average per section:** ~90 words (target often cited for 6h: **450** per section in the 12×10 model).
- **Sections at ≥400 words:** 7/102.
- **Thin sections (<200 words):** 94/102.

**Brutal honesty:** This run is far from a 6-hour book. The spine `standard_book` budget is ~9–11k words; depth adds material but does not approach 54k. Reaching six hours requires a **different runtime/format**, much higher per-slot targets, extracted legacy scaffolds, and/or additional deterministic expansion — none of which are asserted here.

---

## Thin section analysis

**Thin slots** cluster on **HOOK, SCENE, REFLECTION, INTEGRATION** (12 each under 200 words in this audit) — i.e. the **base beatmap** slots before depth, which are short in teacher/persona/registry pulls. **Chapters 9–12** show the most thin sections (10–11 each), correlating with many appended depth slots that are individually short or capped.

**Depth slot types** also appear in the thin list (`DEPTH_PRACTICE_SCAFFOLD`, `DEPTH_BRIDGE_TRANSITION`, `DEPTH_INTEGRATION_LANDING`, etc.) when the composed text stayed under 200 words.

---

## Quality assessment

- **Versus plain slot concatenation:** Ordering (bridge → legacy → enrichment → depth) adds **transition text** at chapter opens when bridges load; with **no legacy YAML**, the main difference vs `compose_from_enriched_book` is **bridge prepend** on 11 section starts and **placeholder stripping + `clean_for_delivery`** on the combined block.
- **Bridge coherence:** The legacy bridge file is **generic spiritual/self-help** tone; it does **not** match the anxiety spine thesis verbatim. It is useful mechanically (transition glue) but **not** topic-aligned without curation or replacement.
- **Legacy scaffolds:** **No V4 YAML** was available, so **no structural lead-in** from the old library in this run.

---

## Honest gaps

1. **Extract** `audiobook_template_v4.zip` (and optionally V2) into `template_expand/_extracted/v4_therapeutic/...` so `load_legacy_section` can return real text.
2. **Raise word targets** — use `deep_book_6h` (or a dedicated pilot format) if the goal is to measure against **54k**; `standard_book` will not get there.
3. **Exercise journey planner** (explicitly out of scope for this PR) would map sections 4 / 8 / 10 in the 10-section model to practice cadence.
4. **Bridge library** may need **topic-specific** bridges or spine-derived transitions instead of the generic `chapter_bridges_all.md` text.

---

## Next step (follow-up PR)

1. Unzip V4 under `template_expand/_extracted/v4_therapeutic/` using the documented layout; re-run this pilot and expect **non-zero** `legacy_template` usage.
2. Add optional **format override** for pilot (`deep_book_6h`) to compare word budgets against 54k honestly.
3. Keep this path behind **explicit scripts** (`run_legacy_template_packet_pilot.py`) until quality review passes — **do not** wire as default in `run_pipeline.py` until approved.
