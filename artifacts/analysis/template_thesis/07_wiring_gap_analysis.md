# Template Thesis Wiring Gap Analysis
# Sprint: Scenario A — April 18, 2026
# Author: Pearl_Architect in Claude Code session

## Summary

The pilot script (`scripts/pilot/run_legacy_template_packet_pilot.py`) already implements
the full wiring between `v2_somatic` loader and `section_packet_composer`. It runs.
The loader works (120/120 sections hit). The pipeline is structurally complete.

**The gaps are not missing wiring. They are three miscalibration problems in the
existing wiring that produce thin, repetitive, structurally wrong output.**

Running the pilot on `anxiety × gen_z_professionals × standard_book` produced:
- 183 sections across 12 chapters
- Average 97 words/section (target 450)
- 181 of 183 sections under 200 words (target floor ~320)
- 0 sections at 400+ words
- Chapter 1 section_01 (HOOK) uses v2_somatic `f1.yaml` text (188 words) —
  but it gets word-capped down to 110 words by `compose_section_packet`'s cap logic
- The same HOOK text (`Put your hand on your chest right now...`) repeats verbatim
  in chapters 1, 2, and 3 (the cap strips the middle, leaving identical openings)
- Section boundaries ARE visible (one paragraph per section, no raw atom dumps)
- Enrichment layer is thin (registry gaps for `anxiety` topic)

---

## 1. Where does the current render path receive chapter content?

**File:** `phoenix_v4/rendering/book_renderer.py`
**Entry point:** `render_book()` at line 1816

The production render path (`render_book`) uses a `plan` dict with:
- `plan["chapter_slot_sequence"]` — list of lists of slot types
- `plan["atom_ids"]` — flat list of atom IDs matched to slots
- `plan["prose_map"]` or resolved via `resolve_prose_for_plan()` at line 1871

The `TxtWriter.write()` at line 1469 iterates `chapter_slot_sequence`, fetches
prose from `prose_map` by `atom_id`, then calls `compose_chapter_prose()` per chapter.

**This path does NOT accept section packets directly.** It accepts a `prose_map`
keyed by `atom_id`. The pilot script bypasses this path entirely and writes its
own `book.txt` by calling `compose_section_packet()` directly per slot.

---

## 2. Where does the v2_somatic loader output section packets?

**File:** `phoenix_v4/planning/legacy_template_loader.py`
**Function:** `load_legacy_section()` at line 306

**Signature:**
```python
def load_legacy_section(
    library_id: str,          # "v2_somatic"
    chapter: int,             # 1-12
    section: int,             # 1-10
    variant_family: str = "F1",  # "F1" through "F5"
    repo_root: Optional[Path] = None,
) -> LegacyTemplateSection
```

**Output dataclass** (`LegacyTemplateSection`, line 38):
```python
@dataclass
class LegacyTemplateSection:
    text: str          # prose body (key: "content" in YAML)
    library_id: str
    chapter: int
    section: int
    variant_family: str
    word_count: int
    metadata: Dict[str, Any]  # title, role, tags if present
    warnings: List[str]
```

**Confirmed working:** `load_legacy_section("v2_somatic", 1, 1, "F1")` returns
188-word text with zero warnings. All 600 YAML files in
`template_expand2/_extracted/qaudiobook_template_v2_somatic/sections_somatic_v2/`
are accessible.

---

## 3. What is the exact gap?

There are **three gaps**, not one:

### Gap A: Word cap is crushing template content (Critical)

**File:** `phoenix_v4/rendering/section_packet_composer.py`, lines 258–266

```python
_cap = int(target_words * 1.10) if target_words and target_words > 0 else 0
if isinstance(_cap, int) and _cap > 0:
    _w = raw_text.split()
    if len(_w) > _cap:
        raw_text = " ".join(_w[:_cap]).strip()
```

The beatmap `target_words` for a HOOK slot in `standard_book` is ~320 words.
The cap is `320 * 1.10 = 352` words maximum.

The stacked packet (legacy template 188w + enrichment ~50w + teacher ~50w) totals
~288 words BEFORE the cap. This is well under 352, so the cap isn't directly
cutting it here. BUT the HOOK text itself is being word-capped by the pilot's
own `tw` variable (line 203-205 in pilot):

```python
tw = beat_slot.get("target_words") if beat_slot else target_per_section_nominal
if not isinstance(tw, int) or tw <= 0:
    tw = target_per_section_nominal  # 450
```

The beatmap target for HOOK in standard_book is ~320 words. The v2_somatic
HOOK text is only 188 words. Combined with thin enrichment, the packet reaches
only 110 words rendered because the cap then clips the enrichment's sentence fragments.

**Root cause:** The enrichment layer is thin (registry gaps for `anxiety` topic),
so the packet total is only the legacy text (~188w) minus word-cap truncation.
The template text alone is not enough — it needs the enrichment layer to be
substantive. Currently the `anxiety` topic's enrichment registry is sparse, so
most slots fall back to generic content-bank text that the deduplication then strips.

### Gap B: Same v2_somatic variant (F1) used for all 12 chapters (Medium)

**File:** `scripts/pilot/run_legacy_template_packet_pilot.py`, line 155

```python
legacy = load_legacy_section(
    args.legacy_library,
    ch_num,
    min(section_idx1, 10),
    "F1",              # ← hardcoded F1 for all chapters
    repo_root=REPO_ROOT,
)
```

The v2_somatic grid has 5 variants (F1-F5) per section. Chapter 1 section_01 F1
is `Put your hand on your chest right now...`. Chapter 2 section_01 F1 is the
same text. Chapter 3 section_01 F1 is also the same text. All 12 chapters open
with the same HOOK because F1 is hardcoded.

