# Manga Mode — System Spec

**Purpose:** Define a deterministic `manga_mode` for Phoenix Omega so the existing atom corpus, teacher system, arc architecture, video pipeline, and translation infrastructure can produce illustrated manga books, webtoon episodes, and visual practice cards at global scale — without building a new system.

**Authority:** This spec. Related authorities: [specs/MUSICIAN_MODE_SYSTEM_SPEC.md](./MUSICIAN_MODE_SYSTEM_SPEC.md) (mode precedent), [specs/GEN_Z_VISUAL_PIPELINE_DEV_SPEC_v1.1.md](./GEN_Z_VISUAL_PIPELINE_DEV_SPEC_v1.1.md) (visual layer), [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) (pipeline), [docs/ATOM_NATIVE_MODULAR_FORMATS.md](../docs/ATOM_NATIVE_MODULAR_FORMATS.md) (format building blocks).

**Status:** Spec draft. Not yet built.

**Deep Research Sources:**
- `docs/deep_research_manga_gemini.txt` — Primary for US, EU, global macro. Google Gemini AI.
- `docs/deep_research_manga_deepseek.txt` — Primary for China, regional mechanics. DeepSeek AI.
- `docs/deep_research_manga_rakuten.txt` — Primary for Japan. Rakuten AI. **Pending delivery.**
- `docs/manga_tech_notes.txt` — Agent architecture, ComfyUI pipeline, Golden Phoenix manga gates, LoRA strategy.

**Related Specs:**
- [MANGA_MODE_STRATEGY.docx](../docs/MANGA_MODE_STRATEGY.docx) — Business strategy and market analysis
- [VIDEO_PIPELINE_SPEC.md](../docs/VIDEO_PIPELINE_SPEC.md) — Video pipeline (manga-derived shorts)
- [VIDEO_IMAGE_MASTER_PROMPT_SPEC.md](../docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md) — Visual prompt patterns

---

## 1. Core intent

Manga Mode treats illustrated panels as deterministic visual renderings of the existing atom corpus.

The system does **not** generate new narrative content for manga. It takes the same atoms (HOOK, SCENE, STORY, REFLECTION, EXERCISE, INTEGRATION) that Pearl Prime compiles into prose books and renders them as illustrated manga pages instead — using visual prompts derived from atom metadata, teacher identity, and style archetype config.

Manga Mode has three explicit branches:

- `full_volume` mode — arc-driven illustrated books (120–200 pages, 3–6 panels/page)
- `webtoon_episode` mode — vertical scroll episodes (50–80 panels, episodic drops)
- `visual_card` mode — single-skill illustrated practice cards (3–5 pages, high visual impact)

The strongest product structure is:

```text
atom = semantic unit (meaning, mechanism, practice)
panel = visual rendering of atom (composition, camera, character, text overlay)
page = layout of panels (flow, rhythm, readability)
chapter = arc-aligned page sequence (emotional curve)
volume = complete illustrated book (teacher-pure, style-locked)
```

---

## 2. Invariants

When `manga_mode=true`:

- No runtime visual improvisation. Visual prompts are compiled from atom metadata + style archetype + teacher identity. Same inputs → same visual prompts.
- Every panel traces to exactly one atom (or atom fragment for multi-panel STORY sequences). No orphan panels.
- Every volume, episode, or card has exactly one `style_archetype_id` locked for its entire duration. No mid-volume style switching.
- Every teacher has exactly one `character_design_packet` per style archetype. Character identity is locked: face, hair, outfit, expression range, color palette, silhouette.
- Teacher-pure rule carries over: illustrated content uses only that teacher's atoms and doctrine. No cross-teacher characters in the same volume.
- Every visual prompt includes: `atom_id`, `atom_type`, `mechanism_depth`, `cost_intensity`, `identity_stage`, `teacher_id`, `style_archetype_id`, `camera_instruction`, `composition_rule`. Full provenance.
- Arc-first rule carries over: every full_volume requires an arc. No arc = no compile.
- Gate system applies: structural entropy, duplication detection, and quality gates must pass on visual prompt sequences, not just prose.
- Text overlays (speech bubbles, captions, SFX) come from atom text, never generated. Translation pipeline produces locale-specific overlays from the same atom source.
- Every production manga must include delivery assets: EPUB (illustrated), vertical scroll HTML, or print-ready PDF. No placeholder pages in delivered output.

---

## 3. Pipeline integration

Manga Mode extends the existing Pearl Prime pipeline. It does **not** create a parallel pipeline.

### 3.1 Runtime flow

```
scripts/run_pipeline.py --output-format manga_full_volume --teacher ahjan --arc arc_id
    │
    ├── 1. Load freeze config (existing)
    │      pearl_prime/modular_format_freeze.py
    │      → loads manga format definitions from v4_freeze_modular_formats.yaml
    │
    ├── 2. Validate teacher (existing)
    │      → resolves teacher bank + character_design_packet
    │
    ├── 3. Rewrite Stage-2 plan (extended)
    │      apply_output_format_to_plan()
    │      → normalizes to page count + panels/page + panel layout templates
    │      → slot template defines visual rhythm (splash → narrative → reflection → practice)
    │
    ├── 4. Compile (existing atom assembly)
    │      → CompiledManga: atom sequences + panel mapping + arc alignment
    │
    ├── 5. Visual prompt compilation (NEW)
    │      pearl_prime/manga/visual_prompt_compiler.py
    │      → reads atom metadata (mechanism_depth, cost_intensity, identity_stage)
    │      → reads style archetype config
    │      → reads teacher character_design_packet
    │      → reads camera/composition config (extends emotion_to_camera_overrides.yaml)
    │      → outputs: deterministic visual prompt per panel
    │
    ├── 6. Panel rendering (NEW)
    │      pearl_prime/manga/panel_renderer.py
    │      → sends visual prompts to render backend (ComfyUI / SD + LoRA)
    │      → applies character LoRA + style LoRA per prompt
    │      → outputs: rendered panel images
    │
    ├── 7. Page assembly (NEW)
    │      pearl_prime/manga/page_assembler.py
    │      → applies layout template (panels → page grid or vertical scroll)
    │      → overlays text (speech bubbles, captions, SFX) from atom text
    │      → applies locale-specific text from translation pipeline
    │      → outputs: assembled pages
    │
    └── 8. Package (extended)
           → outputs: EPUB (illustrated), vertical scroll HTML, print-ready PDF
           → provenance: atoms_model, atoms_root_hash, style_archetype_id,
                         character_packet_hash, visual_prompt_hashes, panel_render_hashes
```

### 3.2 New modules

| Module | Location | Responsibility |
|--------|----------|---------------|
| `visual_prompt_compiler.py` | `pearl_prime/manga/` | Atom metadata → deterministic visual prompt |
| `panel_renderer.py` | `pearl_prime/manga/` | Visual prompt → rendered panel image |
| `page_assembler.py` | `pearl_prime/manga/` | Panels + text overlays → assembled pages |
| `manga_format_freeze.py` | `pearl_prime/manga/` | Manga-specific format validation (extends modular_format_freeze) |

### 3.3 New config files

