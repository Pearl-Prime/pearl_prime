# Story Bank Audit — 2026-04-25

## Coverage of `atoms/{persona}/{topic}/STORY/CANONICAL.txt`

170 of 195 (persona × topic) cells covered (87.2%).

| persona | covered cells | typical variants |
|---|---|---|
| corporate_managers | 15/15 | 20 |
| entrepreneurs | 15/15 | 20 |
| first_responders | 15/15 | 20 |
| gen_alpha_students | 15/15 | 20 |
| gen_x_sandwich | 15/15 | 20 |
| gen_z_professionals | 15/15 | 20 (anxiety has 33) |
| healthcare_rns | 15/15 | 20 |
| millennial_women_professionals | 15/15 | 20 |
| tech_finance_burnout | 15/15 | 20 |
| working_parents | 15/15 | 20 |
| gen_z_student | 12/15 | 4–6 (LOW; needs author) |
| educators | 8/15 | 20 |
| **midlife_women** | **0/15** | — (whole persona empty) |

### Strong cells: 167 of 170 (≥5 variants each)
### Sparse cells (<5 variants): 3
- gen_z_student × courage (4)
- gen_z_student × grief (4)
- gen_z_student × somatic_healing (4)

### Empty cells: 25
- midlife_women × all 15 topics (not authored at all)
- educators × {burnout, financial_anxiety, imposter_syndrome, overthinking, sleep_anxiety, social_anxiety, somatic_healing} (7)
- gen_z_student × {compassion_fatigue, financial_anxiety, financial_stress} (3)

## Pipeline behavior verified

### Before this PR
- `_load_persona_atoms()` correctly parses `atoms/{persona}/{topic}/STORY/CANONICAL.txt` and exposes 20-variant pools as `persona_atoms["STORY"]`.
- `enrichment_select.py` calls `persona_atoms.get(slot_type)` to source content per slot.
- `SOMATIC_10_SLOT_GRID` in `phoenix_v4/planning/beatmap_compile.py` lists slot types per chapter section. **It did NOT include STORY** — section_02 was set to SCENE.
- Result: 859 STORY atoms loaded into memory but never selected. The grid emitted only HOOK / SCENE / REFLECTION / EXERCISE / TEACHER_DOCTRINE / INTEGRATION slot types.

### After this PR
- `SOMATIC_10_SLOT_GRID[1]` changed from `"SCENE"` to `"STORY"`.
- Aligns the runtime grid with `default_slot_definitions: [HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION]` in `config/format_selection/format_registry.yaml`.
- STORY slot at section_02 now selects from `persona_atoms["STORY"]` (the 859-file bank) plus optional teacher / story_planner additions.
- SCENE retained at sections 5 and 9 for non-character anchors and scene_recognition content.

### Sanity test
Single-book render: `gen_z_professionals × financial_stress × overwhelm × F006`, draft profile.

```
slot_types: HOOK 12, STORY 12, SCENE 24, REFLECTION 24, EXERCISE 24, TEACHER_DOCTRINE 12, INTEGRATION 12
chapter 1 slot 1: STORY  source=persona_atom
quality:
  bestseller_craft  PASS  overall_score=0.5462
  ei_v2             PASS  composite=0.6515  (was 0.6321 pre-patch)
  book_pass         PASS
  transformation    PASS
  memorable_lines   WARN  chapters_with_two_or_more_quotable_lines=10/12
  chapter_flow      FAIL  (corpus-wide gap, not specific to this change)
```

Sample STORY content rendered into chapter 1: "He didn't plan to stop. He just did — halfway through the hustle culture, mid-sentence, with the bills and breathing pressing against his ribs like a hand. Nobody noticed the pause. He recovered in two seconds. But those two seconds held more truth than the entire side hustle."

This is from a STORY/CANONICAL.txt variant — character-driven prose where prior renders had generic 2nd-person scene-anchor loops.

## Two complementary story systems

| System | Path | Files | Loaded by | Purpose |
|---|---|---|---|---|
| **Per-persona-topic STORY** (the big bank) | `atoms/{persona}/{topic}/STORY/CANONICAL.txt` | **859** | `_load_persona_atoms` → `persona_atoms["STORY"]` | Static narrative variants, tagged by `mechanism_depth` / `identity_stage` / `cost_type` / `cost_intensity`. Now consumed at section_02 STORY slot. |
| **Character-narrative story_atoms** (the small bank) | `story_atoms/{persona}/anchored/{topic}/{engine}/{arc_pos}/micro/v*.txt` | 30 → 74 (this PR) | `_find_story_atoms_content` via `story_planner.build_story_schedule` | Arc-position-aware character vignettes (Priya, Marcus, Maya, etc.). Injected via `[STORY_INJECTION_POINT]` markers within SCENE/STORY content. |

Both layers stack additively per slot via the existing enrichment pipeline.

## Sparse-cell handling

The 25 empty (persona × topic) cells will hard-fail with the existing CONTENT GAP message when allocated. The QA wrapper's pre-filter already drops `no_master_arc` cells; a parallel STORY-coverage pre-filter is the next-easiest mitigation. Authoring `midlife_women` and missing `educators` STORY atoms is the long-term fix; out of scope for this PR.

## Files in this PR

| Category | Count | Path |
|---|---|---|
| Authoring inputs | 3 | `SOURCE_OF_TRUTH/story_atoms/{character_roster, scene_injection_map, story_atom_tier_templates}.yaml` |
| Character story atoms | 44 | `story_atoms/gen_z_professionals/anchored/anxiety/overwhelm/{recognition, mechanism_proof, turning_point, embodiment}/micro/v*.txt` |
| Grid patch | 1 | `phoenix_v4/planning/beatmap_compile.py` (1-line slot type change + canonical-spec comment) |
| Audit | 1 | `docs/STORY_BANK_AUDIT_2026-04-25.md` (this file) |

49 files total.
