# Manga Character & Setting Consistency System — Architecture Spec

**Version:** 1.0
**Date:** April 2026
**Workstream:** 5
**Authority:** Pearl_Architect
**Status:** Spec draft
**Classification:** Confidential

---

## Overview

This spec defines the **Character & Setting Design Sheet System** — the missing consistency layer that ensures a character looks like themselves across every panel of a series, and that recurring locations maintain visual coherence across chapters and volumes.

The system introduces a new pipeline stage (`CHARACTER_SHEET_BUILD`) that runs once per series after series identity is locked and before any chapter image generation begins. It produces reference images and manifest files consumed by the panel image generation stage.

---

## The Problem

Without this system, every panel generation is a fresh FLUX inference with only a text prompt as character specification. FLUX naturally drifts: the same character description produces different hair length, face shape, skin tone, and outfit across consecutive panels. Over 24 chapters, a character becomes unrecognizable.

This is manga's cardinal consistency requirement and the most common failure mode in AI-generated manga at scale. The MANGA_MODE_SYSTEM_SPEC.md §13 names character continuity as the primary bottleneck. This spec solves it at the reference-image layer, not just the LoRA layer.

---

## Integration Map

This layer slots between Stage 0 (Series Identity Init) and Stage 1 (Batch Composition) from `MANGA_PRODUCTION_PIPELINE_SPEC.md`:

```
STAGE 0: SERIES_IDENTITY_INIT    (specs/manga_series_identity_layer.md)
    ↓  series_identity.yaml locked
STAGE 0.5: CHARACTER_SHEET_BUILD  (THIS SPEC — runs once per series)
    ↓  character_sheet_manifest.json + setting_sheet_manifest.json written
STAGE 1: BATCH_COMPOSITION        (existing)
    ↓  batch includes character_sheet refs
STAGE 2: PROMPT_GENERATION        (existing — extended)
    ↓  panel_prompts.json now includes character_refs and setting_refs
STAGE 3: IMAGE_GENERATION         (extended — IP-Adapter reads from sheets)
    ↓  panels generated with reference image conditioning
STAGE 4: LAYOUT & COMPOSITION     (existing)
STAGE 5: BATCH QC                 (extended — identity drift check added)
```

### Dependency chain (non-negotiable)

```
series_identity.yaml LOCKED
  → character_sheet_manifest.json WRITTEN
  → setting_sheet_manifest.json WRITTEN
    → batch_manifest.json REFERENCES both
      → panel_prompts.json INCLUDES character_refs
        → FLUX generation WITH IP-Adapter conditioning
```

A batch cannot be composed until character sheets are built. The pipeline enforces this:

```python
# batch_composer.py (extended)
for series_id in batch.series_ids:
    assert character_sheet_manifest_exists(series_id), \
        f"Cannot compose batch: character sheets not built for {series_id}"
```

---

## 1. Character Sheet System

### 1.1 What a character sheet is

A character sheet is a set of reference images generated once at series initialization. Every panel that contains a given character passes these images to FLUX via IP-Adapter (or IP-Adapter-Plus), which conditions the generation to match the reference identity.

This is analogous to a professional manga artist's character design sheet — the turnaround drawing they reference every time they draw the character. We generate this once and reuse it forever.

### 1.2 Reference image set per character

```
config/source_of_truth/manga_character_sheets/<series_id>/<character_id>/
    front.png               # full body, forward facing, neutral expression
    side.png                # full body, side profile, neutral
    back.png                # full body, rear view
    three_quarter.png       # 3/4 view (most important for panel use)
    expression_neutral.png  # face close-up, neutral
    expression_happy.png    # face close-up, genuine warmth
    expression_sad.png      # face close-up, grief or disappointment
    expression_angry.png    # face close-up, frustration or resistance
    expression_surprised.png # face close-up, unexpected event
    expression_focused.png  # face close-up, concentration / attention
    sitting.png             # 3/4 view, character seated
    hands_detail.png        # hands close-up — important for hand-heavy scenes
    character_sheet_manifest.json
```

Total: **12 images per character** (configurable; minimum viable set is 8).

