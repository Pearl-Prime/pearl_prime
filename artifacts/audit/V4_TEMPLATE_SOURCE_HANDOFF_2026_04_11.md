# V4 Template Source Handoff — 2026-04-11

## Executive Summary

The repository contains strong evidence that an older Phoenix Omega template system existed, but the actual CSV/JSON template source the user is asking about is not present in this checkout.

The closest referenced file is:

```text
SOURCE_OF_TRUTH/data/templates/phoenix_omega_book_template.csv
```

That path appears repeatedly in historical chat/spec files, but `rg --files` does not show it in the current repo. The only template CSVs found by tracked-file search were unrelated:

```text
config/payouts/fill_template.csv
artifacts/catalog/sales_data_template.csv
```

The repo does contain `persona_topic_variables.schema.yaml`, which is explicitly described as a variable schema for hydrating 12-chapter therapeutic audiobook templates. That schema is real and present, but it is not the missing template CSV itself.

## What We Found

### 1. Historical documentation confirms the old template model

`talp/SYSTEMS_DOCUMENTATION.md` and `archive/SYSTEMS_DOCUMENTATION (3).md` both describe the old model as:

```text
12 chapters × 10 sections × 3-5 variations = combinatorial permutation
```

The same section says the old fixed-template model was replaced because it created formulaic books and duplication risk at scale.

Important excerpt location:

```text
talp/SYSTEMS_DOCUMENTATION.md
Section 19.1 — Why Not Templates
```

Interpretation:

- The phrase the user remembered is real.
- It is described as the old model, not the current canonical spine path.
- It was considered a source of formulaic output unless upgraded with stronger section prose and better composition.

### 2. Historical notes name the missing CSV directly

`old_chat_specs/self help angles.txt` says Phoenix Omega used:

```text
SOURCE_OF_TRUTH/data/templates/phoenix_omega_book_template.csv
```

It describes the CSV shape as:

```text
chapter, order, section_key, template_text
```

It also describes the engine as deterministic and substitution-only:

```text
fixed 12 chapter templates and persona/topic variables (no prose generation)
```

This file also references:

```text
del_newest_intake_prose/HANDOFF_DOC.md
del_newest_intake_prose/TEMPLATE_ENGINE_SPEC.md
del_newest_intake_prose/chapter_01_template.md through chapter_12_template.md
del_newest_intake_prose/persona_topic_variables.schema.yaml
```

Those `del_newest_intake_prose/*` files were not found in the current checkout by tracked-file search. The root-level `persona_topic_variables.schema.yaml` does exist.

### 3. Historical notes mention fixed / annotated template variants

`old_chat_specs/book generations system.txt` repeatedly references:

```text
SOURCE_OF_TRUTH/data/templates/phoenix_omega_book_template.csv
Dels/phoenix_omega_book_template_FIXED.csv
Dels/phoenix_omega_book_template_ANNOTATED.csv
phoenix_omega_book_template_v3.csv
```

It also references the generator command:

```text
python3 SOURCE_OF_TRUTH/tools/generate_phoenix_omega_book_scoped.py \
  --template SOURCE_OF_TRUTH/data/templates/phoenix_omega_book_template.csv \
  --values gen_z_depression_values_CANONICAL.yaml \
  --output qa_gen_z_depression_CANONICAL_FIXED_TEST.md
```

Interpretation:

- There was likely a real CSV in an older `ab_auto` or `Dels` working tree.
- It may have had fixed, annotated, and v3 variants.
- It is not currently available as a tracked file in this repo checkout.

### 4. A variable schema is present and important

The repo has:

```text
persona_topic_variables.schema.yaml
```

The header says:

```text
PERSONA × TOPIC VARIABLE SCHEMA v1.0
Single source of truth for all chapter template hydration
Defines all variables required to hydrate 12-chapter therapeutic audiobook templates
```

This supports the template-hydration architecture, but it does not supply the section prose itself. It is a variable contract, not the book body template.

### 5. The current spine files are not the same as the old template CSV

Current `config/spines/*.yaml` files exist, but they are journey/role skeletons. For example, `config/spines/anxiety_spine.yaml` has 12 chapters, but Chapter 1 only requires:

```text
HOOK, SCENE, REFLECTION
```

That is not the old "10 sections × 3-5 variations" template structure.

Interpretation:

- Current spines define family-specific journey logic.
- The missing old CSV likely defined a fuller deterministic prose template.
- These should not be treated as the same artifact.

## Answer To The User's Core Question

The user asked whether the V4 template with 12 chapters, 7-10 sections per chapter, and 3-5 variations per section is a six-hour book.

Answer:

Not automatically.

It can be a six-hour architecture if:

- all sections are included, not just selected sparsely
- each section expands to a substantial prose passage
- section word budgets are roughly 450-650 words on average
- variations are used for diversity or alternate book builds, not blindly concatenated in the same manuscript

Math:

```text
deep_book_6h target: 52,000-58,000 words
12 chapters: about 4,300-4,800 words per chapter
12 chapters × 8 sections average × 550 words average = 52,800 words
```

So:

- `12 × 8 sections × ~550 words` can reach six hours.
- `12 × 8 short slots × 80-150 words` will not.
- `3-5 variations` normally means alternate variants, not all included content.