| Config | Location | Contents |
|--------|----------|----------|
| `style_archetypes.yaml` | `config/manga/` | 8 style archetype definitions (visual traits, prompt blocks, LoRA refs) |
| `panel_layouts.yaml` | `config/manga/` | Panel layout templates per format (grid patterns, vertical scroll specs) |
| `character_design_packets/` | `config/manga/characters/` | Per-teacher character identity (face, hair, outfit, expressions, silhouette) |
| `camera_language.yaml` | `config/manga/` | Camera → visual prompt mappings (extends video emotion_to_camera_overrides) |
| `manga_gates.yaml` | `config/manga/` | Manga-specific gate definitions (see §7) |
| `comfyui_workflow.json` | `config/manga/` | ComfyUI workflow template for batch panel rendering |
| `sdf/training/` | `config/manga/sdf/` | Per-teacher reference views + trained SDF models |
| `sdf/inference/` | `config/manga/sdf/` | SDF projector, deformer, validator scripts |

---

## 4. Atom-to-panel mapping

Each atom type maps to a specific panel function. This mapping is deterministic.

### 4.1 Panel types

| Atom Type | Panel Function | Panel Count | Camera Default | Purpose |
|-----------|---------------|-------------|----------------|---------|
| HOOK (25–55 words) | Splash panel | 1 (full-page or half-page) | Wide or dramatic angle | High-impact visual, minimal text, reader recognition |
| SCENE (60–120 words) | Environment panel | 1–2 | Wide establishing shot | Atmosphere, grounding, sensory anchor |
| STORY (variable) | Narrative sequence | 4–6 panels | Mixed: close-up, medium, wide | Inciting incident → escalation → turning point → cost |
| REFLECTION (variable) | Teacher panel | 1–2 | Close-up on teacher character | Speech bubble with insight, character-consistent design |
| EXERCISE (80–180 words) | Practice spread | 2–4 panels | Medium, instructional framing | Step-by-step illustrated guide, somatic cues visualized |
| INTEGRATION (variable) | Closing panel | 1 | Pull-back or motif callback | Visual motif callback, forward-motion composition |

### 4.2 STORY atom decomposition

STORY atoms are multi-panel sequences. The decomposition follows the atom's internal narrative structure:

```
STORY atom internal structure → panel mapping:
  inciting_incident  → Panel 1: establishing shot, character enters situation
  mechanism_action   → Panel 2–3: escalation, body-state visualization
  turning_point      → Panel 4: dramatic panel (larger, high contrast)
  cost_or_lesson     → Panel 5–6: aftermath, emotional weight
```

Panel count scales with `mechanism_depth`:
- `mechanism_depth: shallow` → 4 panels
- `mechanism_depth: moderate` → 5 panels
- `mechanism_depth: deep` → 6 panels

### 4.3 Visual metadata usage

The 99.4% metadata coverage on atoms (2,379 of 2,393 as of March 2026) provides per-panel visual parameters:

| Metadata Field | Visual Effect |
|---------------|--------------|
| `mechanism_depth` | Panel count for STORY sequences; visual complexity |
| `cost_intensity` | Panel darkness, contrast, emotional weight of composition |
| `identity_stage` | Character posture and expression evolution across book |
| Teacher doctrine | Character design, color palette, visual symbols |
| Engine type | Environmental mood (shame → confined spaces; grief → open/empty; spiral → disorienting angles) |

---

## 5. Style archetype system

Eight scalable style archetypes, derived from deep research convergence (Gemini + DeepSeek). Each archetype defines a complete visual language.

### 5.1 Archetype definitions

```yaml
# config/manga/style_archetypes.yaml

archetypes:
  hyper_clean_cinematic:
    display_name: "Hyper-Clean Anime Cinematic"
    visual_traits: "Glossy textures, lens flares, detailed eyes, full-color, high-budget animation look"
    line_quality: clean_digital
    color_mode: full_color
    shading: cel_shaded_plus_lighting
    panel_density: medium (3-4/page)
    target_audience: [gen_z_action, global]
    best_regions: [us, eu, sea]
    checkpoint_ref: anime_cinematic_v2
    style_lora_ref: cinematic_style_lora
    teacher_fit: [ra, master_wu]

  webtoon_vertical_romance:
    display_name: "Webtoon Vertical Romance Drama"
    visual_traits: "Soft focus, fashion emphasis, close-up reactions, atmospheric backgrounds"
    line_quality: clean_soft
    color_mode: full_color
    shading: soft_gradient
    panel_density: low (1-2 per screen-height)
    target_audience: [gen_z_female, asia]
    best_regions: [kr, us, sea, cn]
    checkpoint_ref: webtoon_romance_v1
    style_lora_ref: romance_style_lora
    teacher_fit: [maat, miki]

  meme_chaotic_humor:
    display_name: "Meme-Driven Chaotic Humor"
    visual_traits: "Rough linework, exaggerated expressions, limited palette, reaction-image-ready"
    line_quality: rough_expressive
    color_mode: limited_palette
    shading: flat
    panel_density: high (4-6/page, 4-koma style)
    target_audience: [gen_z_comedy, gen_alpha]
    best_regions: [global]
    checkpoint_ref: manga_sketch_v1
    style_lora_ref: null
    teacher_fit: [practice_cards]

  dark_psychological:
    display_name: "Dark Psychological Minimalist"
    visual_traits: "High contrast B&W, sparse backgrounds, focus on character psychology, disturbing imagery"
    line_quality: heavy_ink
    color_mode: black_and_white
    shading: high_contrast_halftone
    panel_density: medium (3-5/page)
    target_audience: [gen_z_older, niche]
    best_regions: [us, eu, jp]
    checkpoint_ref: manga_bw_v2
    style_lora_ref: dark_style_lora
    teacher_fit: [ahjan]

  cozy_iyashikei:
    display_name: "Cozy Slice-of-Life Healing"
    visual_traits: "Soft rounded shapes, pastel palette, fluffy aesthetic, gentle ink washes"
    line_quality: soft_rounded
    color_mode: pastel
    shading: watercolor_wash
    panel_density: low-medium (2-4/page)
    target_audience: [gen_z_anxiety, gen_alpha_safe]
    best_regions: [global]
    checkpoint_ref: iyashikei_v1
    style_lora_ref: cozy_style_lora
    teacher_fit: [sai_maa, joshin]

  power_progression:
    display_name: "Power Fantasy Progression (System/LitRPG)"
    visual_traits: "Dynamic action, UI/HUD overlays, status screens, level-up visuals"
    line_quality: clean_digital
    color_mode: full_color
    shading: cel_shaded
    panel_density: medium-high (4-5/page)
    target_audience: [gen_z_male, gamers]
    best_regions: [us, kr, cn, global]
    checkpoint_ref: action_manga_v2
    style_lora_ref: litrpg_style_lora
    teacher_fit: [exercise_atoms_as_skill_unlocks]

  social_media_simulacra:
    display_name: "Social Media Simulacra"
    visual_traits: "Mimics phone UI, text messages, Instagram stories, TikTok vertical video within comic"
    line_quality: mixed_digital
    color_mode: full_color
    shading: flat_ui
    panel_density: variable (screen-mimetic)
    target_audience: [gen_z_core]
    best_regions: [global]
    checkpoint_ref: mixed_media_v1
    style_lora_ref: null
    teacher_fit: [pearl_news_format]

  interactive_branching:
    display_name: "Interactive/Branching Paths"
    visual_traits: "Poll/choice overlays, AR-ready panels, multi-path indicators"
    line_quality: clean_digital
    color_mode: full_color
    shading: cel_shaded
    panel_density: medium (3-4/page)
    target_audience: [gen_alpha, interactive]
    best_regions: [us, cn]
    checkpoint_ref: anime_v2
    style_lora_ref: null
    teacher_fit: [arc_system_choose_path]
```

