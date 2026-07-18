# ComfyUI Workflow Design: Character Reference & IP-Adapter

**Version:** 1.0
**Date:** April 2026
**Workstream:** 5
**Authority:** Pearl_Architect
**Status:** Spec draft
**Classification:** Confidential

---

## Overview

This spec documents the two ComfyUI workflow designs required for Workstream 5:

1. **`character_sheet_generation.json`** — generates reference image turnarounds and expression sheets for a character (run once per character per series)
2. **`panel_generation_with_reference.json`** — extends the existing panel generation workflow with IP-Adapter reference conditioning for character and setting consistency

Both workflows extend the render stack described in `MANGA_MODE_SYSTEM_SPEC.md` §6. Read that section first for the complete rendering philosophy.

---

## 1. Workflow A: `character_sheet_generation.json`

### 1.1 Purpose

Generates all 12 reference images for a single character. Run once per character at series initialization (Stage 0.5). The output images become the reference inputs for Workflow B at chapter generation time.

### 1.2 Node graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW A: CHARACTER SHEET GENERATION                                     │
│  config/manga/comfyui_workflows/character_sheet_generation.json             │
└─────────────────────────────────────────────────────────────────────────────┘

[NODE 1] CheckpointLoaderSimple
  ├── ckpt_name: <style_archetype_checkpoint>
  │     iyashikei → "CounterfeitV3.safetensors" or "PastelAnimeMix.safetensors"
  │     psychological → "MangaBW_v2.safetensors"
  │     webtoon → "ToonYou.safetensors"
  └── outputs: MODEL, CLIP, VAE

[NODE 2] LoraLoader  (Style LoRA)
  ├── model: from NODE 1
  ├── clip: from NODE 1
  ├── lora_name: <style_lora_for_archetype>
  ├── strength_model: 0.50
  ├── strength_clip: 0.50
  └── outputs: MODEL, CLIP

[NODE 3] CLIPTextEncode  (Positive prompt)
  ├── clip: from NODE 2
  ├── text: "{character_base_prompt}, {view_specification},
              character design reference sheet, white background,
              clean line art, manga style, full body visible,
              {style_archetype_positive_tags}"
  └── outputs: CONDITIONING

[NODE 4] CLIPTextEncode  (Negative prompt)
  ├── clip: from NODE 2
  ├── text: "background scene, blurry background, watermark, signature,
              text overlay, multiple characters, multiple views in frame,
              cropped, cut off, bad anatomy, extra limbs, deformed hands,
              wrong hair color, {character_forbidden_variants}"
  └── outputs: CONDITIONING

[NODE 5] EmptyLatentImage
  ├── width: 1024    (SDXL) or 768 (SD 1.5)
  ├── height: 1024   (1:1 for turnarounds; 768x1024 portrait for expression sheets)
  ├── batch_size: 1
  └── outputs: LATENT

[NODE 6] KSamplerAdvanced
  ├── model: from NODE 2
  ├── positive: from NODE 3
  ├── negative: from NODE 4
  ├── latent_image: from NODE 5
  ├── add_noise: enable
  ├── noise_seed: {character_base_seed + view_offset}
  ├── steps: 30
  ├── cfg: 7.0
  ├── sampler_name: "dpm++2m"
  ├── scheduler: "karras"
  ├── start_at_step: 0
  ├── end_at_step: 30
  ├── return_with_leftover_noise: disable
  └── outputs: LATENT

[NODE 7] VAEDecode
  ├── samples: from NODE 6
  ├── vae: from NODE 1
  └── outputs: IMAGE

[NODE 8] FaceDetailer   (IMPACT PACK — applies to expression sheets only)
  ├── image: from NODE 7
  ├── model: from NODE 2
  ├── clip: from NODE 2
  ├── vae: from NODE 1
  ├── positive: "detailed eyes, clear pupils, defined eyelashes, sharp features"
  ├── negative: "blurry eyes, missing pupils, drooping eyelid"
  ├── guide_size: 512
  ├── guide_size_for: "bbox"
  ├── max_size: 1024
  ├── seed: {character_base_seed + view_offset + 1000}
  ├── steps: 15
  ├── cfg: 6.5
  ├── sampler_name: "dpm++2m"
  ├── scheduler: "karras"
  ├── denoise: 0.45
  ├── bbox_threshold: 0.50
  ├── bbox_dilation: 10
  └── outputs: IMAGE

  CONDITION: Enable FaceDetailer only for expression_* views.
             Disable for turnaround views (front, side, back, three_quarter).
             Disable for sitting, hands_detail.

