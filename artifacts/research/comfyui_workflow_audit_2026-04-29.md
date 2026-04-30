# ComfyUI Workflow Audit — Phoenix Omega vs. Public Manga Workflows

**Date:** 2026-04-29
**Phase:** 1
**Companion:** [community_assets_audit_2026-04-29.yaml](../../config/manga/community_assets_audit_2026-04-29.yaml) · [COMMUNITY_ASSETS_AUDIT.md](../../docs/COMMUNITY_ASSETS_AUDIT_2026-04-29.md)

---

## Phoenix's current workflow — the baseline

**File:** [config/comfyui_workflows/manga_covers/flux_character_portrait_template.json](../../config/comfyui_workflows/manga_covers/flux_character_portrait_template.json)

### Topology (7 nodes)

```
CheckpointLoaderSimple (flux1-schnell-fp8.safetensors)
    ├── CLIPTextEncode (positive)
    ├── CLIPTextEncode (negative)
    └── KSampler (steps=24, cfg=4.0, sampler=euler, scheduler=normal)
        ← EmptyLatentImage (1024×1024)
        → VAEDecode
        → SaveImage
```

### Critical issues (from grounding inspection)

1. **Schnell-at-Dev settings.** Loads `flux1-schnell-fp8.safetensors` but runs KSampler at FLUX.1-dev settings. Schnell is distilled and spec'd for ~4 steps cfg 1.0; running at 24/4.0 produces unpredictable register oscillation. Same finding as the cookbook PR §0 — both PRs must remediate this together.
2. **No character consistency tooling.** No LoRA loader, no IP-Adapter, no PuLID, no ControlNet, no reference image input. Each generation produces a new face. PNG inspection of 8 outputs (3 failed + 5 working) confirmed this is the structural cause of identity drift.
3. **No manga-specific post-processing.** No halftone, no lineart extraction, no screentone — output ships raw to disk. This is why outputs oscillate between B&W manga line and full-color illustration: there's no register lock anywhere in the pipeline.
4. **No batch + variant pathway.** Single positive/negative pair, single seed. The wrapper script `runcomfy_batch.py` iterates externally, but the workflow itself can't generate a character sheet (multi-pose grid) or panel-to-panel variation in a single run.
5. **1024×1024 only.** No multi-aspect-ratio support. Manga panels and character sheets benefit from variable aspect (3:4 portrait, 16:9 splash, 1:1 emote).

---

## Five public workflows audited

### 1. PuLID Flux II — RunComfy

