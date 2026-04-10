# Depth module protocol — EnrichmentSelect (spec only)

**Status:** Architecture and data contract. **No code changes** in `phoenix_v4/planning/enrichment_select.py` in this workstream — implementation is a follow-up.

**Authority inputs:**

- `config/depth/depth_module_map.yaml` — function → sources, counts, topic overrides  
- `phoenix_v4/planning/enrichment_select.py` — current waterfall (teacher → persona → practice library → registry)  
- `phoenix_v4/planning/beatmap_compile.py` — per-slot `target_words`  
- `artifacts/audit/depth_gap_analysis.md` — measured pilot gap (new vs baseline)

---

## When to request depth modules

Let:

- `target_word_count` = sum of `BeatmapSlot.target_words` for the chapter (from beatmap / `budget.json` pattern).  
- `actual_word_count` = sum of `EnrichedSlot.actual_words` for the chapter after the initial waterfall pass.  
- `deficit = target_word_count - actual_word_count`.

**Trigger:**

```
IF deficit > 100:
    Enter depth module pass (ordered, deterministic).
```

Optional guardrails (implementation detail): cap total added words per chapter (e.g. `deficit` clamped to `min(deficit, 1200)`) and stop when `deficit <= 100`.

---

## Phase resolution (early / mid / late)

For a book with `chapter_count` chapters (pilot used 12):

| Phase | Chapter index range | Label |
|-------|----------------------|--------|
| early | 1 … ceil(chapter_count/3) | `early` |
| mid | next … floor(2*chapter_count/3) | `mid` |
| late | remainder | `late` |

For `chapter_count = 12`: early = 1–4, mid = 5–8, late = 9–12.

---

## Selection order

1. **Topic** → load `topic_overrides.{topic_id}` from `depth_module_map.yaml`.  
2. **Phase** → choose `depth_priority_early`, `depth_priority_mid`, or `depth_priority_late`.  
3. **Iterate** priority list in order. For each `depth_module` id:  
   - **Affinity:** if `chapter_affinity` is not `all` and current chapter ∉ affinity → skip.  
   - **Bans:** if module is in `banned_early` and chapter ∈ early phase → skip; if `banned_chapters` lists this chapter → skip.  
   - **Topic restriction:** if module has `topic_restriction` and `topic_id` not listed → skip.  
   - **Knobs:** if `compatible_knobs` present, compare to chapter/slot metadata from `ShapedSpine` / `BeatmapSlot` (e.g. `emotional_temperature`, `pacing_profile`, `mechanism_depth`) — skip on mismatch.  
4. **Sources:** for the first depth module that passes gates, pull material in **source order** listed under `depth_modules.{id}.sources` (e.g. teacher_atom → persona_atom → registry_variant → practice_library).  
5. **Apply** until `deficit <= 100` or all sources for that module are exhausted; then move to the next priority module.  
6. **Audit:** append to `enrichment_audit` (or a new `depth_module_audit` array) which modules fired, which source paths, and word counts added.

---

## What to request (mapping)

| Depth module | Typical pull |
|--------------|--------------|
| `recognition_depth` | Extra HOOK/SCENE variants (registry F2–F5), or additional persona blocks |
| `mechanism_depth` | REFLECTION/COMPRESSION/TEACHING teacher atoms; longer registry REFLECTION variants |
| `story_scene` | STORY/SCENE teacher or persona; registry SCENE |
| `consequence_exposure` | REFLECTION/STORY with cost language; registry REFLECTION |
| `somatic_detail` | EXERCISE teacher atoms; `SOURCE_OF_TRUTH/exercises_v4/approved`; practice library composed text |
| `practice_scaffold` | `config/pearl_practice/component_templates.yaml` slices + `aha_noticing` / `integration` phoenix standards |
| `bridge_transition` | THREAD/INTEGRATION/PIVOT teacher atoms; `bridge` pool |
| `integration_landing` | INTEGRATION teacher atoms; `integration_phoenix_standard.yaml` |
| `witnessing_presence` | PERMISSION/REFLECTION; grief registry long variants |
| `persona_specificity` | Persona CANONICAL blocks under `atoms/{persona}/{topic}/` |
| `teacher_voice` | COMPRESSION/TEACHING/HOOK/REFLECTION teacher atoms; TEACHER_DOCTRINE registry |

---

## Where to find it (canonical paths)

All paths are **repo-relative** and verified in `config/depth/depth_module_map.yaml` under `repo_paths` and `inventory_snapshot`.

- Teacher atoms: `SOURCE_OF_TRUTH/teacher_banks/{teacher_id}/approved_atoms/{SLOT_TYPE}/*.yaml` (field `body` in YAML).  
- Persona: `atoms/{persona_id}/{topic_id}/{SLOT_TYPE}/CANONICAL.txt` and engine subfolders merged into STORY per `registry_resolver._load_persona_atoms`.  
- Registry: `registry/{topic_id}.yaml` — `variants` lists F1–F5.  
- Practice library: `SOURCE_OF_TRUTH/practice_library/inbox/*_PRODUCTION_READY.json` via `practice_library_loader`.  
- Components: `config/pearl_practice/component_templates.yaml`.  
- Phoenix standards: `SOURCE_OF_TRUTH/exercises_v4/aha_noticing_phoenix_standard.yaml`, `integration_phoenix_standard.yaml`.

---

## Logging contract

Extend `enrichment_audit` (future implementation) with:

```yaml
depth_module_pass:
  chapter: 4
  deficit_before: 420
  deficit_after: 85
  modules_applied:
    - module: mechanism_depth
      sources:
        - { type: registry_variant, variant_id: ch04_sec03_reflection_f3, words_added: 180 }
    - module: bridge_transition
      sources:
        - { type: teacher_atom, atom_id: ahjan_THREAD_012, words_added: 42 }
```

---

## Governance reminder

Before merging any PR that wires this into production: run `gh pr diff <number> --stat | tail -1` and confirm **deletions ≤ 50 files** per `CLAUDE.md` non‑negotiable rule.