### 5.2 Style lock rule

Once a `style_archetype_id` is assigned to a volume, episode, or card:
- The same checkpoint, style LoRA, line quality, color mode, and shading mode apply to every panel.
- Character LoRAs are stacked on top of the style LoRA (character LoRA strength > style LoRA strength; see §6.2).
- Style changes are only allowed at **arc boundaries** (between volumes, not within).
- Gate C1 (Style Distinctiveness) and M3 (Style Lock Memory) enforce this.

---

## 6. Render backend (ComfyUI + SD + LoRA)

Source: `docs/manga_tech_notes.txt` — ComfyUI pipeline specification.

### 6.1 Architecture

```
Layer 1 — Intelligence (Phoenix agents)
  story_architect → panel_script → visual_prompt_compiler
  Output: structured panel data (panel_id, character_ids, emotion, camera, scene)

Layer 2 — Prompt Compiler (NEW)
  visual_prompt_compiler.py
  Converts structured data → SD prompt blocks:
    FINAL_PROMPT = CHARACTER_BLOCK + STYLE_BLOCK + CAMERA_BLOCK + SCENE_BLOCK + EMOTION_BLOCK

Layer 2.5 — SDF Geometric Prior (NEW)
  sdf_projector.py
  Projects neural SDF → 2D contour/depth maps per panel camera angle
  Provides: ControlNet depth conditioning + silhouette enforcement
  Prevents: character drift across 1,000+ panels (LoRA alone: ~85%; SDF+LoRA: 95%+)

Layer 3 — ComfyUI Render Engine
  Load Checkpoint → Style LoRA → Character LoRA(s) → SDF ControlNet → IPAdapter
    → Prompt Input → KSamplerAdvanced → MangaToner → FaceDetailer → Upscale → Save
```

### 6.2 LoRA strategy

| LoRA Type | Weight Range | Purpose |
|-----------|-------------|---------|
| Character LoRA | model: 0.8–1.0, clip: 0.6–0.8 | Identity lock (face, hair, outfit, silhouette) |
| Style LoRA | model: 0.4–0.6, clip: 0.4–0.6 | Visual style enforcement |
| Props/Clothes LoRA (optional) | model: 0.2–0.4, clip: 0.2–0.4 | Specific outfit variants |

**Character LoRA is always stronger than style LoRA.** Identity > style.

**Multi-character scenes:** Use regional/latent-couple conditioning to isolate character LoRAs per panel region. Do not blend character LoRAs in the same latent space.

### 6.3 Prompt structure

```
Positive:
  {CHAR_TOKEN}, {character_description},
  {style_block},
  {scene_description}, {camera_instruction},
  emotion: {emotion_state}

Negative:
  extra limbs, deformed hands, watermark, text, logo,
  wrong hairstyle, {character_forbidden_variants}
```

### 6.4 Seed control

```
scene_seed = base_seed + scene_id
panel_seed = scene_seed + panel_id
```

Same scene + same camera → same seed (visual coherence within scenes).

### 6.5 Batch pipeline

Input CSV (driven by visual_prompt_compiler.py):

```
panel_id,character_ids,style_id,scene,emotion,camera,seed
ch1_p01,ahjan,dark_psychological,confined room night,neutral,wide,1234
ch1_p02,ahjan,dark_psychological,confined room detail,tension,close,1235
```

Flow: `CSV → ComfyUI batch node → Render → Visual QA → Save`

### 6.6 B&W vs color

Two render branches in the same workflow:
- **B&W:** B&W manga checkpoint + B&W style LoRA + halftone emphasis
- **Color:** Color anime checkpoint + color style LoRA + cel-shading

Same character LoRAs across both branches. A `color_mode` column in the batch CSV selects the branch per panel.

### 6.7 SDF consistency layer (geometric prior for character identity)

LoRAs lock style and facial features, but they drift under extreme poses, camera angles, and multi-panel scale. Signed Distance Fields (SDFs) solve this by providing a **geometric prior** — a mathematically consistent representation of the character's shape that survives deformation across thousands of panels.

**Why SDF matters for manga at scale:**
- LoRA alone achieves ~85% consistency across 1,000+ panels. SDF + LoRA pushes this to 95%+.
- SDFs enforce volume-preserving deformations: a character's silhouette remains mathematically consistent regardless of viewpoint, pose, or motion — critical for action sequences and dynamic manga panels.
- For B&W manga specifically, SDF-projected contours produce clean inked lines that match hand-drawn consistency across multi-page spreads.

#### 6.7.1 SDF representation

Train a neural network to predict SDF values for each teacher character's body geometry:
- Input: multi-view reference images from the character design packet (front, side, back, 3/4 views)
- Output: implicit surface representation where SDF(x) = signed distance from point x to the character surface
- The SDF captures: face proportions, hair volume, body silhouette, outfit boundaries
- Exaggerated manga features (large eyes, dynamic hair, stylized proportions) are encoded natively — the SDF learns the character as designed, not as anatomically correct

#### 6.7.2 Integration with ComfyUI render stack

SDF operates as an additional conditioning layer in the ComfyUI graph, between the prompt compiler and the sampler:

```
Load Checkpoint
  → Load Style LoRA
  → Load Character LoRA(s)
  → SDF Conditioning Layer (NEW)     ← neural SDF projected to 2D depth/contour map
  → IPAdapter + InstantID (identity)  ← face/identity reinforcement
  → ControlNet (depth from SDF)       ← pose + geometry enforcement
  → Prompt Input (from compiler)
  → KSamplerAdvanced
  → MangaToner (line art post-process) ← manga-specific polish
  → FaceDetailer (eyes/hair fix)
  → 4x-UltimateSD Upscale
  → Save
```

**Key ComfyUI custom nodes required:**
- `ComfyUI-IPAdapter-Plus` — face/identity lock (weight: 0.8)
- `ControlNet` — depth/canny from SDF-derived maps (strength: 0.6)
- `ComfyUI-MangaToner` — line art effects (num_zones: 5–8, edge_strength: 1.2)
- `FaceDetailer` — eyes and hair consistency repair
- `4x-UltimateSD` — upscale for print-ready resolution
- SDF preprocessor node (custom PyTorch) — projects neural SDF to 2D conditioning maps

#### 6.7.3 SDF workflow for manga

