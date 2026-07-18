# Genre LoRA Cross-Test Results (2026-05-07)

## Scope

- Project: `PRJ-MANGA-V2`
- Subsystem: `manga_pipeline`
- Authority doc: `specs/AI_MANGA_PIPELINE_SUMMARY.md`
- Deliverable scope: workflow placeholders and licensing audit only

## Civitai License Audit (Confirmed)

### Super Robot Diffusion XL

- Civitai model ID: `124747`
- API `allowCommercialUse`: `"{Rent,RentCivit}"`
- Interpretation: Rent-program scoped only; not open commercial licensing
- Decision: `SKIP` for Phoenix production use

### DARK FANTASY XL

- Civitai model ID: `1223108`
- API `allowCommercialUse`: `"{Rent,RentCivit}"`
- Interpretation: Rent-program scoped only; not open commercial licensing
- Decision: `SKIP` for Phoenix production use

## Policy Rationale

Per Phoenix tier and governance policy, Rent-program scoped model licenses are out-of-policy for open commercial deployment. Both candidate genre LoRAs are therefore excluded from integration in this phase.

## Implementation Notes

- `scripts/image_generation/comfyui_workflows/animagine_xl_mecha.json` is a placeholder only.
- `scripts/image_generation/comfyui_workflows/animagine_xl_dark_fantasy.json` is a placeholder only.
- No LoRA loader nodes are wired in either workflow.
- No LoRA weights are checked into the repository.
- No changes were made to `scripts/manga/character_individuation/engine_router.py`.

## Phase C Follow-Up

Proceed with Phoenix-native mecha and painterly LoRA development via `ai-toolkit` on Animagine 4.0 under licensing that supports open commercial use.
