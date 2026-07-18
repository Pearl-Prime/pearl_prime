# Integration Effort Estimates — Phoenix Omega Manga Audit (Phase 1)

**Date:** 2026-04-29
**Phase:** 1
**Companion:** [community_assets_audit_2026-04-29.yaml](../../config/manga/community_assets_audit_2026-04-29.yaml) · [FORK_WRAP_BUILD_DECISIONS.md](../../docs/FORK_WRAP_BUILD_DECISIONS_2026-04-29.md)

**Convention:** estimates assume one engineer at Phoenix's familiarity level with ComfyUI + Python. Multiplier of 1.5–2× if assigned to a less-familiar engineer. Costs in dollars assume self-hosted RunPod / equivalent.

---

## Top-5 ROI ranking (do these first)

| # | Action | Effort | Cost | ROI rationale |
|---|---|---|---|---|
| 1 | **Fix workflow Schnell-at-Dev settings** (KSampler steps=24→4, cfg=4.0→1.0) — same fix as cookbook PR §0 | 0.5 h | $0 | Single-line JSON edit; fixes register oscillation in current outputs without any new dependency. |
| 2 | **Migrate LoRA training base from FLUX.1-dev to FLUX.1-schnell or Animagine 4.0** | 0.5 day config + 4 h per LoRA retrain (~5 min/LoRA × 62 LoRAs on H100 = ~5 h compute) | ~$50 in compute (RunPod H100 ~$2-3/hr × ~5 h, plus dev time) | Closes the critical license-violation finding. Required before any commercial Phoenix output. |
| 3 | **Fork PuLID-FLUX with FaceNet loader** into Phoenix workflow stack | 1 day | $0 | First-time Phoenix has character consistency tooling. Combined with already-planned protagonist LoRAs, covers both named cast + one-shots. |
| 4 | **Cross-test Super Robot Diffusion XL on Animagine 4.0** for mecha | 0.5 day | $0 | Validates whether Phoenix can fork the Illustrious-trained mecha LoRA onto a commercial-clean base. If pass → no Phoenix mecha LoRA training needed. |
| 5 | **Smoke-test Animagine 4.0 base for fantasy_adventure + healing genres** with Phoenix prompts | 0.5 day | $0 | Confirms the audit's "no LoRA needed" thesis for these lanes. If confirmed, Phoenix saves the LoRA training budget for these 2 of 25 genres (and likely many more in Phase 2). |

**Total Top-5 effort:** ~3 engineer-days + ~$50 compute. Closes the most urgent license risk + delivers character consistency + validates 3 of 4 Phase 1 genre paths.

---

## Per-recommendation effort breakdown

### Base model migration

| Task | Effort | Notes |
|---|---|---|
| Add Qwen-Image checkpoint to ComfyUI models dir | 0.5 h | Download from HF; ~20 GB |
| Add Animagine XL 4.0 checkpoint | 0.5 h | Download from HF; ~6 GB |
| Add Animagine VAE if not bundled | 0.25 h | |
| Create new workflow JSON variants (one per base) | 1 day | Variant templates: portrait, character-sheet, panel-edit |
| Update `runcomfy_batch.py` to dispatch to multiple workflow variants | 1 day | Already has manifest pattern; need workflow-selection logic |
| Migrate `brand_lora_plans.yaml::training_defaults.base_model` from FLUX.1-dev → FLUX.1-schnell or Animagine | 0.5 h | Config edit only |
| Retrain protagonist LoRAs on new base (62 total in `brand_lora_plans.yaml`) | ~5 h compute total on H100 | $15–$50 RunPod |
| Validate retrained LoRAs against existing reference images | 0.5 day | Side-by-side comparison |
| **Subtotal: base model migration** | **~3 days + $15-50** | |

### Character consistency

| Task | Effort | Notes |
|---|---|---|
| Install `lldacing/ComfyUI_PuLID_Flux_ll` custom nodes | 0.5 h | git clone + pip install |
| Install `cubiq/PuLID_ComfyUI` (for SDXL/Animagine path) | 0.5 h | |
| Verify FaceNet loader auto-downloads VGGFace2 weights to `~/.cache/torch/checkpoints/` | 0.25 h | |
| Edit workflow JSON to include `PulidFluxFaceNetLoader` + `Apply PuLID Flux` nodes | 1 day | Per workflow variant |
| Add reference-image input pathway to Phoenix's prompt compiler | 1 day | Optional reference image per generation |
| Test multi-character workflow (PuLID Flux II pattern) | 1 day | Validate two-character ordering |
| **Subtotal: character consistency** | **~3 days** | |

### Per-genre LoRAs

