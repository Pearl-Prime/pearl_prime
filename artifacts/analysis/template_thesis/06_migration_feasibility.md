# Phase 6: Migration Feasibility

## What "Migration" Means

Not a rewrite. The template approach reuses:
- The existing `v2_somatic` 600-file YAML grid (already on disk)
- The existing `beatmap_compile.py` with `SOMATIC_10_SLOT_GRID` already defined
- The existing `legacy_template_loader.py` (already working: 120/120 section files in pilot)
- The existing Pearl_Writer thin-section expansion runtime (PR #398, already merged)
- The existing chapter title / arc / spine system

What changes:
- The beatmap default for `standard_book` shifts from 4 slots → 10 slots
- Section packet composer becomes the primary content path (not atom pool)
- Chapter composer assembles section packets instead of atom pool picks

This is a wiring job, not an architecture rewrite.

---

## Per-Component Migration Plan

### Component 1: Template Schema + Example Template
**Effort: 2 days**

Deliverable: One complete 12-chapter template YAML for anxiety × gen_z_professionals × overwhelm, with real section jobs described for each chapter.

This is the fail-fast gate. If the operator reads this outline and says "that reads like a book," the full build is authorized. If the operator says "this doesn't feel right," 2 days saved 3 weeks.

Tasks:
- Write 12 chapter outlines, each naming section jobs 01-10 with chapter-specific intent
- Define topic-specific constraints (e.g., "ch04 mechanism_explanation must cover polyvagal not cognitive reframing")
- Define persona-specific variants (e.g., "section_02_scene for gen_z_professionals uses workplace/commute/WFH locations")

No code required.

---

### Component 2: Section-Variant Schema + 3 Variants Per 8 Sections for One Template
**Effort: 3 days**

Deliverable: Hand-authored (or Pearl_Writer-authored) YAML variants for one complete template, one topic, one persona.

The `v2_somatic` content already covers this for somatic healing — but it's topic-agnostic. For anxiety × gen_z_professionals, we need:
- Persona-voiced section_02_scene variants (workplace/commute settings)
- Topic-specific section_06_teacherdoctrine (nervous system × productivity culture)
- Topic-specific section_04_exercise (regulation practices for desk workers)

The `v2_somatic` hook variants are already genre-appropriate and can be used directly for section_01_hook with minimal editing.

Tasks:
- Audit existing v2_somatic content for anxiety × gen_z_professionals fit
- Write/rewrite sections that don't fit (estimated: 30-40% need persona voicing)
- Use Pearl_Writer expansion runtime for thin sections
- Target: 320 words/section minimum, 10 sections × 12 chapters = 120 sections × 3 variants = 360 YAML files

---

### Component 3: Section-Aware Spine Compiler Refactor
**Effort: 3-5 days**

Current: `beatmap_compile.py` nominally supports 10 slots but `standard_book` defaults to 4 slots.

Change needed:
```python
# Current (implicit 4-slot default)
SOMATIC_FULL_RUNTIME_FORMATS = frozenset(
    {"standard_book", "extended_book_2h", ...}
)

# After: standard_book uses SOMATIC_10_SLOT_GRID as default
# Beatmap slot → section YAML path (not atom pool)
```

Tasks:
- Extend `beatmap_compile.py` to map slot → section YAML path (not just slot type)
- Wire `legacy_template_loader.load_legacy_section()` as primary content source for each slot
- Fall back to atom pool only when section YAML unavailable
- Preserve existing atom path for topics without template content

This is an extension, not a rewrite. The loader already works (120/120). The beatmap already has the slot definitions. The connection between them is what's missing.

---

### Component 4: Section-Job Validators
**Effort: 2 days**

New gates to add to the regression museum:

```python
def gate_chapter_opens_with_hook(chapter: str) -> bool:
    """chapter must start with hook text, not exercise/reflection/scene"""

def gate_mechanism_before_exercise(chapter_plan: ChapterPlan) -> bool:
    """section_06 index must precede section_08 index"""

def gate_integration_is_final_section(chapter_plan: ChapterPlan) -> bool:
    """section_10 must be the last section"""

def gate_no_placeholder_leakage(chapter: str) -> bool:
    """[STORY_INJECTION_POINT] must not appear in delivered text"""
```

These validators are cheap to write and permanently block regressions.

---

### Component 5: Render Path Refactor
**Effort: 2-3 days**

Current: `compose_from_enriched_book()` concatenates slot bodies in beatmap order.

Change needed: Section packets are assembled with bridge sentences, not raw concatenation.

The `compose_chapter_prose()` path already does thesis-threaded composition. The refactor wires section packet content through this path:

- Section_01_hook → no bridge before it
- Section_02_scene → bridge from hook to scene
- Section_06_teacherdoctrine → bridge from scene to mechanism
- Section_10_integration → closes with takeaway sentence

Bridge generation already exists (205 zh-TW templates, English pool). This is a routing change.

---

### Component 6: Tests + Museum Extension
**Effort: 2 days**

- Extend `tests/test_legacy_template_loader.py` to test 10-slot loading (currently tests subset)
- Add section-job gate tests to regression museum
- Add "template-rendered chapter" fixture for CI
- Verify no placeholder leakage in rendered output

---

## Build Timeline

| Component | Effort | Dependency |
|-----------|--------|-----------|
| 1. Template schema + example YAML | 2 days | None — starts immediately |
| **[OPERATOR GATE]** | 0 days | Operator reads the YAML outline |
| 2. Section-variant content | 3 days | Component 1 approved |
| 3. Spine compiler refactor | 3-5 days | Component 2 (needs content to test against) |
| 4. Section-job validators | 2 days | Component 3 (validates the new path) |
| 5. Render path refactor | 2-3 days | Components 2+3 |
| 6. Tests + museum | 2 days | Components 3-5 |
| **Total** | **14-17 working days** | |
| **In calendar weeks** | **2.5-3.5 weeks** | |

---

## Compare: "Continue Patching Assembly Pipeline"

| Metric | Template Build | Assembly Patching |
|--------|---------------|-------------------|
| Effort estimate | 2-3 weeks | Unbounded |
| Evidence of convergence | First coherent book in 3 weeks | 0 after 12+ sprint cycles |
| Chapter flow gate failures | Predicted: 0/12 | Current: 12/12 every run |
| Structural coherence | Guaranteed by design | Emergent, not achieved |
| Cost of failure | 3 weeks before knowing | Running cost, indefinite |
| Atom pool asset reuse | Full (atoms still used for fallback) | Full |
| What "done" looks like | Operator reads a coherent book | Gate passes; coherence unknown |

---

## What the Template Build Does NOT Break

- The atom pool content remains valid — fallback path when no template YAML
- The arc/spine/knob system remains in place — chapter titles, thesis, bestseller structure assignments unchanged
- The Pearl_Writer runtime remains in place — fills thin sections regardless of content source
- The regression museum remains in place — gates apply to template output too
- The section registry fast-path remains available — can be run for comparison (Scenario C)

The template build is **additive to the existing stack, not a replacement**.

---

## The Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| v2_somatic chapters 3-7, 9-12 have gaps (archives listed as `status: missing`) | Medium | Audit zip archives; Pearl_Writer fills gaps |
| Template content doesn't fit anxiety × gen_z persona | Low-Medium | Operator reads YAML outline before any code |
| 10-slot beatmap produces too many words (overrun) | Low | Word cap already exists in render path |
| Template content is too generic (no persona voice) | Medium | Component 2 explicitly adds persona-voiced variants |
| 3 weeks is underestimated | Low-Medium | Components 1+operator gate identifies this in 2 days |

The fail-fast gate eliminates the catastrophic risk: if the template outline doesn't read like a coherent book, 2 days are lost, not 3 weeks.