- **URL:** https://www.runcomfy.com/comfyui-workflows/pulid-flux-ii-in-comfyui-consistent-character-ai-generation
- **Author / origin:** lldacing's PuLID-Flux-II nodes; RunComfy hosts the template.
- **Last updated:** 2025-06-16 (ComfyUI v0.3.39).
- **License:** RunComfy ToS; underlying nodes Apache-2.0.
- **What it does:** Reference-image input → consistent character across varied scenes/styles. Two-character support via separate reference loaders.
- **Nodes:** Apply PuLID Flux, CLIPTextEncode, Load Image, SolidMask/MaskComposite/InvertMask (regional control), TeaCache + WaveSpeed (speed optimizers), KSampler with start_at/end_at timing.
- **Loader type:** defaults to InsightFace AntelopeV2 (🔴). Phoenix should swap to FaceNet variant via `lldacing/ComfyUI_PuLID_Flux_ll`'s `PulidFluxFaceNetLoader` to make commercial-clean.
- **Multi-character:** yes — left reference image binds first character described, right binds second. Order matters.
- **Gaps vs Phoenix:**
  - No LoRA stacking node (Phoenix needs to layer protagonist + brand-style + manga-register LoRAs).
  - No manga post-processing (halftone, lineart).
  - No batch / character-sheet pathway.
  - No prompt-template substitution (Phoenix's `runcomfy_batch.py` does this externally).

### 2. Mickmumpitz — Flux Consistent Characters (Input Image)

- **URL:** https://www.viewcomfy.com/blog/consistent-ai-characters-with-flux-and-comfyui
- **Author:** Mickmumpitz (popular YouTube tutorial chain); reproductions on ComfyOnline + ComfyUI.org.
- **What it does:** Single-character consistency from an input reference image; FLUX-native.
- **Strengths:** Well-documented; tutorial coverage; multiple platform reproductions confirm reproducibility.
- **Gaps vs Phoenix:** Same structural gaps as PuLID Flux II (no manga post-processing, no LoRA stack). Single-character only.
- **Use case:** Phoenix's protagonist portrait generation lane — single named character, multiple scenes.

### 3. Consistent Character Creator 3.0 — RunComfy

- **URL:** https://www.runcomfy.com/comfyui-workflows/consistent-character-creator-3-0
- **What it does:** Multi-pose character sheet generator from a single reference. Outputs grid of pose variations.
- **Use case for Phoenix:** Generate the LoRA training reference image set (`reference_views: front_portrait, three_quarter_view, profile_view, expression_neutral, …`) declared in `brand_lora_plans.yaml::protagonist_loras`. This workflow could automate that step.
- **Gaps:** Same loader-license issue as #1; no manga register lock.

### 4. Anime-Style Consistent Character (PuLID + OpenPose + DeepSeek-Janus)

- **URL:** https://comfyui.org/en/unlock-anime-style-characters-with-ai
- **What it does:** Combines PuLID-FLUX for face restoration (>90% feature retention claimed), OpenPose for skeleton/pose control, and DeepSeek-Janus for prompt inversion (image → prompt for re-generation). Anime/manga-specific.
- **Use case for Phoenix:** The closest public approximation of a "manga character pipeline" — face lock + pose control + register-aware re-prompting. **Recommended primary fork target.**
- **Strengths:** Anime-tuned (matches Phoenix's register goal). Pose control is exactly what's needed for manga-panel composition.
- **Gaps:** DeepSeek-Janus inversion is not strictly necessary at Phoenix scale (Phoenix has its own prompt compiler); the OpenPose layer is the high-value add.

### 5. Flux Kontext PuLID — RunComfy

- **URL:** https://www.runcomfy.com/comfyui-workflows/flux-kontext-pulid-consistent-character-generation
- **What it does:** FLUX.1 Kontext (image editing variant) + PuLID for character-edit-in-place. Edit existing image while preserving character identity.
- **Use case for Phoenix:** Character-consistent panel-to-panel edits (same character, new pose/scene/lighting). Useful for the Phase 2 panel_layout dimension.
- **Gaps:** Same loader-license issue. Kontext-specific (different than vanilla schnell/dev path).

---

## Diff matrix — Phoenix vs. fork candidates

| Capability | Phoenix current | PuLID Flux II | Mickmumpitz | Char Creator 3.0 | PuLID+OpenPose+Janus | Kontext+PuLID |
|---|---|---|---|---|---|---|
| Character consistency | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-character | ❌ | ✅ (2-char) | ❌ | ❌ | ⚠ partial | ❌ |
| Pose control | ❌ | ❌ | ❌ | ✅ (sheet) | ✅ (OpenPose) | ⚠ via Kontext |
| LoRA stack | ❌ | ❌ | ❌ | ❌ | ⚠ partial | ❌ |
| Manga register | ❌ | ❌ | ❌ | ❌ | ✅ (anime-tuned) | ❌ |
| Halftone/screentone | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Batch + variant | external script | ❌ | ❌ | ✅ (sheet) | ❌ | ❌ |
| FLUX-schnell native | ⚠ misconfigured | ✅ | ✅ | ✅ | ✅ | ❌ (Kontext-specific) |
| Animagine/SDXL path | ❌ | ❌ (FLUX) | ❌ (FLUX) | ❌ (FLUX) | ❌ (FLUX) | ❌ |
| Commercial-clean loader | ❌ | ⚠ swap req | ⚠ | ⚠ | ⚠ | ⚠ |

**Key finding:** no single public workflow covers all of Phoenix's needs. The optimal fork is a **composite**: PuLID+OpenPose+Janus base for character + pose + anime register, with Phoenix-side additions for LoRA stacking and manga post-processing (HalfTone via ComfyUI_LayerStyle, sketch2manga for screentone).

---

## Cross-pollination with the cookbook PR

The cookbook PR's drift autopsy and this audit's PNG inspection converge on the same diagnostic for Phoenix's current outputs:

| Finding | Cookbook PR §0 | This audit |
|---|---|---|
| Schnell-at-Dev settings | ✅ identified | ✅ confirmed via workflow JSON read |
| Mecha asset-absence (not stylistic drift) | (cookbook focus on prompt) | ✅ added — needs LoRA, not prompt fix alone |
| Asian-script artifacts unprompted | (negative prompt fix) | ✅ Qwen-Image would let Phoenix control these intentionally |
| Register oscillation B&W ↔ color | (prompt-controlled) | ✅ structural — needs LoRA-locked register |
| Identity drift across outputs | (out of cookbook scope) | ✅ structural — needs PuLID+protagonist-LoRA hybrid |

The two PRs are mutually reinforcing. The cookbook PR fixes the prompt layer; this audit's recommendations fix the workflow + base-model + LoRA-stack layer. Neither alone is sufficient; both together close the failure-genre loop.

---

## Recommended Phoenix workflow target (fork outcome)

```
[QwenImageLoader] OR [AnimagineXLLoader] OR [FluxSchnellLoader (4 steps cfg 1.0)]
    ├── LoRAStack (animeoutlineV4 + brand-style LoRA + protagonist LoRA)
    ├── CLIPTextEncode (positive + negative, with Phoenix prompt compiler output)
    ├── PulidFluxFaceNetLoader  (or LoRAOnly if protagonist LoRA is sufficient)
    │   └── Apply PuLID Flux  (one-shot reference; bypassed for known cast)
    ├── OpenPose ControlNet  (optional: enforce pose for character sheet)
    ├── KSampler  (steps + cfg matched to base: schnell=4/1, dev=24/4, animagine=28/6, qwen=20-30/4-6)
    ├── VAEDecode
    ├── HalfTone (ComfyUI_LayerStyle)  (optional: B&W manga register lock)
    ├── sketch2manga (optional: screentone application)
    └── SaveImage
```

**Effort to implement:** 2–3 days. JSON edit + custom-node install. See [integration_effort_estimates_2026-04-29.md](integration_effort_estimates_2026-04-29.md) for breakdown.

This replaces the current 7-node bare workflow. Multiple variants of this template will be needed (one per base model; one per use case: portrait / character-sheet / panel-edit). Phoenix's `runcomfy_batch.py` orchestration layer continues to drive the templates with prompt + seed substitutions.