1. **Fit SDF from character reference sheets.** Use Diffusion-SDF to train from the character design packet's multi-view images (front/side/back). Low-res base SDF, then super-resolve for high-fidelity line art.
2. **Project 3D SDF → 2D contour maps.** For each panel, project the SDF onto the camera plane defined by the panel's `camera_instruction`. This produces a depth map and edge contour that ControlNet uses as geometric conditioning.
3. **Condition Stable Diffusion with SDF modulation.** In img2img mode, use low denoising strength (0.3–0.5) with the SDF contour as ControlNet depth input. The SDF enforces shape geometry while the LoRA enforces style and identity.
4. **Batch thousands of panels.** SDF latents can be procedurally deformed (pose changes, muscle flexing, hair motion) without retraining per panel. The CSV batch pipeline adds an `sdf_pose_mod` column for per-panel deformation parameters.

#### 6.7.4 SDF + LoRA interaction

| Layer | Role | Strength | What it locks |
|-------|------|----------|---------------|
| Neural SDF | Geometric prior | ControlNet 0.5–0.7 | Silhouette, proportions, volume, contour lines |
| Character LoRA | Identity features | model 0.8–1.0 | Face, hair, outfit texture, expression range |
| Style LoRA | Art direction | model 0.4–0.6 | Line quality, shading, color mode |
| IPAdapter + InstantID | Face reinforcement | 0.7–0.8 | Facial geometry consistency in close-ups |

**Conflict resolution:** SDF provides the geometric foundation (shape), LoRA provides the surface detail (style + identity). When they conflict (e.g., LoRA wants to drift a face shape), SDF wins on geometry, LoRA wins on texture. ControlNet strength mediates: higher strength = stricter geometric lock, lower = more LoRA freedom.

#### 6.7.5 Manga-specific SDF adaptations

- **2D contour extraction:** Project 3D SDF onto 2D for manga-style edge detection. The SDF zero-crossing produces clean contours that match professional inked lines — no ControlNet canny artifacts.
- **Screentone compatibility:** SDF depth maps drive screentone density in B&W manga (deeper = darker screentone). Integrates with MangaToner node.
- **Speed line interaction:** For action panels, SDF silhouette defines the speed-line exclusion zone. Character contour stays sharp while background streaks.
- **Expression sheet validation:** SDF encodes the character's expression range. Gate D2 (Identity Drift) can compare rendered panel SDF against the reference SDF to detect drift numerically, not just perceptually.

#### 6.7.6 Extended batch CSV with SDF

```
panel_id,character_ids,style_id,scene,emotion,camera,seed,sdf_pose_mod,controlnet_strength
ch1_p01,ahjan,dark_psychological,confined room night,neutral,wide,1234,standing_front,0.6
ch1_p02,ahjan,dark_psychological,confined room detail,tension,close,1235,leaning_forward,0.7
ch1_p03,ahjan,dark_psychological,mirror scene,shame,close_up,1236,head_down_hands_visible,0.5
```

#### 6.7.7 SDF training pipeline

```
config/manga/sdf/
  training/
    {teacher_id}_reference_views/     # multi-view reference images (from character_design_packet)
    {teacher_id}_sdf_model.pt         # trained neural SDF weights
    {teacher_id}_expression_sheet.pt  # expression-range SDF variants
  inference/
    sdf_projector.py                  # 3D SDF → 2D contour/depth for ControlNet
    sdf_deformer.py                   # pose modification without retraining
    sdf_validator.py                  # compares rendered panel SDF against reference (for Gate D2)
```

**Training cost:** One SDF per teacher character. ~2–4 hours on single GPU per character from reference sheet. Train once, use across all panels for that character. Retrain only when character design changes.

---

## 7. Gate system (Golden Phoenix Manga Gates)

Source: `docs/manga_tech_notes.txt` §8 — Manga version of Golden Phoenix.

Manga Mode adds 22 gates organized in 6 groups. These run alongside the existing 51 CI checks. They do not replace any existing gate.

### Gate Group A — Market-Fit Gates

| Gate | Fails if |
|------|----------|
| A1: Audience Precision | Target audience is vague: must specify age_band, region, platform, tone_band, darkness_band, pacing_target |
| A2: Hook Clarity | Concept cannot be expressed in one strong sentence (HOOK atom test) |
| A3: Emotional Need | Volume does not clearly serve one of: escapist_fantasy, identity_validation, emotional_comfort, aspirational_power, cathartic_intensity, social_resonance |

### Gate Group B — Story Quality Gates

| Gate | Fails if |
|------|----------|
| B1: Series Engine | No repeatable chapter engine (for webtoon_episode mode) |
| B2: Character Attachment | Top 2 characters score below threshold on: recognizability, emotional_projection, fandom_potential, relationship_dynamics |
| B3: Earned Ending | Emotional payoff not causally built by prior beats (existing arc gate extension) |
| B4: Retention Rhythm | No hook in first 3 panels; dead zone > 2 panels without turn; no chapter-end pull |

### Gate Group C — Visual Identity Gates

| Gate | Fails if |
|------|----------|
| C1: Style Distinctiveness | Series looks like generic default anime (style_match_score < 0.70) |
| C2: Character Recognition | Main cast cannot be distinguished in cropped form (min_distinctiveness: 0.70 between top 5 cast) |
| C3: Camera Variety | Shot pattern is repetitive (repeated_shot_pattern_limit exceeded) |
| C4: Page Readability | Eye flow is confusing or dialogue bubble density is poor |

### Gate Group D — Canon / Continuity Gates

| Gate | Fails if |
|------|----------|
| D1: Canon Integrity | Contradiction of teacher doctrine, mechanism rules, or prior arc facts |
| D2: Identity Drift | Character face/outfit drift beyond threshold (min_character_match_score: 0.82) |
| D3: State Continuity | Emotional state, environment state, or visual motif drifts irrationally between panels |

### Gate Group E — Anti-Spam / Anti-Dupe Gates

| Gate | Fails if |
|------|----------|
| E1: Premise Similarity | Concept too close to active portfolio (max_concept_overlap: 0.38) |
| E2: Emotional Promise Density | Too many same-feeling volumes in same wave (max: 2 per wave) |
| E3: Visual Family Density | Same art family dominates release wave (max: 2 per wave) |
| E4: Thumbnail Confusion | Covers/key art too visually similar in feed view (max_confusion: 0.35) |
| E5: Chapter Structure Clone | Chapters across volumes share same beat skeleton too often (max: 0.40) |
| E6: Platform Spam Feel | Wave feels like "same product, different label" — scores: same protagonist fantasy loop, same visual identity family, same promise language, same title pattern, same cover composition, same emotional arc curve |

### Gate Group F — Localization Gates

| Gate | Fails if |
|------|----------|
| F1: Dialogue Naturalness | Text overlay dialogue feels translated rather than native |
| F2: Cultural Fit | References, humor, or intimacy level feel off-market for target locale |
| F3: Content Restrictions | Violates local platform or age-band packaging norms (China censorship, etc.) |

### Anti-duplication scoring model

```yaml
# config/manga/manga_dupe_eval.yaml

dupe_axes:
  premise_overlap: 0.20
  protagonist_overlap: 0.12
  emotional_promise_overlap: 0.12
  world_structure_overlap: 0.08
  chapter_beat_overlap: 0.10
  dialogue_signature_overlap: 0.05
  visual_family_overlap: 0.15
  cover_thumb_overlap: 0.08
  title_pattern_overlap: 0.05
  launch_wave_overlap: 0.05

thresholds:
  warn_at: 0.55
  block_at: 0.68

wave_density_caps:
  max_same_emotional_promise_per_wave: 2
  max_same_visual_family_per_wave: 2
  max_same_power_fantasy_loop_per_wave: 2
  max_same_romance_triangle_pattern_per_wave: 2
```