For "The Garden at Tidecalm": 4 characters × 12 images = 48 reference images generated once at series start.

### 1.3 Character sheet manifest

```json
{
  "schema_version": "1.0",
  "artifact_type": "character_sheet_manifest",
  "series_id": "garden_at_tidecalm_001",
  "generated_at": "2026-04-17T10:00:00Z",
  "generation_workflow": "character_sheet_generation_v1.json",

  "characters": {
    "sora_hashimoto": {
      "character_id": "sora_hashimoto",
      "display_name": "Sora Hashimoto",
      "generation_prompt_base": "teenage girl, short uneven dark hair, wiry build, oversized dark olive jacket, worn sneakers, iyashikei manga style, soft_rounded linework, watercolor_wash shading, clean white background",
      "reference_images": {
        "front": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/front.png",
        "side": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/side.png",
        "back": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/back.png",
        "three_quarter": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/three_quarter.png",
        "expression_neutral": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/expression_neutral.png",
        "expression_happy": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/expression_happy.png",
        "expression_sad": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/expression_sad.png",
        "expression_angry": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/expression_angry.png",
        "expression_surprised": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/expression_surprised.png",
        "expression_focused": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/expression_focused.png",
        "sitting": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/sitting.png",
        "hands_detail": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/hands_detail.png"
      },
      "ip_adapter_strength": 0.75,
      "lora_ref": "loras/characters/sora_hashimoto_lora.safetensors",
      "lora_strength_model": 0.85,
      "lora_strength_clip": 0.70,
      "visual_evolution_notes": "Volume 2+: jacket removed variant. Volume 3: jacket carried. Request appropriate variant at panel generation time.",
      "volume_variants": {
        "volume_1": "jacket_on",
        "volume_2": "jacket_transitional",
        "volume_3": "jacket_carried_or_absent"
      }
    }
  }
}
```

### 1.4 Storage paths

```
config/
└── source_of_truth/
    └── manga_character_sheets/
        └── <series_id>/
            └── <character_id>/
                ├── front.png
                ├── side.png
                ├── back.png
                ├── three_quarter.png
                ├── expression_neutral.png
                ├── expression_happy.png
                ├── expression_sad.png
                ├── expression_angry.png
                ├── expression_surprised.png
                ├── expression_focused.png
                ├── sitting.png
                ├── hands_detail.png
                └── character_sheet_manifest.json
```

### 1.5 Extended panel_prompts.json field

The `character_refs` field is added to every panel prompt entry that contains a character:

```json
{
  "panel_id": "ch_03_panel_04",
  "series_id": "garden_at_tidecalm_001",
  "chapter_id": "ch_03",
  "visual_prompt": "Sora kneeling in garden soil, hands touching plant roots, focused expression, morning light, iyashikei manga style",
  "camera": "medium_close",
  "characters_in_panel": ["sora_hashimoto"],
  "character_refs": [
    {
      "character_id": "sora_hashimoto",
      "reference_image": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/three_quarter.png",
      "expression_ref": "config/source_of_truth/manga_character_sheets/garden_at_tidecalm_001/sora_hashimoto/expression_focused.png",
      "ip_adapter_strength": 0.75,
      "lora_ref": "loras/characters/sora_hashimoto_lora.safetensors",
      "lora_strength_model": 0.85,
      "volume_variant": "volume_1"
    }
  ],
  "setting_refs": [
    {
      "location_id": "uma_garden",
      "reference_image": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/establishing_shot.png",
      "ip_adapter_strength": 0.45,
      "camera_angle": "medium"
    }
  ],
  "base_seed": 1234,
  "controlnet_strength": 0.6
}
```

---

## 2. Setting Sheet System

### 2.1 What a setting sheet is

A setting sheet is a set of reference images for recurring locations. Passed to IP-Adapter at a lower strength than character sheets (we want atmosphere consistency, not exact replication), they ensure the garden looks like the same garden across chapters — same stone wall texture, same bench position, same light quality.

### 2.2 Reference image set per location

