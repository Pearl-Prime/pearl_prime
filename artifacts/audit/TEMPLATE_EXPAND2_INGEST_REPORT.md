# template_expand2/ Ingest Report

**Project:** `proj_state_convergence_20260328`  
**Subsystem:** `core_pipeline`, `teacher_mode`  
**Date:** 2026-04-11  
**Agents:** Pearl_Dev + Pearl_Editor + Pearl_Architect  

---

## Source inventory (root of `template_expand2/`)

Loose files at drop root: **21** zips, **16** atom batch `.txt`, **5** chat / lineage `.txt`, **3** markdown specs — **44** top-level files (excluding `_extracted/`), plus **`_extracted/`** trees (see audit for full zip catalog).  
Total files under `template_expand2/` (including extracted): **1,012** (measured `find template_expand2 -type f | wc -l`).

| Category | Count | Notes |
|----------|------:|-------|
| Zip archives | 21 | All extracted under `template_expand2/_extracted/` |
| Atom batch `.txt` | 16 | Imported via `scripts/ingest/import_template_expand2_atoms.py` (chat/old_chat excluded) |
| Chat / lineage `.txt` | 5 | Classified `prompt_lineage` — not imported |
| Spec `.md` | 3 | Reference only — not imported |
| Extracted dirs | 21 | One per zip; **~12 MB** on disk |

Authoritative classification tables: `artifacts/audit/TEMPLATE_EXPAND2_INGEST_AUDIT.md`.

---

## V2 somatic library (12×10×5)

**Library id:** `v2_somatic`  
**Path:** `template_expand2/_extracted/qaudiobook_template_v2_somatic/sections_somatic_v2/`  
**Archive:** `template_expand2/qaudiobook_template_v2_somatic.zip`

| Metric | Measured |
|--------|----------|
| Chapters | 12 (`chapter_01` … `chapter_12`) |
| Sections per chapter | 10 (`section_01_*` … `section_10_*`) |
| Variants per section | 5 (`f1.yaml` … `f5.yaml`) |
| Total section YAML files | 600 (+ `registry.yaml` at library root) |
| Total words (all YAML bodies, `content` key) | 92,325 |
| Average words per section file | ~153 |
| Fills 12×10×5 grid? | **YES** |

**Loader:** `phoenix_v4/planning/legacy_template_loader.py` resolves somatic paths as  
`chapter_{NN}/section_{NN}_<type>/fN.yaml` with YAML body in `content` (same as `text` / `body`).

---

## Persona atom import

**Script:** `scripts/ingest/import_template_expand2_atoms.py`  

| Metric | Value |
|--------|------:|
| Batch files processed | 14 (mapped in `FILE_PERSONA_TOPIC`; duplicates and chat files skipped) |
| Parsed atoms | 612 |
| Files written | 612 |
| Skipped (fingerprint dedup vs existing `atoms/<persona>/<topic>/`) | 0 |

**Note on dedup:** Dedup is **exact SHA-256 of normalized whitespace** against existing `.txt` under each target `atoms/<persona>/<topic>/` tree. Canonical persona batches did not fingerprint-match existing files in those trees in this run (0 skips). Editorial review may still fold near-duplicates; that is outside this importer.

**New persona content** (`midlife_women` and engines/topics per batch) is now on disk under `atoms/midlife_women/...`. **New personas are not added to `config/catalog_planning/canonical_personas.yaml` in this change** (PM decision).

---

## Existing persona overlap (canonical batches)

| File | Persona | Action |
|------|---------|--------|
| `gen_alpha_students__grief_*`, `gen_z_professionals__grief_*`, `healthcare_rns__grief_*` | Canonical | Imported under `atoms/.../grief/<ENGINE>/`; dedup 0 this run |
| `gen_alpha_students__anxiety__false_alarm__BATCH.txt` | gen_alpha_students | Imported under `atoms/gen_alpha_students/anxiety/` |
| `gen_alpha_students__core__PILOT_BATCH.txt` | gen_alpha_students | Imported under `atoms/gen_alpha_students/core/` |

---

## Pilot results (V3 — `v2_somatic`)

**Command:**

```bash
PYTHONPATH=. python3 scripts/pilot/run_legacy_template_packet_pilot.py \
  --topic anxiety \
  --persona gen_z_professionals \
  --teacher ahjan \
  --legacy-library v2_somatic \
  --output-dir artifacts/pilot/legacy_template_packet_v3/anxiety/ \
  --seed legacy_packet_pilot_v3
```

**Outputs:** `artifacts/pilot/legacy_template_packet_v3/anxiety/` (`book.txt`, `section_packet_audit.json`, `word_budget.json`, `README.md`).

| Metric | V1 (none) | V2 (bootstrap V4) | V3 (real `v2_somatic`) | Target (6h) |
|--------|-----------|---------------------|-------------------------|-------------|
| Total words (packets) | 9,170 | 8,566 | **18,715** | 54,000 |
| Sections in pilot | 102 | 102 | **101** | 120 (12×10) |
| Legacy scaffold sections with YAML text | 0 / 102 | 2 / 102 | **101 / 101** | full grid |
| Bridge inserts (ch &gt; 1) | 11 | 0 | **0** | 11 (needs `chapter_bridges_all.md` on disk) |
| Avg words / section | ~90 | ~84 | **185.3** | ~450 |
| Thin sections (&lt;200 w) | 94 | 94 | **73** | 0 |
| Sections ≥400 w | — | — | **8** | — |

**Gap to 54k:** V3 adds **~18.7k** packet words with **full** somatic legacy YAML per slot (F1). Remaining gap is **budget / composer / bridges / enrichment depth**, not missing template files for the 12×10×5 grid.

---

## Gap analysis

1. **V2 somatic library** closes the **“no real section YAML”** gap for the composer pilot: every section in this `standard_book` run loaded `v2_somatic` F1 text without `section_yaml_not_found`.
2. **54k target** still requires higher per-slot budgets (`deep_book_6h` or equivalent), stronger enrichment fill, and **chapter bridges** present (`template_expand/chapter_bridges_all.md` was not contributing in this workspace — 0 bridge hits).
3. **New personas** from zips are **indexed** in `legacy_template_index.yaml` as atom-library references; production promotion needs PM + `canonical_personas.yaml` update.

---

## Tests

- `python3 -m pytest tests/test_legacy_template_loader.py` — **9 passed** (includes `test_v2_somatic_expand2_section_when_extracted` when `template_expand2` is present).

---

## CLOSEOUT_RECEIPT

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Dev + Pearl_Editor + Pearl_Architect
TASK:           template_expand2 ingest: audit, V2 somatic loader/index, atom import, pilot V3
COMMIT_SHA:     (run `git log -1 --format=%H` on the branch containing this merge)
FILES_WRITTEN:  artifacts/audit/TEMPLATE_EXPAND2_INGEST_AUDIT.md; artifacts/audit/TEMPLATE_EXPAND2_INGEST_REPORT.md;
                config/templates/legacy_template_index.yaml; phoenix_v4/planning/legacy_template_loader.py;
                scripts/ingest/import_template_expand2_atoms.py; scripts/pilot/run_legacy_template_packet_pilot.py;
                tests/test_legacy_template_loader.py; template_expand2/**; atoms/** (expand2 imports);
                artifacts/pilot/legacy_template_packet_v3/**; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; artifacts/audit/TEMPLATE_EXPAND2_INGEST_AUDIT.md
STATUS:         completed
HANDOFF_TO:     Pearl_PM / Pearl_GitHub
NEXT_ACTION:    Open PR; run push-guard + preflight; optional editorial dedup pass on canonical atom batches
```