**Fix:** Assign variant families by chapter: Ch1→F1, Ch2→F2, Ch3→F3, Ch4→F4,
Ch5→F5, Ch6→F1, etc. This is a one-line change.

### Gap C: Pilot script is not integrated into the production render path (Low — by design)

The pilot is a standalone script that writes its own `book.txt`. The production
render path (`render_book`) uses a different mechanism (atom registry + plan dict).
The template path is intentionally a side pipeline. This is correct architecture
for the sprint — the template path should be the primary path for the build,
and the pilot script IS the template path.

The "production render path" mismatch is not a bug — the pilot IS the production
template render path. It just needs to be hardened.

---

## 4. What files need to change and what changes are needed?

### Change 1: Rotate variant families across chapters (1 line)

**File:** `scripts/pilot/run_legacy_template_packet_pilot.py`, line 155

```python
# BEFORE:
legacy = load_legacy_section(
    args.legacy_library, ch_num, min(section_idx1, 10), "F1", repo_root=REPO_ROOT
)

# AFTER:
variant_families = ["F1", "F2", "F3", "F4", "F5"]
variant_family = variant_families[(ch_num - 1) % len(variant_families)]
legacy = load_legacy_section(
    args.legacy_library, ch_num, min(section_idx1, 10), variant_family, repo_root=REPO_ROOT
)
```

This eliminates verbatim repetition of the same template text across chapters.

### Change 2: Add a template-only mode that uses template text as primary content (Core fix)

The current stacking order in `compose_section_packet` is:
`bridge → journey_intro → legacy_template → enrichment → teacher_atom → depth`

The legacy template is layer 3 (scaffold). The enrichment layer (layer 4) is
supposed to provide the primary substance. For `anxiety` topic, the enrichment
registry is sparse — so packets are thin.

**Option A (Recommended for Scenario A):** Use the template text AS the primary
content layer and skip the enrichment dependency. Increase the variant
selection to cycle through F1-F5 AND chapter-appropriate sections to maximize
diversity.

**Implementation:** In the pilot, skip the enrichment peek and pass only the
template text + teacher atom. Set `expand_thin_sections=True` to let
Pearl_Writer expand sections below target.

```python
# In the pilot main loop, replace the enrichment assembly block:
packet = compose_section_packet(
    chapter_index=ch_num,
    section_index=section_idx1,
    section_type=slot.slot_type,
    target_words=tw,
    spine_context=spine_context,
    beatmap_slot=beat_slot,
    enrichment_slot=None,          # Remove enrichment dependency
    legacy_template_section=legacy_dict,
    bridge_text=bridge_text,
    quality_profile="draft",
    exercise_phase=ex_phase,
    teacher_atom_content=teacher_layer,
    expand_thin_sections=True,     # Let Pearl_Writer fill gaps
)
```

**Option B (Lighter):** Fix the enrichment registry coverage for `anxiety` topic
so the stacking works as intended. This is the correct long-term fix but requires
registry population work (2-3 week task).

### Change 3: Use chapter-appropriate section indices for somatic grid (Enhancement)

The SOMATIC_10_SLOT_GRID maps `section_01`=HOOK through `section_10`=INTEGRATION.
The pilot correctly passes `min(section_idx1, 10)` as section index. However,
the beatmap may generate >10 slots per chapter (enriched chapters have depth
slots pushing count to 12-15). The `min(section_idx1, 10)` cap means slots 11+
all reuse section_10 (INTEGRATION) template text.

**Fix:** Only load template text for slots 1-10. For depth slots beyond 10, pass
`legacy_dict=None` and rely on depth_module content only.

---

## 5. Minimal viable wiring

The smallest change that produces a book.txt with visible section structure and
non-repeated template text:

**Step 1:** Apply Change 1 (variant rotation, 3 lines) in the pilot script.
**Step 2:** Verify by running the pilot and checking that chapters 1-5 have
different HOOK text.

That's it for a structurally correct output. The word count will still be low
(~17k total vs. 54k target for standard_book) but sections will be:
- In order (HOOK → SCENE → REFLECTION → EXERCISE × 2 → TEACHER_DOCTRINE → REFLECTION → EXERCISE × 2 → SCENE → INTEGRATION)
- Non-repeating across chapters
- Legible (each section is one coherent passage)

**To reach word count target:** Add Change 2 with `expand_thin_sections=True`.
This triggers Pearl_Writer expansion for sections below 60% of their word target.
Note: Pearl_Writer requires LLM API access (Qwen or Claude). If no LLM is
available, accept the thin output and flag it as a content-coverage gap.

---

## Pilot verification (April 18, 2026)

Run: `python3 scripts/pilot/run_legacy_template_packet_pilot.py`

Results:
- Output: `artifacts/pilot/scenario_a_sprint_20260418/book.txt`
- 183 sections, 12 chapters
- 120 sections got legacy template text (loader works, 100% hit rate for 10-slot chapters)
- Section boundaries ARE visible — no raw atom pool dumps
- No `## HOOK v01 --- ---` scaffolding in output
- Critical problem: same HOOK text repeats chapters 1-3 (variant F1 hardcoded)
- Critical problem: avg 97 words/section (target 450) — enrichment registry sparse

The pipeline wiring is complete. The output needs variant rotation and enrichment coverage.

---

## Go/no-go trigger

The 14-17 day build is authorized when:
1. The operator reads `config/source_of_truth/book_templates/anxiety_gen_z_professionals_overwhelm_v1.yaml`
   and confirms the 12-chapter arc reads like a coherent book
2. Change 1 (variant rotation) is applied and verified: chapters 1-5 have distinct HOOK text
3. Decision is made on enrichment strategy: registry population (Option B, 2-3 weeks)
   vs. Pearl_Writer expansion (Option A, available now with LLM access)

The structural wiring exists. The content diversity and density are the remaining gaps.