```
config/source_of_truth/manga_setting_sheets/<series_id>/<location_id>/
    establishing_shot.png       # wide — full space visible
    medium_shot.png             # chest-level; typical scene composition
    detail_shot_01.png          # specific recurring detail (e.g., stone wall texture)
    detail_shot_02.png          # second detail (e.g., the bench)
    detail_shot_03.png          # third detail (e.g., the water trough)
    day_variant.png             # standard daytime lighting
    morning_variant.png         # morning fog / soft early light
    evening_variant.png         # golden hour / dusk
    seasonal_spring.png         # spring variant (if series spans seasons)
    seasonal_autumn.png         # autumn variant
    setting_sheet_manifest.json
```

Total: **10 images per location** (adjust based on how often location appears).

For "The Garden at Tidecalm": uma_garden gets full 10-image set; secondary locations get reduced sets (5-7 images).

### 2.3 Setting sheet manifest

```json
{
  "schema_version": "1.0",
  "artifact_type": "setting_sheet_manifest",
  "series_id": "garden_at_tidecalm_001",
  "generated_at": "2026-04-17T10:30:00Z",

  "locations": {
    "uma_garden": {
      "location_id": "uma_garden",
      "display_name": "Uma's Garden",
      "frequency": "high",
      "ip_adapter_strength_default": 0.45,
      "generation_prompt_base": "walled coastal garden, weathered stone walls, overgrown plants, wooden bench listing slightly, stone water trough, iyashikei manga style, soft_rounded linework, watercolor_wash shading, morning soft light",
      "reference_images": {
        "establishing_shot": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/establishing_shot.png",
        "medium_shot": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/medium_shot.png",
        "detail_stone_wall": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/detail_shot_01.png",
        "detail_bench": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/detail_shot_02.png",
        "detail_water_trough": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/detail_shot_03.png",
        "day_variant": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/day_variant.png",
        "morning_fog_variant": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/morning_variant.png",
        "evening_variant": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/evening_variant.png",
        "seasonal_spring": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/seasonal_spring.png",
        "seasonal_autumn": "config/source_of_truth/manga_setting_sheets/garden_at_tidecalm_001/uma_garden/seasonal_autumn.png"
      },
      "use_strength_by_camera": {
        "establishing": 0.55,
        "medium": 0.45,
        "close": 0.30,
        "detail": 0.60
      }
    }
  }
}
```

### 2.4 IP-Adapter strength guidance for settings

Settings use lower IP-Adapter strength than characters — we want recognizable consistency, not exact replication (panels need to show seasonal change, time of day, and story state):

| Camera distance | IP-Adapter strength | Rationale |
|----------------|--------------------|--------------------|
| Establishing shot | 0.55 | Major layout must match |
| Medium shot | 0.45 | Atmosphere consistency, layout flexible |
| Close-up | 0.30 | Detail panels; texture guides but composition free |
| Detail shot | 0.60 | Specific recurring detail must match |

---

## 3. ComfyUI Workflow Design

### 3.1 New workflow: `character_sheet_generation.json`

This workflow generates the reference image set for one character. Run once per character at series initialization.

**Node graph overview:**

```
Load Checkpoint (iyashikei style checkpoint: CounterfeitV3 or equivalent)
    ↓
Load Style LoRA (cozy_style_lora, strength 0.5)
    ↓
Positive Prompt: "{character_description}, character design sheet, white background,
                  turnaround reference sheet, manga style, clean linework,
                  {view_specification}"
    ↓
Negative Prompt: "background, scenery, blurry, watermark, text, multiple views in one image,
                  wrong hair color, anatomical errors"
    ↓
Empty Latent Image (1024x1024 for SDXL, 768x768 for SD 1.5)
    ↓
KSamplerAdvanced (steps: 30, cfg: 7.0, sampler: dpm++2m, seed: {character_base_seed + view_offset})
    ↓
VAE Decode
    ↓
MangaToner (optional: apply light manga line-art post-process)
    ↓
FaceDetailer (eyes and hair repair for close-up expressions)
    ↓
4x-UltimateSD Upscale (for print-quality sheets)
    ↓
Save Image (to character_sheet directory)
```