| Task | Effort | Cost |
|---|---|---|
| Download Super Robot Diffusion XL → cross-test on Animagine | 0.5 day | $0 |
| If degraded: train Phoenix mecha LoRA on Animagine | 1 day setup + 0.5 h compute on H100 | ~$3 |
| Download DARK FANTASY XL v1.1 → smoke test | 0.25 day | $0 |
| Verify Civitai 6-flag commercial permissions for each fork-target LoRA (~15 LoRAs Phase 1) | 1.5 h (5 min × 15 + buffer) | $0 |
| Document fantasy_adventure + healing as "no LoRA needed" lanes | 0.5 h | $0 |
| **Subtotal: per-genre LoRAs (Phase 1)** | **~2 days + ~$3** | |

### ComfyUI workflow refactor

| Task | Effort | Notes |
|---|---|---|
| Fork PuLID+OpenPose+Janus anime-character workflow as Phoenix template | 1 day | Strip Janus inversion, add Phoenix LoRA stack |
| Fork PuLID Flux II as Phoenix multi-character template | 0.5 day | FaceNet loader swap |
| Fork Consistent Character Creator 3.0 for LoRA reference image generation | 0.5 day | Drives `lora_refs/` population |
| Add HalfTone post-processing node (ComfyUI_LayerStyle) | 0.25 day | |
| (Optional) Add sketch2manga screentone path | 0.5 day | |
| Update `flux_character_portrait_template.json` → multiple variants | 0.5 day | Replace 7-node bare template |
| **Subtotal: workflow refactor** | **~3 days** | |

### LoRA training pipeline

| Task | Effort | Notes |
|---|---|---|
| Install ai-toolkit + clone repo | 0.5 h | |
| Adapt config templates from `train_lora_flux_schnell_24gb.yaml` to Phoenix conventions | 0.5 day | |
| Add Phoenix-side wrapper for batch training (62 LoRAs) | 1 day | Iterate over `brand_lora_plans.yaml` entries |
| (Optional) Install kohya_ss for advanced configs | 0.5 day | |
| (Optional) Install FluxGym for non-engineer onboarding | 0.5 day | Operator tool, not required |
| **Subtotal: training pipeline** | **~2 days** | |

### Custom node install

| Task | Effort | Notes |
|---|---|---|
| ComfyUI-Manager install | 0.25 h | Operator tool |
| `lldacing/ComfyUI_PuLID_Flux_ll` install | 0.25 h | Listed in char-consistency above |
| ComfyUI_LayerStyle install | 0.25 h | |
| sketch2manga install + dependencies | 0.5 h | |
| ComfyUI-Img2DrawingAssistants (optional) | 0.25 h | |
| **Subtotal: custom node install** | **~2 h** | |

---

## License verification overhead

| Asset class | Items | Time per | Total |
|---|---|---|---|
| Civitai LoRAs (Phase 1) | ~15 | 5 min | 1.25 h |
| HuggingFace models (Phase 1) | ~6 | 5 min | 0.5 h |
| Custom node packs (Phase 1) | ~8 | 5 min | 0.7 h |
| **Total verification overhead** | | | **~2.5 h** |

---

## Aggregate Phase 1 fork-implementation budget

| Stream | Effort | Cost |
|---|---|---|
| Base model migration | 3 days | $15-50 |
| Character consistency | 3 days | $0 |
| Per-genre LoRAs (Phase 1) | 2 days | ~$3 |
| Workflow refactor | 3 days | $0 |
| Training pipeline | 2 days | $0 |
| Custom node install | 0.25 day | $0 |
| License verification | 0.3 day | $0 |
| **Phase 1 total** | **~14 engineer-days** | **~$20-55** |

A two-engineer pair could land Phase 1 in ~7–10 calendar days. A solo engineer in ~3 weeks. The dollar cost is dominated by LoRA retraining compute, not asset acquisition (everything is free/open-source).

---

## Phase 2 cost estimate (if approved)

If operator approves Phase 2 at the narrowed scope recommended in [COMMUNITY_ASSETS_AUDIT.md](../../docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md):

- `qa_and_drift_detection` deep-dive (Qwen-VL vs WD-EVA02 in-house bench): 1 day research + 1 day bench setup + ~$5 compute
- `orchestration_and_batch` (Manga Editor Desu! deep diff): 1 day evaluation
- 4–6 high-priority remaining genres in LoRA roster: 2 days
- Estimated Phase 2 budget: ~5 engineer-days + ~$10 compute

Total Phase 1 + Phase 2 (narrowed): ~19 engineer-days + ~$65.

---

## What's NOT in this estimate

- **Operator decisions** required between phases (FLUX-dev migration timing, base model primary choice, AGPL acceptance, etc.).
- **Catalog regeneration** with the new base model — separate effort, depends on volume.
- **QA harness build** for the cookbook PR's drift-detection layer — Phase 2 territory.
- **Phoenix mecha LoRA training data acquisition** if the cross-test fails — license-cleared training data is non-trivial to assemble.
- **Phoenix QA bench** for Qwen-Image-i2L claim validation — Phase 2 territory; non-trivial bench design.
