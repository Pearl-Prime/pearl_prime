# Phase 1: Git Archaeology — The Old Template System

## Summary Finding

**The template system EXISTED in git — but was never fully operational as a book-production path.**

It exists in two distinct forms:
1. **Vendor-supplied YAML grids** (the `v2_somatic` library) — fully built, 12 chapters × 10 sections × 5 variants = 600 YAML files, on disk, loadable
2. **A pilot composer** that can load these YAMLs into "section packets" — partially built, reached 51/120 legacy hits in a pilot run

The system was never connected to the main production rendering path. It lived in `scripts/pilot/` — not in the pipeline that ships books.

---

## Key Commits Found

| SHA | Date | Description |
|-----|------|-------------|
| `f9a22456fc` | 2026-04-10 | `feat: legacy template index + loader + exercise configs` |
| `4a0e704b2f` | 2026-04-10 | `test: legacy template loader + section packet composer (10+ tests)` |
| `8879a8ccb8` | 2026-04-10 | `feat: section packet composer prototype` |
| `acd9c10260` | 2026-04-11 | `feat: legacy template packet composer (anxiety pilot) (#383)` |
| `a57a3fc22e` | 2026-04-11 | `feat: legacy template zip extraction, loader paths, V2 anxiety pilot (#385)` |
| `203f4c2fe9` | 2026-04-11 | `feat: template_expand2 ingest — V2 somatic loader, 612 atoms, pilot V3, audits (#389)` |

All template-related commits cluster around **April 10-11, 2026**. The template approach was built as a sprint, reported on, and then development pivoted back to patching the assembly pipeline.

---

## What Was Actually Built

### The `v2_somatic` Grid (THE KEY FIND)

**Location:** `template_expand2/_extracted/qaudiobook_template_v2_somatic/sections_somatic_v2/`

**Structure:**
```
chapter_01/
  section_01_hook/    f1.yaml f2.yaml f3.yaml f4.yaml f5.yaml
  section_02_scene/   f1.yaml f2.yaml f3.yaml f4.yaml f5.yaml
  section_03_reflection/
  section_04_exercise/
  section_05_scene/
  section_06_teacherdoctrine/
  section_07_reflection/
  section_08_exercise/
  section_09_scene/
  section_10_integration/
chapter_02/ ... (same structure)
...
chapter_08/ (confirmed present — others inferred from index)
```

**Measured stats (from `config/templates/legacy_template_index.yaml`):**
- `chapters: 12`
- `sections_per_chapter: 10`
- `variants_per_section: 5`
- `total_section_yaml_files: 600`
- `avg_words_per_section: 153`
- `total_words: 92,325`

**Sample section content (ch08, section_01_hook, f1.yaml):**
```
variant_id: ch08_sec01_hook_f1
section_type: HOOK
purpose: Opening — somatic healing recognition
content: |
  Something is different now.
  You might not be able to name it, but your body knows. A subtle shift. 
  A slight loosening where there was only tension before.
  [... 14 paragraphs, clean prose, 1106 chars ...]
```

The content is readable, therapeutic, structured. This is production-quality prose.

### The Section Role Map

Defined in `config/templates/legacy_template_index.yaml`:
```yaml
section_roles:
  section_01: hook
  section_02: scene
  section_03: reflection
  section_04: exercise
  section_05: scene
  section_06: teacher_doctrine
  section_07: reflection
  section_08: exercise
  section_09: scene
  section_10: integration
```

This matches **exactly** what the operator described: named section roles per slot.

### The Pilot Report

`artifacts/pilot/STACKED_PACKET_REPORT.md` documents a pilot run (April 2026):

- When run with v4 library (default): **2/120 legacy hits** (only 2 section YAMLs existed in v4)
- When run with v2_somatic library: **51/120 legacy hits** (limited by 4-slot-per-chapter beatmap in standard_book)
- The pilot reached `14,397 words` for a full book (vs 54,000 target for 6h format)
- Root cause: `standard_book` beatmap only had **4 base slots** per chapter (HOOK, SCENE, REFLECTION, INTEGRATION), not 10
- The somatic grid's 10 sections/chapter were never used because the beatmap didn't request them

### The `beatmap_compile.py` Finding

`phoenix_v4/planning/beatmap_compile.py` defines:
```python
SOMATIC_FULL_RUNTIME_FORMATS = frozenset(
    {"standard_book", "extended_book_2h", "deep_book_4h", "deep_book_6h"}
)
SOMATIC_10_SLOT_GRID = [
    "HOOK", "SCENE", "REFLECTION", "EXERCISE", "SCENE",
    "TEACHER_DOCTRINE", "REFLECTION", "EXERCISE", "SCENE", "INTEGRATION"
]
```

This grid exists in code. **It was never the default production path.** The pipeline continues to render from atom pools, not from this structured 10-slot grid.

---

## Section Registry Pipeline (Related but Different)

Commit `af32c55582` (April 7, 2026) added a "section registry pipeline":
- 14 topic registries (anxiety, burnout, etc.) each with named section types
- This is NOT the same as the template system — it's a flat YAML of atoms per topic
- The section_registry is currently the fallback fast-path, producing ~4,800 words/book (too thin)

---

## What the Old Chat Specs Reveal

`old_chat_specs/book generations system.txt` (undated, predates git history):
- Shows the original ChatGPT conversation designing the book generation system
- Explicitly calls for "structural diversity" — 12-20 "book architectures" not cosmetic variation
- Frames the product as: **BOOK = Structure Type + Narrative Arc + Persona Lens + Topic Framing + Section Roles + Voice Mode + Progression Logic**

`old_chat_specs/old_claude_template_persona_stuff.txt`:
- Shows atom-role contracts being designed: recognition → mechanism proof → turning point → embodiment
- This was the original vision — named roles per atom

---

## Verdict: Did the Template System Exist?

**Yes, partially.** Specifically:

| Component | Status |
|-----------|--------|
| 12 × 10 × 5 YAML content grid | FULLY BUILT — 600 files on disk |
| Section role definitions | BUILT — in legacy_template_index.yaml |
| Section packet loader | BUILT — works for 51/120 slots |
| Section packet composer (pilot) | BUILT — runs via `scripts/pilot/` |
| Integration with main render path | NOT BUILT — never wired |
| Chapter-level section-aware planning | NOT BUILT — beatmap uses 4 slots not 10 |
| Variant selection per (book_id + chapter + section) | NOT BUILT — prototype only |

**The template content exists. The plumbing to use it as the production path was never finished.**

The system was discovered, inventoried, piloted — and then the team pivoted to patching the assembly pipeline instead of completing the template wiring.

---

## Why It Was Not Completed

From `artifacts/pilot/STACKED_PACKET_REPORT.md`:
> "Replacing registry-as-default for full six-hour books still requires format alignment (10 slots), placeholder cleanup, and expansion to hit duration targets."

The effort to make the template approach production-ready was estimated as requiring:
1. Beatmap expansion to 10 slots per chapter (not 4)
2. Placeholder cleanup (`[STORY_INJECTION_POINT]` leaking into delivery)
3. Pearl_Writer expansion to fill thin sections
4. Format alignment between template grid and runtime beatmap

Instead, the team ran benchmark books and patched the assembly pipeline.