---

## 8. Format definitions

These add to `v4_freeze_modular_formats.yaml` alongside existing prose formats. They use the same canonical building blocks from [ATOM_NATIVE_MODULAR_FORMATS.md](../docs/ATOM_NATIVE_MODULAR_FORMATS.md).

### 8.1 manga_visual_card (visual_card mode)

```yaml
manga_visual_card:
  display_name: "Illustrated Practice Card"
  mode: visual_card
  structure: "B1_HOOK splash → B5_EXERCISE illustrated spread → B6_CLOSE closing panel"
  pages: 3-5
  panels_per_page: 1-2
  story_required: false
  reflection_required: false
  word_target: 50-150 (text overlays only)
  best_for: "Social sharing, mobile, Gen Alpha"
  maps_to_existing: "5-Minute Practice (atom-native)"
```

### 8.2 manga_pocket_guide (visual_card mode)

```yaml
manga_pocket_guide:
  display_name: "Illustrated Pocket Guide"
  mode: visual_card
  structure: "10-20 entries; each = B1_HOOK panel + B5_EXERCISE illustrated step + B6_CLOSE panel"
  pages: 30-60
  panels_per_page: 2-4
  story_required: false
  reflection_required: optional
  word_target: 500-1500
  best_for: "EPUB, app cards, classroom"
  maps_to_existing: "Pocket Guide"
```

### 8.3 manga_symptom_atlas (visual_card mode)

```yaml
manga_symptom_atlas:
  display_name: "Illustrated Symptom Atlas"
  mode: visual_card
  structure: "20-60 cards; each = visual symptom panel + mechanism explanation + 60-second practice illustrated"
  pages: 60-180
  panels_per_page: 2-3
  story_required: false
  reflection_required: true (mechanism explanation)
  word_target: 1000-3000
  best_for: "Crisis utility, repeat use, highest therapeutic value"
  maps_to_existing: "Symptom-to-Action Atlas"
```

### 8.4 manga_full_volume (full_volume mode)

```yaml
manga_full_volume:
  display_name: "Full Manga Volume"
  mode: full_volume
  structure: "Arc-driven chapters; each chapter = B1 splash → B2 environment → B3 narrative sequence → B4 teacher panel → B5 practice spread → B6 closing"
  pages: 120-200
  panels_per_page: 3-6
  story_required: true (arc required)
  reflection_required: true
  word_target: 3000-8000 (text overlays)
  best_for: "Premium print/digital, European collector market, Webtoon serialization"
  maps_to_existing: "Pearl Prime full book pipeline"
```

### 8.5 manga_webtoon_episode (webtoon_episode mode)

```yaml
manga_webtoon_episode:
  display_name: "Vertical Scroll Webtoon Episode"
  mode: webtoon_episode
  structure: "50-80 vertical panels, optimized for thumb-scroll, episodic drops"
  pages: 1 (continuous vertical scroll)
  panels_per_page: 50-80 (vertical stack)
  story_required: true (episodic engine)
  reflection_required: optional
  word_target: 500-2000
  best_for: "Webtoon/Tapas platforms, Korea/US/SE Asia"
  maps_to_existing: "Pearl News episodic format"
```

---

## 9. Agent architecture (21 agents, 5 memory systems)

Source: `docs/manga_tech_notes.txt` §§2–7. These map to the existing Pearl_Dev / Pearl_Writer / Pearl_Editor agent model.

### 9.1 Layers

| Layer | Agents | Maps to existing |
|-------|--------|-----------------|
| L0: Market Intelligence | trend_intel, audience_segmentation | New (market-facing) |
| L1: Portfolio / Greenlight | concept_generator, portfolio_greenlight | Extends catalog planning |
| L2: Story System | story_architect, chapter_outline, panel_script, dialogue_voice, pacing_retention | Extends Pearl_Writer |
| L3: Visual System | style_director, character_design, environment_prop, panel_composition, page_layout | New (extends video pipeline) |
| L4: Assembly / Rendering | image_render, visual_consistency | New (ComfyUI backend) |
| L5: QA / Safety / Anti-Dupe | canon_guard, anti_duplication | Extends Pearl_Editor + existing gates |
| L6: Localization / Distribution | market_localization, growth_asset, performance_feedback | Extends translation pipeline + video pipeline |

### 9.2 Memory systems

| Memory | Stores | Maps to existing |
|--------|--------|-----------------|
| M1: Canon Memory | Timeline, chapter facts, relationship changes, unresolved mysteries | Extends arc system |
| M2: Character Identity Memory | Face tokens, hairstyle tokens, outfit IDs, expression ranges, silhouette | New (LoRA management) |
| M3: Style Lock Memory | Approved style embeddings, banned drift patterns, palette IDs, layout signatures | New (extends video brand_style_tokens) |
| M4: Series Differentiation Index | Premise vectors, protagonist vectors, emotional promise vectors, visual family embeddings | Extends CTSS (platform similarity) |
| M5: Performance Analytics Memory | CTR by cover, read-through by chapter, drop-off panel clusters, most-shared beats | New (feedback loop) |

### 9.3 Minimum viable agent set (Phase 1)

9 agents + 3 memory systems:

```
trend_intel_agent
concept_generator_agent
story_architect_agent
panel_script_agent
style_director_agent
character_design_agent
image_render_agent
canon_guard_agent
anti_duplication_agent

+ canon_memory
+ character_identity_memory
+ style_lock_memory
```

### 9.4 Elite agent set (Phase 3+)

Add 12 agents + 2 memory systems:

```
audience_segmentation_agent
portfolio_greenlight_agent
chapter_outline_agent
dialogue_voice_agent
pacing_retention_agent
environment_prop_agent
panel_composition_agent
page_layout_agent
visual_consistency_agent
market_localization_agent
growth_asset_agent
performance_feedback_agent

+ series_differentiation_index
+ performance_analytics_memory
```

---

## 10. Regional deployment

### 10.1 Trust map

| Region | Primary Research Source | Key Insight | Primary Format | Primary Style |
|--------|----------------------|-------------|----------------|--------------|
| USA / NA | Gemini | 23% CAGR, manga in education | Pocket Guide, Practice Card | dark_psychological, cozy_iyashikei |
| Europe (France) | Gemini | Mature market, collector mentality | Full Volume (premium print) | dark_psychological, hyper_clean_cinematic |
| China | DeepSeek | Bilibili 315M MAU, Xianxia genre | Webtoon Episode (vertical scroll) | webtoon_vertical_romance (Manhua variant) |
| South Korea | Both | OSMU model, Wait-Until-Free monetization | Webtoon Episode | webtoon_vertical_romance |
| Japan | Rakuten (pending) | 72.7% digital, premium print coexist | Full Volume + Practice Card | cozy_iyashikei, dark_psychological |
| SE Asia | Both | Mobile-first, 30% local content quota | Practice Card, Webtoon Episode | cozy_iyashikei, meme_chaotic_humor |
| Latin America | Both | AVOD model, 94% CTV smart TVs | Practice Card + video shorts | hyper_clean_cinematic, meme_chaotic_humor |