**Batch execution:** A Python wrapper script calls this workflow 12 times per character, varying the `view_specification` prompt injection and seed offset:

```python
VIEW_SPECS = {
    "front":               ("full body, front view, facing camera", 0),
    "side":                ("full body, side profile, looking left", 1),
    "back":                ("full body, rear view", 2),
    "three_quarter":       ("3/4 view, slight angle left, full body", 3),
    "expression_neutral":  ("face close-up, neutral expression, eye level", 4),
    "expression_happy":    ("face close-up, warm genuine smile, soft eyes", 5),
    "expression_sad":      ("face close-up, downcast eyes, slight lip press", 6),
    "expression_angry":    ("face close-up, furrowed brow, tight jaw, frustrated", 7),
    "expression_surprised":("face close-up, wide eyes, slight open mouth", 8),
    "expression_focused":  ("face close-up, focused concentration, direct gaze", 9),
    "sitting":             ("3/4 view, seated cross-legged on ground, full body", 10),
    "hands_detail":        ("hands close-up, slightly open, soil on fingers", 11),
}

for view_name, (view_prompt, seed_offset) in VIEW_SPECS.items():
    run_comfyui_workflow(
        workflow="character_sheet_generation.json",
        character_prompt=character.generation_prompt_base,
        view_prompt=view_prompt,
        seed=character.base_seed + seed_offset,
        output_path=f".../{character_id}/{view_name}.png"
    )
```

### 3.2 Modified workflow: `panel_generation_with_reference.json`

This extends the existing panel generation workflow by inserting IP-Adapter conditioning between the LoRA layer and the sampler.

**New nodes added to existing panel workflow:**

```
[EXISTING: Load Checkpoint]
[EXISTING: Load Style LoRA]
[EXISTING: Load Character LoRA]
    ↓
[NEW: Load Reference Image]              ← reads character_refs[0].reference_image
    ↓
[NEW: CLIP Vision Encode]                ← ComfyUI-IPAdapter-Plus: CLIPVisionLoader
    ↓
[NEW: IP-Adapter Apply]                  ← IPAdapterApply node
    inputs:
      model: (from LoRA stack)
      ipadapter: (loaded model)
      image: (reference image)
      weight: character_refs[0].ip_adapter_strength  (0.75 for characters)
      weight_type: "linear"
      start_at: 0.0
      end_at: 0.85   # release near end to allow scene-specific detail
    ↓
[NEW: Load Expression Reference]         ← reads character_refs[0].expression_ref
    ↓
[NEW: IP-Adapter Apply (face only)]      ← second IPAdapterApply for face crop
    inputs:
      weight: 0.60
      weight_type: "style transfer"
    ↓
[EXISTING: ControlNet (SDF depth)]      ← from MANGA_MODE_SYSTEM_SPEC.md §6.7
    ↓
[EXISTING: Prompt Input]
    ↓
[EXISTING: KSamplerAdvanced]
    ↓
[NEW: Load Setting Reference (optional)] ← reads setting_refs[0].reference_image
    ↓
[NEW: IP-Adapter Apply (setting)]        ← lower weight (0.45)
    ↓
[EXISTING: MangaToner]
[EXISTING: FaceDetailer]
[EXISTING: Upscale]
[EXISTING: Save]
```

**Multi-character panels:** When `characters_in_panel` contains 2+ characters, use regional/latent-couple conditioning to isolate IP-Adapter influence per panel region:

```
Character 1 IP-Adapter (left region mask)
Character 2 IP-Adapter (right region mask)
    ↓ Combined via attention mask conditioning
KSamplerAdvanced
```

Do not blend character IP-Adapters in the same latent space without region isolation — faces will merge.

### 3.3 Required ComfyUI custom nodes

