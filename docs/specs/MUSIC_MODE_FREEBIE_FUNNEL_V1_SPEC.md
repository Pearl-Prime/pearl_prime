# Music Mode Freebie Funnel — V1 Spec

**Status:** SPECCED (gt30d C05 · 2026-07-22)  
**Keepers:** I026 (I027 survey pointer)  
**Owner:** Pearl_Architect (Claude) → Cursor D08 wires selection  
**Reuse:** `docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/` — do not greenfield a parallel music stack.

## 0. Purpose

Freebie selection for music-mode brands MUST be driven by:

1. `brand_wizard` YAML output for the minted brand, and
2. `musician_reflections_survey` (or successor) YAML,

**not** hardcoded freebie lists in Python.

## 1. Selection contract

```text
inputs: brand_wizard.yaml + musician_reflections_survey.yaml
output: freebie_bundle_id + rationale_fields
rules:
  - missing wizard/survey → hard error (no silent default catalog freebie)
  - selection deterministic given same inputs
  - diversity CI from music_mode pack remains authoritative
```

## 2. Merge-with-existing

| Existing | Role |
|---|---|
| 20260721 music_mode wizard-to-pipeline pack | Brand mint + pipeline detect + diversity CI |
| Freebie harbor closeout pack (20260715) | Harbor/post-experience — do not reimplement |

## 3. Cursor D08 checklist

1. [ ] Locate wizard + survey YAML schemas on disk; document paths in CLOSEOUT.
2. [ ] Implement selector function consumed by freebie funnel entrypoint.
3. [ ] Unit test: hardcoded list path fails / is removed.
4. [ ] Smoke one brand fixture end-to-end (no live publish).

## 4. Signal

`gt30d-c05-spec-terminal` when this file lands.