[NODE 9] ImageUpscaleWithModel  (4x-UltimateSD Upscale)
  ├── upscale_model: "4x_ESRGAN.pth"  or "4xAnimeSharp.pth"
  ├── image: from NODE 8 (or NODE 7 if FaceDetailer disabled)
  └── outputs: IMAGE  (4096x4096 output for print-quality sheets)

[NODE 10] SaveImage
  ├── images: from NODE 9
  ├── filename_prefix: "{series_id}_{character_id}_{view_name}"
  ├── output_dir: "config/source_of_truth/manga_character_sheets/{series_id}/{character_id}/"
  └── (no output — side effect)
```

### 1.3 Parameter injection

The workflow is a JSON template. The Python wrapper (`character_sheet_build.py`) replaces these template variables before submitting each run:

| Template variable | Source | Example |
|------------------|--------|---------|
| `{character_base_prompt}` | Built from `series_identity.yaml` character.visual_archetype | `"teenage girl, short uneven dark hair, wiry build, oversized dark olive jacket"` |
| `{view_specification}` | VIEW_SPECS dict in wrapper script | `"full body, front view, facing camera"` |
| `{style_archetype_checkpoint}` | `brand_dna.yaml` → style archetype | `"CounterfeitV3.safetensors"` |
| `{style_lora_for_archetype}` | `style_archetypes.yaml` | `"cozy_style_lora.safetensors"` |
| `{style_archetype_positive_tags}` | Style archetype config | `"soft rounded shapes, pastel palette, watercolor wash"` |
| `{character_base_seed}` | Deterministic from character_id hash | `4821` |
| `{view_offset}` | Per-view integer (0-11) | `0` for front, `1` for side, etc. |
| `{character_forbidden_variants}` | From character visual_archetype notes | `"wrong hair length, different jacket color"` |

### 1.4 Output quality validation

After generation, each image is automatically validated:

```python
def validate_character_sheet_image(image_path: str, view_name: str) -> ValidationResult:
    """Validate generated character sheet image before writing to manifest."""

    # 1. Dimensions check
    img = Image.open(image_path)
    assert img.width >= 1024 and img.height >= 1024, "Minimum resolution not met"

    # 2. Background check (white background expected)
    corner_pixels = [img.getpixel((10, 10)), img.getpixel((img.width-10, 10))]
    bg_brightness = sum(sum(p) for p in corner_pixels) / (len(corner_pixels) * 3)
    assert bg_brightness > 200, "Background not white — character sheet unusable as reference"

    # 3. Not-blank check
    center_pixel = img.getpixel((img.width//2, img.height//2))
    assert sum(center_pixel) < 700, "Image appears blank — generation failed"

    # 4. Aesthetic score (optional, using CLIP aesthetic scorer)
    if AESTHETIC_SCORER_AVAILABLE:
        score = aesthetic_score(image_path)
        assert score > 0.65, f"Aesthetic score {score} too low for reference sheet"

    return ValidationResult(valid=True, image_path=image_path)
```

---

## 2. Workflow B: `panel_generation_with_reference.json`

### 2.1 Purpose

Extends the existing panel generation workflow (described in `MANGA_MODE_SYSTEM_SPEC.md` §6) with:
1. IP-Adapter reference conditioning from character sheets
2. Optional setting reference conditioning
3. Expression-specific face reference for close-up shots
4. Region-isolated conditioning for multi-character panels

### 2.2 Node graph (single-character panel)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WORKFLOW B: PANEL GENERATION WITH CHARACTER REFERENCE                      │
│  config/manga/comfyui_workflows/panel_generation_with_reference.json        │
└─────────────────────────────────────────────────────────────────────────────┘

════════════════════════════
  LAYER 1: MODEL LOADING
════════════════════════════

[NODE 1] CheckpointLoaderSimple
  ├── ckpt_name: {style_archetype_checkpoint}
  └── outputs: MODEL, CLIP, VAE

[NODE 2] LoraLoader  (Style LoRA)
  ├── model/clip: from NODE 1
  ├── lora_name: {style_lora}
  ├── strength_model: 0.50
  ├── strength_clip: 0.50
  └── outputs: MODEL, CLIP

[NODE 3] LoraLoader  (Character LoRA — primary character)
  ├── model/clip: from NODE 2
  ├── lora_name: {character_lora_path}
  ├── strength_model: {lora_strength_model}   (0.85 default)
  ├── strength_clip: {lora_strength_clip}     (0.70 default)
  └── outputs: MODEL, CLIP

════════════════════════════
  LAYER 2: IP-ADAPTER CONDITIONING
════════════════════════════

[NODE 4] IPAdapterModelLoader   (IPAdapter-Plus)
  ├── ipadapter_file: "ip-adapter-plus_sd15.bin"  or  "ip-adapter-plus_sdxl.bin"
  └── outputs: IPADAPTER

[NODE 5] CLIPVisionLoader
  ├── clip_name: "clip_vision_vit_l14.safetensors"
  └── outputs: CLIP_VISION

[NODE 6] LoadImage  (Body reference)
  ├── image: {character_reference_image}
  │           (from character_refs[0].reference_image — three_quarter or front)
  └── outputs: IMAGE, MASK

[NODE 7] IPAdapterApply   (Body / full character conditioning)
  ├── model: from NODE 3
  ├── ipadapter: from NODE 4
  ├── image: from NODE 6
  ├── clip_vision: from NODE 5
  ├── weight: {ip_adapter_strength}   (0.75 for protagonist; 0.65 for secondary)
  ├── weight_type: "linear"
  ├── start_at: 0.0
  ├── end_at: 0.85
  │     NOTE: Releasing at 0.85 rather than 1.0 lets scene details
  │     influence the final denoising steps without overriding character identity.
  ├── attn_mask: None   (full image — no region mask for single character)
  └── outputs: MODEL

[NODE 8] LoadImage  (Expression / face reference)
  ├── image: {expression_reference_image}
  │           (from character_refs[0].expression_ref — expression_focused, etc.)
  └── outputs: IMAGE, MASK

[NODE 9] IPAdapterApply   (Face expression conditioning — secondary, lower weight)
  ├── model: from NODE 7
  ├── ipadapter: from NODE 4
  ├── image: from NODE 8
  ├── clip_vision: from NODE 5
  ├── weight: 0.55
  ├── weight_type: "style transfer"
  ├── start_at: 0.0
  ├── end_at: 0.70
  │     NOTE: Lower weight and shorter range — expression is guidance, not lock.
  │     The scene prompt should determine the actual expression; the ref
  │     only enforces the base facial identity.
  └── outputs: MODEL

════════════════════════════
  LAYER 3: SDF GEOMETRIC CONDITIONING (from MANGA_MODE_SYSTEM_SPEC §6.7)
════════════════════════════

[NODE 10] SDFConditioningNode   (custom PyTorch node)
  ├── sdf_model: {sdf_model_path}
  ├── camera_angle: {sdf_pose_mod}   (e.g., "standing_front", "leaning_forward")
  └── outputs: DEPTH_MAP, CONTOUR_MAP

[NODE 11] ControlNetLoader
  ├── control_net_name: "control_v11f1p_sd15_depth.pth"
  └── outputs: CONTROL_NET

[NODE 12] ControlNetApply
  ├── conditioning: (positive prompt conditioning, see NODE 15)
  ├── control_net: from NODE 11
  ├── image: DEPTH_MAP from NODE 10
  ├── strength: {controlnet_strength}   (0.60 default; 0.70 for extreme poses)
  └── outputs: CONDITIONING

════════════════════════════
  LAYER 4: SETTING REFERENCE (optional)
════════════════════════════

[NODE 13] LoadImage  (Setting reference — optional, skip if no setting_refs)
  ├── image: {setting_reference_image}
  └── outputs: IMAGE, MASK

[NODE 14] IPAdapterApply   (Setting conditioning — low weight)
  ├── model: from NODE 9
  ├── ipadapter: from NODE 4
  ├── image: from NODE 13
  ├── clip_vision: from NODE 5
  ├── weight: {setting_ip_adapter_strength}   (0.35-0.55 based on camera distance)
  ├── weight_type: "linear"
  ├── start_at: 0.0
  ├── end_at: 0.60
  │     NOTE: Even lower range — setting is atmosphere, not constraint.
  └── outputs: MODEL

  CONDITION: If panel has no setting_refs, skip NODES 13-14 and pass
             NODE 9 output directly to the sampler.

════════════════════════════
  LAYER 5: PROMPT COMPILATION
════════════════════════════

[NODE 15] CLIPTextEncode  (Positive)
  ├── clip: from NODE 3
  ├── text: "{scene_prompt}, {camera_instruction},
              emotion: {emotion_state},
              {style_archetype_positive_tags},
              manga panel, {series_visual_tags}"
  └── outputs: CONDITIONING

[NODE 16] CLIPTextEncode  (Negative)
  ├── clip: from NODE 3
  ├── text: "extra limbs, deformed hands, watermark, text, logo,
              wrong hairstyle, {character_forbidden_variants},
              photorealistic, 3D render, low quality, blurry"
  └── outputs: CONDITIONING

[NODE 17] ControlNetApply  (applies ControlNet conditioning to prompt)
  ├── conditioning: from NODE 15
  ├── control_net: from NODE 11
  ├── image: DEPTH_MAP from NODE 10
  ├── strength: {controlnet_strength}
  └── outputs: CONDITIONING

════════════════════════════
  LAYER 6: LATENT & SAMPLING
════════════════════════════

[NODE 18] EmptyLatentImage
  ├── width: 1200
  ├── height: 900
  ├── batch_size: 1
  └── outputs: LATENT

[NODE 19] KSamplerAdvanced
  ├── model: from NODE 14  (or NODE 9 if no setting)
  ├── positive: from NODE 17
  ├── negative: from NODE 16
  ├── latent_image: from NODE 18
  ├── add_noise: enable
  ├── noise_seed: {panel_seed}
  │     panel_seed = base_seed + scene_id + panel_id  (deterministic — see §6.4 of MANGA_MODE_SYSTEM_SPEC)
  ├── steps: 30
  ├── cfg: 7.5
  ├── sampler_name: "dpm++2m"
  ├── scheduler: "karras"
  ├── start_at_step: 0
  ├── end_at_step: 30
  └── outputs: LATENT

[NODE 20] VAEDecode
  ├── samples: from NODE 19
  ├── vae: from NODE 1
  └── outputs: IMAGE

════════════════════════════
  LAYER 7: POST-PROCESSING
════════════════════════════

[NODE 21] MangaToner   (optional — manga-specific line art post-process)
  ├── image: from NODE 20
  ├── num_zones: 6
  ├── edge_strength: 1.1
  │     NOTE: Lower than MANGA_MODE_SYSTEM_SPEC default (1.2) to preserve
  │     IP-Adapter face detail from NODE 9.
  └── outputs: IMAGE

  CONDITION: Apply MangaToner only for:
             - dark_psychological archetype (always)
             - cozy_iyashikei (optional, at 0.8 strength)
             - Skip for webtoon_vertical_romance (color style; toner ruins soft shading)

[NODE 22] FaceDetailer   (IMPACT PACK)
  ├── image: from NODE 21 (or NODE 20 if MangaToner skipped)
  ├── model: from NODE 14
  ├── clip: from NODE 3
  ├── vae: from NODE 1
  ├── positive: "detailed eyes, clear pupils, {character_face_tags}"
  ├── negative: "blurry eyes, missing pupils"
  ├── denoise: 0.35  (low — preserve IP-Adapter identity; only repair artifacts)
  ├── steps: 12
  ├── cfg: 6.0
  └── outputs: IMAGE

  NOTE: denoise 0.35 (not 0.45 as in character sheet generation) because
        we are in a scene, not a white-background sheet. Too much denoise
        here fights the IP-Adapter conditioning we paid for.

[NODE 23] SaveImage
  ├── images: from NODE 22
  ├── filename_prefix: "{series_id}_{book_id}_{panel_id}"
  ├── output_dir: "renders/{book_id}/raw_panels/"
  └── (no output — side effect)
```

### 2.3 Multi-character panel variant

When `characters_in_panel` contains 2+ characters, the workflow uses `RegionalIPAdapter` from ComfyUI-Impact-Pack to isolate each character's reference conditioning to its spatial region:

```
After NODE 3 (Character LoRA stack for char 1):
    ↓
[NODE 3b] LoraLoader  (Character LoRA — second character)
  ├── model/clip: from NODE 3
  ├── lora_name: {character_2_lora_path}
  ├── strength_model: 0.75   (slightly lower — second character)
  ├── strength_clip: 0.65
  └── outputs: MODEL, CLIP

After LoRA stack:

[NODE 6a] LoadImage  (Reference image, character 1)
[NODE 6b] LoadImage  (Reference image, character 2)

[NODE MASK-A] ImageToMask  (left-half mask for character 1 region)
  ├── Generates pixel mask: left 55% of frame
  └── outputs: MASK

[NODE MASK-B] ImageToMask  (right-half mask for character 2 region)
  ├── Generates pixel mask: right 55% of frame (overlap intentional)
  └── outputs: MASK

[NODE 7a] IPAdapterApply   (Character 1, regional)
  ├── model: from NODE 3b
  ├── image: from NODE 6a
  ├── weight: 0.75
  ├── attn_mask: MASK-A   ← spatial isolation
  └── outputs: MODEL

[NODE 7b] IPAdapterApply   (Character 2, regional)
  ├── model: from NODE 7a
  ├── image: from NODE 6b
  ├── weight: 0.70   (slightly lower for secondary character)
  ├── attn_mask: MASK-B
  └── outputs: MODEL

[Continue with NODE 8 onward as single-character workflow]
```

**Why overlap in masks:** A 55%/55% overlap allows the boundary region (where characters interact or are spatially close) to receive some conditioning from both references. Pure 50%/50% split creates a hard edge artifact at the panel center. The overlap softens this.

**Maximum characters per panel with regional IP-Adapter:** 3. Beyond that, masks become too narrow to be effective. For panels with 4+ characters, fall back to text-prompt-only identity (no IP-Adapter) and rely on LoRA stack alone.

### 2.4 B&W (grayscale) panel variant

For `dark_psychological` and `cozy_iyashikei` (partial) style archetypes that use grayscale or limited palette:

```
After NODE 20 (VAEDecode):

[NODE 20b] ImageToGrayscale  (if color_mode = "black_and_white")
  ├── image: from NODE 20
  └── outputs: IMAGE (grayscale)

[NODE 20c] HalftoneApply  (if color_mode = "black_and_white" and halftone_enabled)
  ├── image: from NODE 20b
  ├── dot_size: 4
  ├── angle: 45
  ├── shadow_threshold: 0.3
  └── outputs: IMAGE

[Continue with NODE 21 MangaToner (required for B&W)]
```

### 2.5 IP-Adapter model selection guide

Different IP-Adapter models have different characteristics. The correct model depends on the base checkpoint:

| Base checkpoint type | IP-Adapter model | Notes |
|---------------------|-----------------|-------|
| SD 1.5 based | `ip-adapter-plus_sd15.bin` | Face preservation mode; best for manga characters with exaggerated features |
| SDXL based | `ip-adapter-plus_sdxl_vit-h.bin` | Higher fidelity, larger model |
| For face-only (expression nodes) | `ip-adapter-plus-face_sd15.bin` or `ip-adapter-faceid-portrait.bin` | Portrait-specialized; better facial detail |

**Rule:** Do not mix IP-Adapter base versions across nodes in the same workflow. If using SDXL checkpoint, use SDXL IP-Adapter throughout.

---

## 3. Weight Interaction Reference

This table summarizes how all conditioning weights interact. When values conflict, SDF wins on geometry; LoRA wins on style texture; IP-Adapter wins on identity reference matching.

| Layer | Component | Weight range | What it controls | Priority |
|-------|-----------|-------------|-----------------|----------|
| 1 | Style LoRA | model: 0.40-0.60, clip: 0.40-0.60 | Line quality, shading mode, palette | Lowest |
| 1 | Character LoRA | model: 0.75-0.90, clip: 0.65-0.75 | Face, hair, outfit texture | Medium |
| 2 | IP-Adapter (body reference) | 0.65-0.80 | Full character pose and identity | High |
| 2 | IP-Adapter (face reference) | 0.50-0.65 | Facial features, expression base | High |
| 2 | IP-Adapter (setting) | 0.30-0.55 | Location atmosphere | Low |
| 3 | ControlNet (SDF depth) | 0.55-0.70 | Body geometry, proportions | Highest |
| 4 | Prompt | cfg: 7.0-7.5 | Scene content, emotion, camera | Context |

**Conflict resolution precedence:** SDF geometry > LoRA identity > IP-Adapter reference > Style LoRA > Prompt

**Sum of LoRA weights:** Never exceed 2.0 total across all LoRAs loaded simultaneously. For 3 LoRAs (style + char1 + char2): 0.50 + 0.85 + 0.75 = 2.10 — reduce char2 to 0.65 to stay under cap.

---

## 4. Seed Management

Seed control is non-negotiable. Same inputs must produce same outputs for reproducibility and regeneration.

```python
# From MANGA_MODE_SYSTEM_SPEC.md §6.4 — enforced in workflow JSON

scene_seed = base_seed + scene_id
panel_seed = scene_seed + panel_id

# Example:
base_seed = 2000               # from series_identity generation_hash
scene_id = 3                   # chapter 03
panel_id = 4                   # panel 4 in chapter 3

scene_seed = 2000 + 3 = 2003
panel_seed = 2003 + 4 = 2007   # NODE 19 noise_seed = 2007
```

Character sheet seeds:
```python
character_base_seed = int(hashlib.sha256(character_id.encode()).hexdigest(), 16) % 10000
# sora_hashimoto → 4821
# view_offset: front=0, side=1, back=2, three_quarter=3, expression_*=4-9, etc.
view_seed = character_base_seed + view_offset
```

---

## 5. File Locations

```
config/manga/comfyui_workflows/
    character_sheet_generation.json         # Workflow A
    panel_generation_with_reference.json    # Workflow B (single character)
    panel_generation_multi_character.json   # Workflow B variant (2-3 characters)
    panel_generation_bw.json                # Workflow B variant (grayscale)
    cover_art_generation.json               # Separate workflow for volume covers

config/manga/comfyui_nodes_required.txt     # List of required custom nodes for installation

models/
    checkpoints/
        CounterfeitV3.safetensors
        MangaBW_v2.safetensors
        ToonYou.safetensors
    loras/
        styles/
            cozy_style_lora.safetensors
            dark_style_lora.safetensors
        characters/
            <series_id>/
                <character_id>_lora.safetensors
    controlnet/
        control_v11f1p_sd15_depth.pth
    ipadapter/
        ip-adapter-plus_sd15.bin
        ip-adapter-plus-face_sd15.bin
        ip-adapter-plus_sdxl_vit-h.bin
    clip_vision/
        clip_vision_vit_l14.safetensors
    upscale/
        4x_ESRGAN.pth
        4xAnimeSharp.pth
```

---

## 6. Workflow Validation Checklist

Before submitting to production, validate each workflow version:

```
WORKFLOW A (character_sheet_generation.json):
  [ ] Generates 12 images for a known character in < 5 minutes on A100
  [ ] All 12 outputs have white background
  [ ] Expression variants show recognizably different emotions
  [ ] Front/side/back turnarounds are visually consistent (same character)
  [ ] FaceDetailer active only on expression_* views; disabled for body turnarounds
  [ ] Seeds are deterministic: re-running same parameters produces identical outputs
  [ ] Output files saved to correct character_sheet directory

WORKFLOW B (panel_generation_with_reference.json):
  [ ] Loaded character reference image produces recognizable character in output
  [ ] IP-Adapter body weight 0.75 + face weight 0.55 do not over-flatten the composition
  [ ] ControlNet depth does not fight IP-Adapter identity (test at different strengths)
  [ ] Setting reference at weight 0.45 adds atmosphere without dominating character
  [ ] Seeds deterministic across runs
  [ ] FaceDetailer denoise 0.35 repairs eye artifacts without changing face identity
  [ ] B&W variant: halftone density appropriate; not over-rendered
  [ ] Multi-character variant: faces do not merge at boundary region

GATE COMPLIANCE:
  [ ] Gate D2 (Identity Drift): 20 test panels from same character all score > 0.82 CLIP similarity
  [ ] Gate C2 (Character Recognition): main cast distinguishable in cropped panels
  [ ] Gate C1 (Style Distinctiveness): series does not look like generic default anime
```

---

## 7. Known Limitations & Mitigations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| IP-Adapter degrades at extreme angles | Character may not match reference for 90-degree profile shots | Use `side.png` reference image (not `front.png`) when camera is `side_profile`; select reference based on panel camera angle |
| IP-Adapter face blending in multi-character panels | Two characters' faces partially merge near panel center | Regional conditioning with overlapping masks; ensure clear spatial separation in prompt ("standing left of frame", "standing right of frame") |
| Expression ref over-rides scene emotion | Character expression doesn't match scene emotional beat | Reduce face IP-Adapter weight to 0.40-0.45 for emotionally complex panels; trust the prompt |
| Setting IP-Adapter flattens day/night variant | Garden looks the same time-of-day regardless of prompt | Select time-specific setting reference (morning_variant vs. day_variant vs. evening_variant) in `compile_panel_prompt()` |
| LoRA + IP-Adapter weight sum too high | Generation artifacts; oversaturation | Monitor: character LoRA (0.85) + IP-Adapter body (0.75) + IP-Adapter face (0.55) total influence high. Reduce LoRA to 0.75 if artifacts appear |
| Character evolution (Sora's jacket) | Volume 1 reference has jacket on; volume 2 panels should show jacket off | Build separate `volume_2_jacket_off` character sheet variant; select via `volume_variant` field in panel_prompts.json |

---

## 8. Integration With Existing Specs

| Integration point | This workflow adds | Spec authority |
|------------------|-------------------|----------------|
| Render stack (`MANGA_MODE_SYSTEM_SPEC.md` §6) | IP-Adapter nodes between LoRA layer and sampler | `MANGA_MODE_SYSTEM_SPEC.md` |
| SDF conditioning (`MANGA_MODE_SYSTEM_SPEC.md` §6.7) | NODE 10-12 implement SDF depth conditioning | `MANGA_MODE_SYSTEM_SPEC.md` |
| Gate D2 Identity Drift | Workflow enables CLIP similarity scoring; drift check now has reference to compare against | `MANGA_MODE_SYSTEM_SPEC.md` §7 |
| Series identity characters (`manga_series_identity_layer.md`) | `character.visual_archetype` → NODE 3 positive prompt | `specs/manga_series_identity_layer.md` |
| Character sheet manifests (`manga_character_setting_consistency.md`) | manifest.reference_images → NODE 6 + 8 inputs | `specs/manga_character_setting_consistency.md` |
| panel_prompts.json | `character_refs` and `setting_refs` fields drive NODE 6, 8, 13-14 | `specs/manga_character_setting_consistency.md` |
| Batch CSV (`MANGA_MODE_SYSTEM_SPEC.md` §6.5) | Extended with `reference_image`, `expression_ref`, `setting_ref` columns | `MANGA_MODE_SYSTEM_SPEC.md` |

---

*SpiritualTech Systems · ComfyUI Character Reference Workflow Spec v1.0 · Confidential*