| Node / Extension | Purpose | Source |
|-----------------|---------|--------|
| `ComfyUI-IPAdapter-Plus` | IP-Adapter reference conditioning | github.com/cubiq/ComfyUI_IPAdapter_plus |
| `CLIPVisionLoader` | Encode reference images for IP-Adapter | Included with IPAdapter-Plus |
| `IPAdapterApply` | Apply reference conditioning to model | Included with IPAdapter-Plus |
| `IPAdapterTiledBatch` | For batch processing multiple references | Included with IPAdapter-Plus |
| `RegionalIPAdapter` | Region-isolated conditioning for multi-character | ComfyUI-Impact-Pack |
| `ControlNet` (depth, canny) | SDF geometric conditioning | Built into ComfyUI |
| `ComfyUI-MangaToner` | Line-art manga post-processing | Third party |
| `FaceDetailer` | Face/eye/hair repair | ComfyUI-Impact-Pack |
| `4x-UltimateSD` | Upscale to print quality | Ultimate SD Upscale node |

---

## 4. Pipeline Integration

### 4.1 New pipeline stage: `CHARACTER_SHEET_BUILD`

```python
# scripts/manga/character_sheet_build.py

def run_character_sheet_build(series_id: str) -> CharacterSheetManifest:
    """
    Runs once per series. Generates all reference images and writes manifests.
    Prerequisites: series_identity.yaml must be locked.
    """
    identity = load_series_identity(series_id)
    assert identity.validation_status == "locked", \
        "Series identity must be locked before building character sheets"

    manifest = CharacterSheetManifest(series_id=series_id)

    # 1. Generate character sheets
    for character in identity.characters.values():
        sheets = generate_character_sheet(
            character_id=character.character_id,
            generation_prompt_base=build_character_prompt(character),
            base_seed=character_seed_from_id(character.character_id),
            workflow="character_sheet_generation.json",
            output_dir=character_sheet_path(series_id, character.character_id)
        )
        manifest.add_character(character.character_id, sheets)

    # 2. Generate setting sheets
    for location in identity.setting_bible.locations.values():
        sheets = generate_setting_sheet(
            location_id=location.location_id,
            generation_prompt_base=build_setting_prompt(location, identity.brand_id),
            workflow="character_sheet_generation.json",  # same workflow, different prompts
            output_dir=setting_sheet_path(series_id, location.location_id)
        )
        manifest.add_location(location.location_id, sheets)

    # 3. Write manifests
    write_manifest(manifest, character_sheet_manifest_path(series_id))
    write_manifest(build_setting_manifest(series_id), setting_sheet_manifest_path(series_id))

    return manifest
```

### 4.2 Integration with Stage 2 (Prompt Generation)

The `visual_prompt_compiler.py` is extended to inject character and setting refs into each panel prompt:

```python
# pearl_prime/manga/visual_prompt_compiler.py (extended)

def compile_panel_prompt(panel_script: PanelScript, series_id: str) -> PanelPrompt:
    """Extended to include character_refs and setting_refs."""
    char_manifest = load_character_sheet_manifest(series_id)
    set_manifest = load_setting_sheet_manifest(series_id)

    character_refs = []
    for char_id in panel_script.characters_in_panel:
        char_entry = char_manifest.characters[char_id]
        character_refs.append({
            "character_id": char_id,
            "reference_image": select_reference_image(char_entry, panel_script),
            "expression_ref": select_expression_ref(char_entry, panel_script.emotion),
            "ip_adapter_strength": char_entry.ip_adapter_strength,
            "lora_ref": char_entry.lora_ref,
            "lora_strength_model": char_entry.lora_strength_model,
            "volume_variant": get_volume_variant(panel_script.chapter_id, char_entry)
        })

    setting_refs = []
    for loc_id in panel_script.locations_in_panel:
        if loc_id in set_manifest.locations:
            loc_entry = set_manifest.locations[loc_id]
            setting_refs.append({
                "location_id": loc_id,
                "reference_image": select_setting_reference(loc_entry, panel_script.camera),
                "ip_adapter_strength": loc_entry.use_strength_by_camera.get(
                    panel_script.camera, loc_entry.ip_adapter_strength_default
                )
            })

    return PanelPrompt(
        ...existing_fields...,
        character_refs=character_refs,
        setting_refs=setting_refs
    )

def select_reference_image(char_entry, panel_script):
    """Pick the most appropriate reference image given camera and body framing."""
    if panel_script.camera in ["close_up", "extreme_close_up"]:
        return char_entry.reference_images["expression_neutral"]  # face crop
    elif panel_script.camera in ["medium", "medium_close"]:
        return char_entry.reference_images["three_quarter"]
    else:
        return char_entry.reference_images["front"]

def select_expression_ref(char_entry, emotion):
    """Map panel emotion to expression reference image."""
    emotion_map = {
        "neutral":    "expression_neutral",
        "happy":      "expression_happy",
        "sad":        "expression_sad",
        "angry":      "expression_angry",
        "surprised":  "expression_surprised",
        "focused":    "expression_focused",
        "resigned":   "expression_sad",
        "determined": "expression_focused",
        "relieved":   "expression_happy",
    }
    key = emotion_map.get(emotion, "expression_neutral")
    return char_entry.reference_images[key]
```

