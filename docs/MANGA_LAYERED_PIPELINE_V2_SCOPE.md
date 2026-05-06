# Manga Layered Pipeline V2 — Implementation Pointer (2026-05-07)

**Authority spec:** [docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md](CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md)

This document is a thin index. The V2 design is already specified — this
file maps each spec stage to a Pearl_Dev implementation workstream and
records the corrected budget that supersedes the over-engineered draft
that briefly lived in this scope-doc slot.

## Why V2 exists

V1 ships per the brand-2 manga ship at PR #<this-pr> with documented
caveats (identity drift across panels, register oscillation, heuristic
bubble placement). The hybrid character-individuation pipeline closes
all three. See the authority spec §0 for the full problem statement
and `artifacts/research/dashboard_22_failure_diagnosis_2026-05-02.md`
for the visual evidence (22 stillness_press protagonists collapsing to
the same Gaussian-attractor face).

## Scope (5 stages from the authority spec + 2 additive items)

| # | Source | Owner | Effort | Notes |
|---|---|---|---|---|
| 1 | Spec §2.1 — Author fills 12-axis YAML | Operator + brand owner | ~15 min per character | Schema already exists at `config/manga/character_design_template.yaml`; vocabulary at `config/manga/character_design_axes.yaml`. CONTENT work, not engineering. |
| 2 | Spec §2.2 — Constraint solver | Pearl_Dev | ~1 engineering day | 200-400 LOC Python; spec §2.2 has full pseudocode + thresholds (5 same-brand / 7 cross-brand). Hard rejection prevents catalog collisions. |
| 3 | Spec §2.3 — Prompt builder | Pearl_Dev | ~1 day | Reads validated `character_design` block; emits axis-specific tokens per base model (Animagine XL / Qwen-Image / FLUX-schnell — see spec §2.3 token-strategy table). |
| 4 | Spec §2.4 — PuLID-FaceNet install + reference-sheet generation | Pearl_Int (Pearl Star node install) + Pearl_Dev (reference-sheet generator) | ~0.5 day install + ~30 min per character ref-sheet | `lldacing/ComfyUI_PuLID_Flux_ll` (Apache 2.0). InsightFace BLOCKED — non-commercial per audit PR #803. |
| 5 | Spec §2.5 — Face-distance QA harness | Pearl_Dev | ~1 day | `facenet-pytorch` (commercial-clean VGGFace2) + cosine distance + threshold gate (<0.4 fail, 0.4–0.55 borderline manual, ≥0.55 pass). Runs post-render before commit. |
| +A | Per-character LoRA training (named recurring cast only) | Pearl_Dev | ~10 min training-prep per LoRA × 12-14 characters | `ai-toolkit (ostris, MIT)` per audit PR #803. NOT 200+ catalog — recurring cast only per `config/manga/brand_lora_plans.yaml`. PuLID covers everything else. |
| +B | Manga register layer | Pearl_Dev | ~0.5 day | `animeoutlineV4` LoRA + halftone post-processing (`ComfyUI_LayerStyle`) for the seinen-photorealistic register defect documented in `artifacts/research/comfyui_workflow_audit_2026-04-29.md`. |

**Total engineering budget: ~5-7 days Pearl_Dev wall-clock**, plus the
per-character authoring time (operator-driven; parallelizable).

This supersedes the earlier "9-component, 2-3 week LoRA-everywhere" draft
that briefly occupied this slot — the constraint solver is the
load-bearing innovation that makes 200+ catalog distinctness
deterministic without LoRA-per-character. LoRA training is now scoped to
the ~14 named recurring cast where per-series consistency over 12+
chapters justifies the per-character GPU spend.

## Workstream

`ws_manga_layered_pipeline_v2_20260507` (status: proposed) — single
parent ws covering all 7 items. Pearl_Dev may sub-divide into per-stage
ws's once Pearl_Architect cap entry ratifies the scope.

## Cap entry

`MANGA-LAYERED-PIPELINE-V2-01` — recommended for ratification in the
next Pearl_Architect session. Authority docs:

- `docs/CHARACTER_INDIVIDUATION_PIPELINE_SPEC_2026-05-02.md` (the spec)
- `artifacts/research/comfyui_workflow_audit_2026-04-29.md` (the
  commercial-clean stack; PuLID-FLUX-FaceNet vs blocked InstantID)
- `artifacts/research/average_face_problem_eval_2026-05-02.md` (the
  Gaussian-attractor analysis driving the 12-axis vocabulary)
- `config/manga/brand_lora_plans.yaml` (named-cast LoRA scope)

## V1 → V2 transition plan

1. V1 panels (this PR) live on R2 at
   `s3://phoenix-omega-artifacts/manga/<series>/ep_001/` and on WEBTOON
   Canvas after operator upload.
2. V2 ws lands the 7 items above.
3. Backfill re-renders go to `s3://.../<series>/ep_001/v2/` so V1 ↔ V2
   visual comparison is a directory diff. Operator decides per-series
   whether V2 supersedes V1 on WEBTOON Canvas after the diff is in hand.
4. Future ships (brand-3+, brand-1 ep_002, brand-2 ep_002) start on V2
   directly; no V1-then-V2 dual track for new content.

## Pearl_Dev sequencing recommendation

Phase A (~1.5 days) — Stages 2 + 3 + Pearl_Star PuLID install in parallel
Phase B (~1 day) — Stage 4 reference-sheet generator + Stage 5 QA harness
Phase C (~1 day) — Item +A LoRA training pipeline + +B register layer
Phase D (~1 day) — V2 re-render of stillness_press ep_001 + ep_002 +
                   cognitive_clarity ep_001 against V1 baseline; visual
                   diff lands as artifacts/qa/v1_v2_diff_<date>.md

Phase D's diff is the gate for accepting V2 as the new default; it is
NOT a rendering task to be repeated for every catalog item.
