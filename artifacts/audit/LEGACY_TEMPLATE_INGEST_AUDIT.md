# Legacy Template Ingest Audit

**Project:** `proj_state_convergence_20260328`
**Subsystem:** `core_pipeline`
**Date:** 2026-04-11
**Auditor:** Pearl_Dev + Pearl_Architect

## Scope

This audit covers **all tracked files under `template_expand/`** and **three historical chat-spec files under `old_chat_specs/`** referenced for legacy audiobook scaffolding. It records what exists on disk, what is missing, and how each source maps to Phoenix pipeline concepts.

## Critical finding: V2/V4 template libraries are ZIP-only

The following **directories do not exist** as extracted trees:

- `template_expand/audiobook_template_v4/` — **missing** (only `audiobook_template_v4.zip` present)
- `template_expand/audiobook_template_v2_full/` — **missing** (only `.zip`)
- `template_expand/audiobook_template_v2_SOMATIC/` — **missing** (only `.zip`)
- `template_expand/audiobook_templates_v2_BOTH/` — **missing** (only `.zip`)
- `template_expand/audiobook_template_v2_bestseller/` — **missing** (only `.zip`)
- `template_expand/_extracted/` — **missing** (recommended layout for future YAML extraction is documented in `config/templates/legacy_template_index.yaml`)

**Implication:** Until archives are extracted under a stable path (e.g. `template_expand/_extracted/v4_therapeutic/...`), the legacy YAML section loader **cannot** load per-chapter/per-section scaffolds from those libraries. The machine index marks these as `status: missing` at the directory path; zip files are listed as `available` as **archives** only.

## Per-file inventory (`template_expand/`)

Word counts use `wc -w` on text sources. **Zip files are binary; word counts from `wc` are not meaningful** — listed as *binary archive* with approximate file size.

| Path | Type | Complete / partial | Words (approx.) | Chapters | Sections/ch. | Variants/section |
|------|------|-------------------|-----------------|----------|--------------|------------------|
| `template_expand/01_hooks.py` | code_embedded | Partial (hooks library; not YAML) | ~5,562 | 12 (phases) | 20 hooks (4×5) implied in header | 5 variants / phase block |
| `template_expand/02_scenes.py` | code_embedded | Partial | ~2,577 | (see module) | (see module) | (see module) |
| `template_expand/03_reflections.py` | code_embedded | Partial | ~5,748 | (see module) | (see module) | (see module) |
| `template_expand/04_exercises.py` | code_embedded | Partial | ~2,528 | (see module) | (see module) | (see module) |
| `template_expand/05_teacherdoctrine.py` | code_embedded | Partial | ~4,290 | (see module) | (see module) | (see module) |
| `template_expand/chapter_bridges_all.md` | bridge | Complete for 12 chapters | ~1,753 | 12 | 2 blocks each (conclusion + next bridge) | N/A |
| `template_expand/complete_chapters_integrated.md` | integrated_chapter | Complete stitched export | ~5,865 | 12 | Full chapter per row (CSV-like) | Pause markers `{{ pause_s }}` |
| `template_expand/section_01_all_chapters.md` | prose / integrated | Partial (openings only) | ~343 | 12 | Section 1 only | N/A |
| `template_expand/audiobook_template_v4.zip` | archive | **Not extracted** | — (binary ~619 KB) | 12 (expected when extracted) | 10 (expected) | 5 (expected) |
| `template_expand/audiobook_template_v2_full.zip` | archive | **Not extracted** | — (binary ~519 KB) | unknown until extract | unknown | unknown |
| `template_expand/audiobook_template_v2_somatic.zip` | archive | **Not extracted** | — (binary ~570 KB) | unknown until extract | unknown | unknown |
| `template_expand/audiobook_template_v2_bestseller.zip` | archive | **Not extracted** | — (binary ~601 KB) | unknown until extract | unknown | unknown |
| `template_expand/audiobook_templates_v2_BOTH.zip` | archive | **Not extracted** | — (binary ~1.09 MB) | unknown until extract | unknown | unknown |

## Per-file inventory (`old_chat_specs/`)

| Path | Type | Complete / partial | Words (approx.) | Notes |
|------|------|-------------------|-----------------|-------|
| `old_chat_specs/old_chat_pose_book_template.txt` | prompt_lineage | Partial (chat transcript + pasted specs) | ~21,609 | Therapeutic preprompt, 10-section template references, TTS constraints — **historical lineage**, not runtime atoms |
| `old_chat_specs/old_claude_template_persona_stuff.txt` | prompt_lineage | Partial (chat + narrative craft notes) | ~18,266 | Persona/story mechanism discussion — **historical**, not ingested prose |
| `old_chat_specs/question_book_template_2025-01-13.txt` | prompt_lineage | Partial (usage transcript + production-system handoff) | ~7,724 | 12-chapter therapeutic audiobook generation system handoff, writer-brief decision tree, and scale assumptions — **historical lineage**, not runtime atoms |

## Pipeline concept mapping

| Source | spine (chapter order/roles) | beatmap slot | registry section | depth module | composer bridge | teacher/persona atom |
|--------|----------------------------|--------------|-------------------|--------------|-----------------|---------------------|
| Zip libraries (v2/v4) when extracted | Indirect (chapter-shaped YAML expected) | Strong (section-shaped slots) | No | Possible style/somatic layers | No | No |
| `chapter_bridges_all.md` | No | No | No | No | **Yes** | No |
| `complete_chapters_integrated.md` | Weak (generic arc) | No (stitched) | No | No | Embedded in prose | No |
| `section_01_all_chapters.md` | No | Hook-like | No | No | No | No |
| `01_hooks.py` … `05_teacherdoctrine.py` | Phase labels in hooks | Slot-family analog | No | No | No | No |
| `old_chat_pose_book_template.txt` | Schema in text | 10-section schema | No | Safety/somatic language | No | No |
| `old_claude_template_persona_stuff.txt` | No | Story arc guidance | No | Somatic pacing notes | No | No |

## Conclusion

### What to import (recommended)

- **Section scaffolds:** From extracted V4 (or V2) YAML trees under `template_expand/_extracted/{library_id}/chapter_NN/section_NN/variant_*.yaml` once archives are unpacked and paths verified.
- **Bridge text:** `chapter_bridges_all.md` — chapter conclusions and next-chapter bridges, parsed deterministically by chapter index.

### What to reference only (do not atomize in this slice)

- **`complete_chapters_integrated.md`** — fully stitched chapters; decomposing into reusable slots would duplicate work already planned for extracted YAML; use as **baseline reference** for tone/length comparisons, not as a per-slot feed.

### What not to use directly as production prose

- **`old_chat_specs/*.txt`** — prompt lineage and chat history; valuable for **schema, safety intent, and historical production handoffs**, not for direct ingestion as book atoms.
- **Python template modules (`01_hooks.py`–`05_teacherdoctrine.py`)** — treat as **code-embedded libraries** until converted or wrapped; the loader returns structured warnings instead of crashing when YAML paths are absent.

### Honest gaps

- No extracted `audiobook_template_v4/` tree on disk → **zero** legacy YAML sections load today without extraction.
- Side pipeline remains **additive**; spine, registry, and enrichment defaults are unchanged.