### 4.3 Integration with Stage 5 (QC)

The QC agent gets a new check: **Identity Drift Detection**.

```python
# pearl_prime/manga/qc/identity_drift_check.py

def check_identity_drift(book_id: str, series_id: str) -> DriftReport:
    """
    For each character in each panel, compare rendered panel against character sheet.
    Uses CLIP embedding cosine similarity.
    Gate: D2 (Identity Drift) from MANGA_MODE_SYSTEM_SPEC.md §7
    Threshold: 0.82 minimum match score.
    """
    char_manifest = load_character_sheet_manifest(series_id)
    report = DriftReport(book_id=book_id)

    for chapter in load_book_chapters(book_id):
        for panel in chapter.panels:
            for char_ref in panel.character_refs:
                rendered_panel = load_panel_image(panel.panel_id)
                reference_image = load_image(char_ref.reference_image)

                similarity = clip_cosine_similarity(
                    crop_character_region(rendered_panel, char_ref.character_id),
                    reference_image
                )

                if similarity < 0.82:
                    report.add_drift_failure(
                        panel_id=panel.panel_id,
                        character_id=char_ref.character_id,
                        similarity_score=similarity,
                        threshold=0.82
                    )

    return report
```

---

## 5. Economics

### 5.1 Images per character sheet

Recommended set: **12 images per character** (as defined in §1.2).

Minimum viable set (short series or secondary characters): **8 images**
- front, side, three_quarter
- expression_neutral, expression_happy, expression_sad, expression_focused
- sitting

Extended set (protagonist in long series): **15 images**
- All 12 above
- running_motion (for action-adjacent panels)
- close_face_detail (for intimate emotional panels)
- additional_volume_variant (e.g., jacket-off variant for Sora in volume 2+)

### 5.2 Cost estimate (RunComfy / RunPod)

Parameters:
- SDXL FLUX at RunComfy API rate: approximately $0.007 per image at 1024x1024, 30 steps
- Upscaling adds ~20% overhead

| Item | Images | Cost estimate |
|------|--------|---------------|
| Character sheet (12 images × 4 characters) | 48 | ~$0.40 |
| Setting sheet (10 images × 4 locations) | 40 | ~$0.34 |
| **Total per series** | **88** | **~$0.74** |

This is essentially zero cost relative to chapter generation. A 24-chapter series generates approximately 24 × 9 = 216 panels minimum. Character sheet build adds ~40% more images but is done once and reused across all chapters.

### 5.3 Time estimate (1 character sheet)

At RunComfy batch processing with 6 workers:
- 12 images, ~15 seconds each at batch throughput
- **Character sheet for 1 character: approximately 3 minutes**
- Full series (4 characters + 4 locations = 88 images): approximately 22 minutes

This is a one-time upfront cost before any chapter generation begins.

### 5.4 LoRA training vs. IP-Adapter: trade-off analysis

| Approach | Consistency | Setup time | Cost | Best for |
|----------|-------------|------------|------|----------|
| IP-Adapter alone | ~75-80% | 30 min | $1 | Short series, secondary characters, prototyping |
| LoRA alone | ~85% | 4-8 hours training | $10-30 | Mid-length series, key characters |
| IP-Adapter + LoRA | ~90-93% | 4-8 hours (LoRA) | $15-35 | Long series, protagonist |
| IP-Adapter + LoRA + SDF | ~95%+ | 6-12 hours | $20-50 | Series with 100+ panels per character |