## Key Architecture Lesson

The old fixed-template model had a scale problem, but it also points to the missing piece in the new spine pipeline:

```text
section-level authored prose with real word budgets
```

The new spine pipeline now has good journey logic, knobs, beatmaps, enrichment, and depth passes. What it still lacks for six-hour output is a long-form section composer that can turn each section role into a substantial passage.

The missing old CSV/template system may contain useful section prose patterns, but it should not be restored blindly. It should be mined and converted into a governed section library.

## Recommended Next Work

### P0 — Recover or Reconstruct the Old Template Source

Search outside this checkout for:

```text
SOURCE_OF_TRUTH/data/templates/phoenix_omega_book_template.csv
Dels/phoenix_omega_book_template_FIXED.csv
Dels/phoenix_omega_book_template_ANNOTATED.csv
phoenix_omega_book_template_v3.csv
del_newest_intake_prose/
ab_auto/
```

Likely old-machine path from historical notes:

```text
/Users/geoffreymalone/Documents/augment-projects/ab_auto/
```

If recovered, do not merge it directly into production. First inspect:

- row count
- chapter coverage
- section_key taxonomy
- template_text length
- unresolved variable tokens
- validation rules
- whether the fixed or annotated variant is the correct source

### P1 — Convert Old Template Into a Section Library

If the CSV is recovered, transform it into a governed structure like:

```text
config/sections_v4/<topic_family>/<chapter>/<section_key>/<variant_id>.yaml
```

Each section should carry:

```yaml
chapter: 1
section_order: 1
section_key: hook
section_type: HOOK
variant_family: F1
target_words: 450
template_text: ...
allowed_topics: [...]
forbidden_topics: [...]
requires_variables: [...]
```

Do not collapse it into atoms. It should become a long-form section/prose library that `compose_chapter_prose` can consume.

### P2 — Add 6-Hour Section Budgets

Add explicit budgets for `deep_book_6h`:

```text
book target: 52,000-58,000 words
chapter target: 4,300-4,800 words
section target: 450-650 words if 7-10 sections/chapter
```

The current spine path should not be expected to reach six hours unless this budget is wired into the section composer.

### P3 — Integrate With Current Spine Pipeline Safely

Use the current pipeline layers:

```text
Spine Select
Knob Apply
Beatmap Compile
Enrichment Select
Depth Pass
Section Compose
Book Render
Quality Gate
```

The old template material should enter at `Section Compose`, not replace the spine. The spine owns journey logic; section templates provide long-form prose.

## Suggested Handoff Prompt

```text
Act as Pearl_Architect + Pearl_Dev for Phoenix Omega.

Read:
- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- artifacts/audit/V4_TEMPLATE_SOURCE_HANDOFF_2026_04_11.md
- persona_topic_variables.schema.yaml
- config/format_selection/format_registry.yaml
- scripts/run_pipeline.py
- phoenix_v4/rendering/chapter_composer.py
- phoenix_v4/planning/enrichment_select.py
- config/spines/anxiety_spine.yaml
- artifacts/pilot/DEFINITIVE_PIPELINE_COMPARISON.md

TASK:
Recover or reconstruct the missing old Phoenix Omega template source and design a safe conversion path into the new spine pipeline.

First, search for these missing historical sources:
- SOURCE_OF_TRUTH/data/templates/phoenix_omega_book_template.csv
- Dels/phoenix_omega_book_template_FIXED.csv
- Dels/phoenix_omega_book_template_ANNOTATED.csv
- phoenix_omega_book_template_v3.csv
- del_newest_intake_prose/
- ab_auto/

If found, do not wire into production. Audit structure, row count, token usage, section types, and word counts. Produce:
- artifacts/audit/V4_TEMPLATE_SOURCE_RECOVERY_AUDIT.md
- docs/V4_SECTION_LIBRARY_CONVERSION_SPEC.md

If not found, reconstruct the schema from old_chat_specs and persona_topic_variables.schema.yaml, then propose the minimum section-library schema needed for deep_book_6h.

WRITE_SCOPE:
- artifacts/audit/V4_TEMPLATE_SOURCE_RECOVERY_AUDIT.md
- docs/V4_SECTION_LIBRARY_CONVERSION_SPEC.md
- optional config/sections_v4/README.md only if schema needs a placeholder

OUT_OF_SCOPE:
- run_pipeline.py changes
- production wiring
- rewriting spines
- copying unverified old CSVs into production paths

NON-NEGOTIABLE:
- Do not treat the old template CSV as canonical until recovered and audited
- Do not include all 3-5 variations in one manuscript unless each variation has a distinct role
- Preserve registry as default
- Spine remains journey authority; old templates can only become section prose sources
```

## Current Status

```text
STATUS: documented
PRIMARY FINDING: old template CSV is referenced but not present in current checkout
CONFIRMED PRESENT: persona_topic_variables.schema.yaml
CONFIRMED CURRENT SPINES: config/spines/*.yaml are journey skeletons, not old 10-section templates
NEXT_ACTION: recover old CSV/template folder or reconstruct a section-library spec from historical notes
```