### 10.2 Translation overlay strategy

Same visual panels, locale-specific text overlays:
- Translation pipeline (11 locales active) produces localized atom text
- Text overlay engine applies locale-specific speech bubbles, captions, SFX
- Reading direction config: LTR (default), RTL (Arabic), top-to-bottom (Japanese vertical)
- Font config per locale (CJK fonts, Latin fonts, Arabic fonts)

### 10.3 China-specific adaptations

- Bilibili OGV format support for video pipeline manga-derived shorts
- Existing doctrine gates map to Chinese content compliance (forbidden language enforcement)
- Teacher-pure rule prevents cross-contamination that triggers censorship flags
- Therapeutic content avoids romance tropes that require "bromance" coding

---

## 11. Output package per volume

```
manga_output/
  {volume_id}/
    market_brief.yaml
    audience_brief.yaml
    style_bible.yaml               # locked style archetype + customizations
    character_packets/              # per-teacher character design packets
      {teacher_id}_packet.yaml
    panel_scripts/                  # per-chapter panel scripts
      ch{N}_panels.yaml
    visual_prompts/                 # compiled visual prompts (deterministic)
      ch{N}_prompts.csv
    rendered_panels/                # output images
      ch{N}_p{NN}.png
    assembled_pages/                # final pages with text overlays
      ch{N}_page{NN}.png
    localization/                   # per-locale text overlay variants
      {locale}/
        ch{N}_page{NN}.png
    deliverables/
      {volume_id}.epub              # illustrated EPUB
      {volume_id}_scroll.html       # vertical scroll version
      {volume_id}_print.pdf         # print-ready PDF
    provenance/
      manifest.yaml                 # full audit trail
    dupe_eval_report.yaml           # anti-duplication scoring
    gate_results.yaml               # all gate pass/fail results
```

---

## 12. Implementation phases

Following repo rules: smallest possible change, extend existing patterns, no new systems unless explicitly required.

### Phase 1: Config + Schema (Days 1–14)

- Add manga format definitions to `v4_freeze_modular_formats.yaml`
- Define `visual_style_archetype` enum in `teacher_registry.yaml`
- Add `panel_layout` field to atom metadata schema
- Create `config/manga/style_archetypes.yaml`
- Create `config/manga/panel_layouts.yaml`
- Create `config/manga/manga_gates.yaml`
- Gate: existing CI must still pass (snapshot before/after)

### Phase 2: Visual Prompt Compiler (Days 15–35)

- Build `pearl_prime/manga/visual_prompt_compiler.py`
- Read atom metadata + style archetype → deterministic visual prompts
- Reference `config/video/emotion_to_camera_overrides.yaml` for camera mappings
- Add manga-specific CI checks: visual prompt deduplication, panel composition validation
- Gate: structural entropy must pass on visual prompt sequences

### Phase 3: Panel Assembly + Rendering (Days 36–60)

- Build `pearl_prime/manga/panel_renderer.py` (ComfyUI integration)
- Build `pearl_prime/manga/page_assembler.py` (layout + text overlay)
- Integrate with existing asset resolver from video pipeline
- Output formats: EPUB (illustrated), vertical scroll HTML, print-ready PDF
- Gate: all existing quality gates + manga gates (§7)

### Phase 4: Distribution + Feedback (Days 61–90)

- Extend video pipeline for manga-derived short-form content (panel reveals, motion comics)
- Add Webtoon vertical format exporter
- Wire translation pipeline for localized text overlays (11 existing locales)
- Build performance feedback loop (analytics → style_director, pacing_retention)
- Gate: full `go_live.py` must pass, including manga format smoke tests

---

## 13. Critical implementation truths

Source: `docs/manga_tech_notes.txt` §13.

The real bottleneck is **not** raw image generation. It is:

1. **Character continuity** — solved by teacher-pure rule + character LoRA + SDF geometric prior + IPAdapter/InstantID + identity memory (LoRA alone ~85% consistency; SDF+LoRA 95%+)
2. **Style lock** — solved by style archetype lock + style LoRA + style lock memory
3. **Page readability** — solved by panel layout templates + page readability gate (C4)
4. **Portfolio differentiation** — solved by anti-duplication gates (E1–E6) + differentiation index
5. **Earned emotional progression** — solved by arc-first rule + existing arc gates

These are where most AI manga systems fail. Phoenix Omega has existing infrastructure for all five.

---

## 14. Pending

- **Rakuten deep research (Japan):** When `deep_research_manga_rakuten.txt` is delivered, this spec will be updated with Japan-specific strategy: Shonen Jump+ integration, premium print collector workflow, Iyashikei genre emphasis, and Japanese vertical text overlay config.
- **ComfyUI workflow validation:** The workflow template (`config/manga/comfyui_workflow.json`) requires testing with actual SD checkpoints and LoRAs before Phase 3.
- **Character LoRA training:** Per-teacher character LoRAs must be trained from character design packets before panel rendering can begin.
- **SDF model training:** Per-teacher neural SDFs must be trained from character reference sheets (~2–4 hours per character on single GPU). SDF training depends on character design packets being finalized first. Train LoRA and SDF in parallel once reference sheets are approved.
- **ComfyUI custom node validation:** SDF preprocessor node, MangaToner, IPAdapter-Plus, FaceDetailer, and 4x-UltimateSD must be installed and tested together before Phase 3 batch rendering.
- **Human-in-the-loop QA:** Visual QA protocol (existing HITL pattern from video pipeline) must be adapted for manga panel review cadence.

---

## 15. Production stack (what you actually run)

This section defines the concrete technology stack. The system is **not** a single image generator — it is a deterministic visual compiler for atoms, with GPU rendering as one layer.

### 15.1 Backend services

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Pipeline orchestrator | Python 3.11 + existing `run_pipeline.py` | Extends Pearl Prime; no new entrypoint |
| Prompt compiler API | FastAPI (internal) | Serves `visual_prompt_compiler.py` as a service for batch requests |
| Render job queue | Celery + Redis | Async GPU rendering — prevents pipeline freeze at 100+ panels |
| Metadata store | PostgreSQL | Panel tracking, render status, provenance, gate results |
| Asset storage | MinIO / S3 | Raw panels, final panels, pages, deliverables, LoRA models |

**Why a job queue matters:** Without async rendering, the pipeline blocks on every panel. At 120–200 panels per volume, this is fatal. Celery workers process render jobs from two priority queues:
- `render_high` — single-panel re-renders, QA fixes
- `render_batch` — bulk chapter rendering (8–16 panels per GPU batch)

### 15.2 Module-to-service mapping

| Module (from §3.2) | Implementation | Service type |
|---------------------|---------------|-------------|
| `visual_prompt_compiler.py` | Pure Python + Jinja2 templates for prompt assembly | Stateless function; runs inline or via FastAPI |
| `panel_renderer.py` | ComfyUI API wrapper + Celery worker | Async GPU service; reads from Redis queue |
| `page_assembler.py` | Pillow (PIL) + OpenCV + HTML template engine | Stateless function; post-render assembly |
| `manga_format_freeze.py` | Pydantic schema validation + YAML loader | CI check; runs at compile time |