**Recommendation by series length:**

- Short series (1 volume, < 100 character panels): IP-Adapter alone. Fast, cheap, acceptable consistency.
- Medium series (2-3 volumes, 100-300 panels): IP-Adapter + LoRA. Train LoRA once, amortize across entire series.
- Long series (4+ volumes, 300+ panels): IP-Adapter + LoRA + SDF. Full stack. The SDF investment pays back across hundreds of panels.

For "The Garden at Tidecalm" (3 volumes, ~200 panels per main character across full run): **IP-Adapter + LoRA recommended.** SDF optional; consider adding in volume 2 if budget allows.

LoRA training pipeline details are in `MANGA_MODE_SYSTEM_SPEC.md` §16.2.

---

## 6. Storage Layout (complete)

```
config/
└── source_of_truth/
    ├── manga_series/                          # Series identity layer
    │   └── <series_id>/
    │       └── series_identity.yaml
    │
    ├── manga_character_sheets/                # THIS SYSTEM
    │   └── <series_id>/
    │       ├── character_sheet_manifest.json
    │       └── <character_id>/
    │           ├── front.png
    │           ├── side.png
    │           ├── back.png
    │           ├── three_quarter.png
    │           ├── expression_neutral.png
    │           ├── expression_happy.png
    │           ├── expression_sad.png
    │           ├── expression_angry.png
    │           ├── expression_surprised.png
    │           ├── expression_focused.png
    │           ├── sitting.png
    │           └── hands_detail.png
    │
    └── manga_setting_sheets/                  # THIS SYSTEM
        └── <series_id>/
            ├── setting_sheet_manifest.json
            └── <location_id>/
                ├── establishing_shot.png
                ├── medium_shot.png
                ├── detail_shot_01.png
                ├── detail_shot_02.png
                ├── detail_shot_03.png
                ├── day_variant.png
                ├── morning_variant.png
                ├── evening_variant.png
                ├── seasonal_spring.png
                └── seasonal_autumn.png

models/
└── loras/
    └── characters/
        └── <series_id>/
            └── <character_id>_lora.safetensors   # trained after sheet generation

config/manga/sdf/                              # from MANGA_MODE_SYSTEM_SPEC.md §6.7
    └── training/
        └── <series_id>_<character_id>_sdf_model.pt
```

---

## 7. Failure Modes & Recovery

| Failure | Detection | Recovery |
|---------|-----------|---------|
| Identity drift in panel | QC Stage 5 drift check (< 0.82 similarity) | Regenerate panel with increased IP-Adapter strength (0.85) or swap reference image |
| Character sheet generation failure | Sheet manifest validation: check all 12 images exist | Re-run `character_sheet_build.py` for affected character |
| Wrong expression reference selected | Visual review / similarity check | Update `select_expression_ref()` mapping; regenerate affected panels |
| Setting sheet not consulted for location | Panel prompt validation: `setting_refs` empty for known location | Extend `compile_panel_prompt()` to auto-detect locations from scene description |
| Multi-character face blending | Drift check detects two characters merging | Enable regional IP-Adapter with explicit region masks; regenerate |
| LoRA drift on extreme pose | Drift check below threshold on action-heavy panels | Lower LoRA strength (0.70), increase SDF ControlNet strength (0.70); regenerate |

---

## 8. What This Spec Does NOT Cover

- LoRA training pipeline details (covered in `MANGA_MODE_SYSTEM_SPEC.md` §16.2)
- SDF geometric conditioning details (covered in `MANGA_MODE_SYSTEM_SPEC.md` §6.7)
- ComfyUI node graph notation (covered in `specs/comfyui_workflow_character_reference.md`)
- Series identity generation (covered in `specs/manga_series_identity_layer.md`)
- Brand DNA visual style (covered in `MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md`)

---

*SpiritualTech Systems · Character & Setting Consistency System Spec v1.0 · Confidential*