### 15.3 Config loading

All YAML configs load via `pydantic` schemas with versioned config loader (same pattern as existing `FreezeSettings` dataclass in `pearl_prime/modular_format_freeze.py`):
- Style archetypes → `StyleArchetypeConfig`
- Panel layouts → `PanelLayoutConfig`
- Camera language → `CameraLanguageConfig`
- Manga gates → `MangaGateConfig`

### 15.4 GPU infrastructure

| Tier | Hardware | Throughput | Use case |
|------|----------|-----------|----------|
| Dev / proof-of-concept | 1x RTX 4090 (24GB VRAM) | ~50 panels/hour | First pipeline test, LoRA training |
| Production (single volume) | 2x RTX 4090 | ~100 panels/hour | Weekly volume production |
| Scale (catalog) | 4x GPU nodes (4090 or A100) | ~400 panels/hour | Batch catalog generation, multi-locale |

**Batch sizing:** 8–16 panels per GPU batch on 24GB VRAM (SDXL). Reduce to 4–8 for multi-LoRA stacks with SDF ControlNet active.

### 15.5 Assembly tools

| Task | Tool | Notes |
|------|------|-------|
| Panel image composition | Pillow (PIL) | Panel → page grid placement |
| Text overlay (speech bubbles, captions, SFX) | Pillow + custom bubble renderer | Locale-aware font selection |
| Vertical scroll assembly | HTML template engine (Jinja2) | For webtoon_episode format |
| EPUB generation | `ebooklib` (Python) | Illustrated EPUB with embedded images |
| Print PDF | WeasyPrint or ReportLab | Print-ready with bleed margins |
| Screentone / manga polish | OpenCV (optional post-process) | Alternative to MangaToner node |

### 15.6 Storage layout

```
s3://manga-assets/
  models/
    checkpoints/          # SD checkpoints per style archetype
    loras/
      characters/         # per-teacher character LoRAs
      styles/             # per-archetype style LoRAs
    sdf/                  # trained SDF models per teacher
  renders/
    {volume_id}/
      raw_panels/         # direct ComfyUI output
      qa_approved/        # post-QA panels
      pages/              # assembled pages
      deliverables/       # EPUB, HTML, PDF
```

### 15.7 Automated QA layer

These run after every render batch, before page assembly:

| Check | Method | Maps to gate |
|-------|--------|-------------|
| Identity drift detection | Compare rendered panel SDF against reference SDF | Gate D2 |
| Duplicate panel detection | Perceptual hash (pHash) similarity across volume | Gate E5 |
| Panel similarity scoring | CLIP embedding cosine similarity | Gate E3, E6 |
| Anatomy validation | ControlNet pose estimation vs intended pose | Gate C2 |
| Style consistency | CLIP embedding distance from style bible reference | Gate C1 |

---

## 16. Model recommendations (checkpoints + LoRAs per archetype)

### 16.1 Base checkpoints

Map each style archetype to a specific SD checkpoint. Use 2–3 checkpoints maximum to reduce complexity.

| Style Archetype | Recommended Base | Notes |
|----------------|-----------------|-------|
| hyper_clean_cinematic | AnimagineXL or AnythingV5 | High-quality anime, good at cinematic lighting |
| webtoon_vertical_romance | ToonYou or MeinaMix | Soft shading, fashion-forward, close-up strength |
| meme_chaotic_humor | Manga sketch model (SD 1.5) | Rough linework, exaggerated expressions |
| dark_psychological | Manga B&W model (SD 1.5 or SDXL) | High contrast, halftone, sparse composition |
| cozy_iyashikei | Pastel anime model or CounterfeitV3 | Soft palette, rounded shapes |
| power_progression | AnimagineXL or action manga checkpoint | Dynamic posing, UI overlay compatibility |
| social_media_simulacra | Mixed media / SDXL base | Flat UI elements, text-compatible |
| interactive_branching | AnimagineXL | Clean digital, overlay-friendly |

**Rule: lock checkpoint per archetype.** Do not mix checkpoints within a single volume. Different archetypes can use different checkpoints, but every panel in a volume uses the same one.

### 16.2 LoRA training pipeline

Per-teacher character LoRAs are trained from character design packets:

```
Input:  config/manga/characters/{teacher_id}_packet.yaml
        + 15-30 reference images (front, side, back, 3/4, expressions, poses)

Training:
  Tool: kohya_ss or sd-scripts
  Steps: 1500-3000 (depending on reference count)
  Learning rate: 1e-4 (SDXL) or 5e-5 (SD 1.5)
  Network rank: 32-64
  Resolution: 1024x1024 (SDXL) or 768x768 (SD 1.5)
  Regularization: 200-500 class images (generic anime character)

Output: loras/characters/{teacher_id}_lora.safetensors

Validation:
  Generate 20 test images across different poses/cameras
  Compare against reference sheet
  Must pass: face_match > 0.85, outfit_match > 0.80, silhouette_match > 0.82
```

**Training order:** Train character LoRAs in parallel with SDF models (both depend on finalized character design packets). Style LoRAs can use off-the-shelf models initially; train custom style LoRAs only if off-the-shelf drift from the style bible.

### 16.3 Model selection constraints

- **Max 3 base checkpoints** in production (reduces VRAM management complexity)
- **Max 3 LoRAs stacked simultaneously** (character + style + optional props; more causes bleed)
- **Total LoRA weight cap:** sum of all LoRA model weights should not exceed 2.0
- **Checkpoint switching:** only at volume boundaries, never mid-chapter

---

## 17. Dev instructions (copy-paste ready)

These are structured as sequential dev tasks. Each phase is a complete deliverable with a verification step.

### Quick-start: Colab test (no hardware required)

Before Phase 1, validate the pipeline logic on a free Google Colab T4 GPU:

```
scripts/manga/colab_manga_test.ipynb
```

This notebook runs: visual prompt compiler → panel rendering → page assembly → PDF export using `diffusers` (not ComfyUI — Colab test only). Covers spec §§4.1, 5.1, 6.3, 6.4, 6.5. Takes ~5 minutes for 10 panels. No API keys, no cost, no local GPU.

### DEV TASK — PHASE 1: Foundation (Days 1–14)

**Goal:** First manga pipeline working end-to-end (5 atoms → 10 panels → assembled page → PDF).

**Step 1: Config schemas**
```bash
# Create config directory
mkdir -p config/manga/characters config/manga/sdf

# Create pydantic schemas
# File: pearl_prime/manga/schemas.py
# Define: StyleArchetypeConfig, PanelLayoutConfig, CameraLanguageConfig
# Load from: config/manga/*.yaml
# Pattern: match FreezeSettings in pearl_prime/modular_format_freeze.py
```

**Step 2: Visual prompt compiler**
```python
# File: pearl_prime/manga/visual_prompt_compiler.py
#
# Input:
#   - compiled atoms (from existing pipeline stage 4)
#   - style_archetype_id (from format config)
#   - teacher_id (from pipeline flags)
#
# Output: CSV with deterministic panel prompts
#   Columns: panel_id, atom_id, atom_type, character_id, style_id,
#            scene, emotion, camera, seed, sdf_pose_mod, controlnet_strength
#
# Rules:
#   - NO random prompt generation
#   - NO freestyle text — all prompt blocks from config
#   - Every panel maps to exactly one atom (or atom fragment)
#   - Prompt = CHARACTER_BLOCK + STYLE_BLOCK + CAMERA_BLOCK + SCENE_BLOCK + EMOTION_BLOCK
#   - Seed = base_seed + scene_id + panel_id (deterministic)
```

**Step 3: Install ComfyUI stack**
```bash
# Install ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI && pip install -r requirements.txt

# Install required custom nodes via ComfyUI-Manager:
#   - ControlNet
#   - IPAdapter-Plus
#   - InstantID
#   - FaceDetailer
#   - Ultimate SD Upscaler
#   - MangaToner (or equivalent line-art node)

# Load initial checkpoints (2 minimum):
#   - 1x anime/color (AnimagineXL or AnythingV5)
#   - 1x manga/B&W

# Test: generate single image via ComfyUI API
# Verify: API responds, image saves to storage
```

**Step 4: Panel renderer (basic)**
```python
# File: pearl_prime/manga/panel_renderer.py
#
# Read CSV from visual_prompt_compiler
# For each row:
#   - Build ComfyUI API request
#   - Apply: checkpoint, style LoRA, character LoRA
#   - Set seed from CSV
#   - Save output image to storage
#
# Phase 1: synchronous (no Celery yet)
# Phase 2 upgrade: async via Celery worker
```

**Step 5: Page assembler (basic)**
```python
# File: pearl_prime/manga/page_assembler.py
#
# Load panel images
# Apply layout template from config/manga/panel_layouts.yaml
# Add text overlays from atom text (speech bubbles, captions)
# Output: page PNG files
# Output: single PDF (using Pillow → PDF or WeasyPrint)
```

**Step 6: First end-to-end test**
```bash
# Run:
PYTHONPATH=. python scripts/run_pipeline.py \
  --output-format manga_visual_card \
  --teacher ahjan \
  --topic shame

# Expected output:
#   manga_output/{volume_id}/
#     prompts.csv           (5 rows)
#     panels/               (5-10 images)
#     pages/                (3-5 pages)
#     deliverables/test.pdf (assembled)

# Verify: snapshot before/after, existing CI still passes
```

### DEV TASK — PHASE 2: Consistency (Days 15–35)

**Goal:** Character consistency across 50+ panels. Identity drift < 15%.

**Step 1: LoRA training pipeline**
- Train 1 character LoRA for Ahjan (primary test teacher)
- Use kohya_ss with settings from §16.2
- Validate: 20 test images, face_match > 0.85

**Step 2: Seed control system**
- Implement: `scene_seed = base_seed + scene_id`, `panel_seed = scene_seed + panel_id`
- Same scene + same camera → same seed
- Verify: re-running same CSV produces identical images

**Step 3: Style lock enforcement**
- Load style archetype config at compile time
- Reject any panel prompt that references a different archetype than the volume's locked style
- Add CI check: `check_manga_style_lock.py`

**Step 4: Identity drift checker**
- Compare rendered panels against character reference sheet
- Use CLIP embedding cosine similarity
- Threshold: 0.82 minimum (matches Gate D2)
- Flag panels below threshold for re-render

**Step 5: Async rendering**
- Add Redis + Celery
- Move panel_renderer to Celery worker
- Two queues: `render_high`, `render_batch`
- Verify: 50-panel chapter renders without pipeline freeze

### DEV TASK — PHASE 3: SDF + Scale (Days 36–60)

**Goal:** 95%+ consistency. Full volume rendering (120+ panels).

**Step 1: SDF training**
- Train neural SDF for Ahjan from character reference sheet
- Output: `config/manga/sdf/training/ahjan_sdf_model.pt`
- ~2–4 hours on single GPU

**Step 2: SDF projector**
```python
# File: config/manga/sdf/inference/sdf_projector.py
#
# Input: trained SDF model + camera angle from panel prompt
# Output: 2D depth map + contour map
# Feed into: ControlNet depth conditioning (strength 0.5-0.7)
```

**Step 3: Full ComfyUI workflow**
- Wire complete stack: Checkpoint → Style LoRA → Character LoRA → SDF ControlNet → IPAdapter → KSampler → MangaToner → FaceDetailer → Upscale → Save
- Save as: `config/manga/comfyui_workflow.json`
- Test: 50+ panels, measure consistency score

**Step 4: Page assembly (production)**
- Add Pillow-based bubble renderer (locale-aware)
- Add EPUB generation via `ebooklib`
- Add vertical scroll HTML template (for webtoon format)
- Add print PDF with bleed margins

**Step 5: Full volume test**
```bash
PYTHONPATH=. python scripts/run_pipeline.py \
  --output-format manga_full_volume \
  --teacher ahjan \
  --arc arc_shame_spiral_01 \
  --topic shame

# Expected: 120-200 panels, assembled into EPUB + HTML + PDF
# Verify: all manga gates pass, identity drift < 5%
```

### DEV TASK — PHASE 4: Distribution + Gates (Days 61–90)

**Goal:** Multi-locale, anti-spam, platform distribution.

- Wire translation pipeline for text overlay localization (11 locales)
- Build manga-specific CI gate scripts (22 gates from §7)
- Extend video pipeline for manga-derived panel reveals and motion comics
- Add Webtoon vertical format exporter
- Build performance feedback loop
- Run full `go_live.py` with manga smoke tests
- Verify: full gate suite passes, multi-locale output renders correctly

---

## 18. What will break you if ignored

These are the concrete failure modes that kill AI manga pipelines at scale. Each maps to a mitigation already in this spec.

| Failure Mode | What Happens | Mitigation in This Spec |
|-------------|-------------|------------------------|
| No job queue | Pipeline freezes at 100+ panels; dev thinks system is broken | §15.1: Celery + Redis async rendering |
| No seed control | Same scene renders differently each run; visual incoherence | §6.4: deterministic seed = base + scene_id + panel_id |
| No identity validation | Characters slowly drift; by panel 50, face is unrecognizable | §6.7: SDF + LoRA + IPAdapter; §7 Gate D2 |
| Too many styles per wave | Catalog looks like spam; platform algorithms deprioritize | §7 Gates E3, E6: max 2 same visual family per wave |
| No batch pipeline | Dev renders panels one-by-one; 200-panel volume takes days | §6.5: CSV batch → ComfyUI batch node |
| Freestyle prompting | Prompts drift from atoms; output loses therapeutic coherence | §2 Invariant: all prompts compiled from atom metadata, never freestyle |
| Checkpoint mixing mid-volume | Visual style breaks between chapters | §5.2: style locked per volume; §16.3: switching only at volume boundaries |
| LoRA weight imbalance | Character identity dissolves into style; faces go generic | §6.2: character LoRA 0.8–1.0 always > style LoRA 0.4–0.6 |

---

*This spec follows the pattern established by [MUSICIAN_MODE_SYSTEM_SPEC.md](./MUSICIAN_MODE_SYSTEM_SPEC.md). Manga Mode is a mode, not a system. It rides the existing pipeline.*
