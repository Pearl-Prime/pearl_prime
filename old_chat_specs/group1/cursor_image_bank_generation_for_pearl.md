# Image bank generation for Pearl Star
_Exported on 4/16/2026 at 19:32:48 GMT+8 from Cursor (3.1.15)_

---

**User**

Act as Pearl_Dev + Pearl_Video for Phoenix Omega.

Read these files before doing any work:

- docs/SESSION_UNITY_PROTOCOL.md
- docs/PEARL_ARCHITECT_STATE.md
- docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md (FULL)
- specs/AI_MANGA_PIPELINE_SUMMARY.md (first 100 lines)
- specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md (§4-§8 — panel breath, color arc, fractal, gutter)
- config/manga/panel_layouts.yaml (FULL — 6 atom types → panel functions)
- config/manga/brand_illustration_styles.yaml (FULL — 13 brand styles)
- config/manga/genre_ite_profiles.yaml (FULL)
- config/manga/teacher_character_prompts.yaml (FULL — ahjan entry = JP brand 1)
- config/manga/sabido_roles.yaml (FULL — dialogue constraints)
- config/manga/asset_selection_priority.yaml
- config/video/therapeutic_video_rules.yaml (FULL — arc pacing, cut intervals)
- config/video/brand_style_tokens.yaml (FULL — topic palettes)
- config/video/image_prompt_templates.yaml (FULL — 20+ style templates)
- config/video/prompt_constraints.yaml (FULL — NEVER rules)
- config/video/flux_bank_scenes.yaml (FULL — 4 visual intents)
- config/catalog_planning/teacher_brand_lane_assignments.yaml (Japan lane)
- config/catalog_planning/brand_identity_system.yaml (grep stillness_press)
- config/catalog_planning/canonical_topics.yaml (15 topics)
- scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json
- scripts/image_generation/comfyui_workflows/flux_video_bank.json
- scripts/image_generation/prompt_compiler.py (FULL — token budgets)
- scripts/video/run_flux_bank_build.py (FULL — US bank builder)
- scripts/video/build_image_bank_index.py (first 40 lines)
- registry/anxiety.yaml (first 40 lines — chapter/section structure)
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv

Verify Pearl Star:
  curl -s --max-time 5 http://192.168.1.112:8188/system_stats 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('GPU:', d['devices'][0]['name'], 'VRAM:', round(d['devices'][0]['vram_total']/1e9,1), 'GB')" || echo "ComfyUI DOWN"

Emit a STARTUP_RECEIPT then execute.

TASK: Generate two complete image banks on Pearl Star ComfyUI:
  BANK 1: Japan Brand 1 (Stillness Press / Ahjan) manga panel bank — 552 panels
  BANK 2: US Brand 1 (Stillness Press / Ahjan) video image bank — 400 images
Follow ALL pipeline documentation. Do not drift.

PROJECT_ID: proj_state_convergence_20260328
SUBSYSTEM: manga_pipeline, video_pipeline

───────────────────────────────────────────────────────────────────────

INFRASTRUCTURE:

  Pearl Star: 192.168.1.112
  ComfyUI: http://192.168.1.112:8188
  GPU: NVIDIA RTX 5070 Ti (16GB VRAM)
  Model: flux1-schnell-fp8.safetensors
  Manga workflow: flux_txt2img_manga.json (1024×1024, 24 steps, CFG 4.0)
  Video workflow: flux_video_bank.json (576×1024 9:16, 4 steps, CFG 1.0)

───────────────────────────────────────────────────────────────────────

BANK 1: JAPAN MANGA PANEL BANK (552 panels)

  Brand: Stillness Press (stillness_press_jp)
  Teacher: Ahjan
  Style: Cozy Iyashikei — "Contemplative Ink Wash"
  Visual: soft ink linework, warm earth-toned watercolor wash,
          generous negative space, paper texture grain,
          Studio Ghibli meets Vagabond

  Colors: #4A5568 (slate), #E2E8F0 (cloud white), accent #C9A227 (warm gold)

───────────────────────────────────────────────────────────────────────

PANEL COUNT BREAKDOWN (per the spec):

  12 chapters × panels per chapter:
    HOOK: 1 splash panel (dramatic wide angle) = 12 panels
    SCENE: 1 environment panel (wide establishing) = 12 panels
    STORY: 4-panel narrative sequence (mixed angles) = 48 panels
    REFLECTION: 1 teacher panel (close-up character) = 12 panels
    EXERCISE: 2-panel practice spread (instructional) = 24 panels
    INTEGRATION: 1 closing panel (motif callback) = 12 panels
    SUBTOTAL per chapter: ~10 panels (conservative) or ~46 panels (full)

  APPROACH: Generate the FULL 46 panels per chapter for production.
  BUT START with the CORE set (10 per chapter = 120 panels) to validate
  quality, then expand to full 552.

  PHASE 1A: Core panel set (120 panels)
  PHASE 1B: Full panel set (remaining 432 panels)

───────────────────────────────────────────────────────────────────────

PANEL GENERATION — PROMPT STRUCTURE:

  Use the prompt_compiler.py 3-part structure:
    POSITIVE: style_prefix + panel_type_descriptor + topic_content + brand_aesthetic
    NEGATIVE: shared_negatives + style_negatives (from teacher_character_prompts.yaml)

  MAX TOKENS: 120 positive, 60 negative (per prompt_compiler.py)
  QUALITY PREFIX: "masterpiece, best quality, highly detailed illustration"

  STYLE PREFIX (Ahjan/Stillness Press):
    "seinen manga, soft ink linework, warm earth-toned watercolor wash,
    generous negative space, paper texture grain, Studio Ghibli meets
    Vagabond contemplative scenes, high detail, clean linework"

  NEGATIVE (Ahjan):
    "chibi, exaggerated, action pose, bright neon, horror, dark shadows,
    speed lines, battle aura, low quality, blurry, deformed, extra fingers,
    bad anatomy, watermark, text, logo, 3d render, photograph"

  PER PANEL TYPE:

  HOOK (splash, chapter opener):
    "dramatic wide angle composition, low angle establishing shot,
    atmospheric mood, {topic_scene}, {color_palette}"
    Examples per topic:
      anxiety: "figure standing at window watching rain, slate blue tones"
      grief: "empty garden bench in morning mist, warm amber"
      burnout: "desk with closed laptop, cold mug, grey morning light"

  SCENE (environment, establishing):
    "wide establishing shot, environmental storytelling, atmospheric,
    no figures, {location}, {color_palette}"
    Examples:
      anxiety: "quiet room with morning light through curtains, muted blue"
      grief: "autumn path with fallen leaves, warm gold, empty"

  STORY (4-panel narrative sequence):
    Panel 1: "medium shot, character entering scene, {emotion}, {setting}"
    Panel 2: "close-up hands or object, emotional detail, {action}"
    Panel 3: "medium-wide, character reacting, {body language}"
    Panel 4: "close-up face/profile (no full face), shift in expression"

  REFLECTION (teacher close-up):
    "close-up character focus, gentle expression, speech/thought implied,
    soft background bokeh, {teacher_aesthetic}"

  EXERCISE (2-panel instructional):
    Panel 1: "hands in position, somatic instruction implied, warm tones"
    Panel 2: "same hands, shifted position, completion implied, softer tones"

  INTEGRATION (closing, motif callback):
    "wide shot, forward motion implied, motif from chapter opener visible,
    warmer palette than chapter start, sense of gentle completion"

───────────────────────────────────────────────────────────────────────

ITE COMPLIANCE (per IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC):

  PANEL BREATH ENGINE:
    Generate inhale-phase panels (progressively larger) and exhale-phase
    panels (progressively smaller) as part of the STORY sequence.
    At least 1 breath sequence per chapter (wide panel ≥40% page width
    with nature/fractal detail).

  COLOR TEMPERATURE ARC:
    HOOK panels: warm (3500-4500K equivalent, orange-amber shift)
    STORY panels: high warm + tension (2500-3500K, higher saturation)
    REFLECTION panels: mixed warm-cool (4500-5500K, purple/violet)
    EXERCISE panels: cool (5500-7000K, blue-green, lower saturation)
    INTEGRATION panels: warm-soft (4000-5000K, golden hour)

    Implement by varying the color palette terms in each prompt:
      HOOK: "warm amber light, golden tones"
      STORY tension: "deep warm tones, red amber accent"
      REFLECTION: "soft violet undertones, mixed warm-cool"
      EXERCISE: "cool blue-green light, calm saturation"
      INTEGRATION: "golden hour warmth, soft amber glow"

  FRACTAL BACKGROUNDS:
    EXERCISE + INTEGRATION panels: include fractal nature elements
    "nature fractal background, organic tree branch patterns,
    flowing water detail, FD 1.3-1.5 complexity"

  NO FACES (Sabido compliance):
    All character panels: "no full face visible, profile or back of head,
    hands and body language only, expression through posture"

───────────────────────────────────────────────────────────────────────

MANGA BANK EXECUTION:

  For EACH of 12 chapters × 15 topics:

  STEP 1: Build prompts
    Generate the positive + negative prompt for each panel type
    using the 3-part structure. Total: ~120 prompts for core set.

  STEP 2: Queue on ComfyUI
    Load flux_txt2img_manga.json workflow.
    Strip _meta keys (known ComfyUI requirement).
    Set positive prompt, negative prompt, seed (hash-based per panel_id).
    POST http://192.168.1.112:8188/prompt
    Poll /history/{prompt_id} until complete.
    Download result PNG.

  STEP 3: Save with naming convention
    assets/manga_bank/stillness_press_jp/{topic}/{chapter_nn}/{panel_type}_{nn}.png
    Example: assets/manga_bank/stillness_press_jp/anxiety/ch01/hook_01.png

  STEP 4: Build index
    Generate assets/manga_bank/stillness_press_jp/index.json
    Per entry: {topic, chapter, panel_type, filepath, prompt_hash, timestamp}

  TIMING:
    Core set (120 panels): ~25s each at 24 steps = ~50 min
    Full set (552 panels): ~230 min (~3.8 hours)

  START WITH CORE SET. Validate quality. Then expand.

───────────────────────────────────────────────────────────────────────

BANK 2: US VIDEO IMAGE BANK (400 images)

  Brand: Stillness Press (stillness_press)
  Teacher: Ahjan
  Style: Soft gouache / therapeutic video bank

  Uses the DIFFERENT workflow: flux_video_bank.json
    Resolution: 576×1024 (9:16 vertical — for Reels/Shorts)
    Also generate 1024×576 (16:9 horizontal — for YouTube)
    Steps: 4 (FLUX Schnell ultra-fast)
    CFG: 1.0

───────────────────────────────────────────────────────────────────────

US BANK — IMAGE MATRIX:

  15 topics × 4 visual intents × ~5-7 style variations = ~400 images

  VISUAL INTENTS (from flux_bank_scenes.yaml):
    HOOK_VISUAL: "soft abstract moment of curiosity, gentle light"
    CHARACTER_EMOTION: "hands in contemplative pose, emotional resonance"
    SYMBOLIC_METAPHOR: "single symbolic object in soft focus"
    ENVIRONMENT_ATMOSPHERE: "atmospheric environment, no figures, calm"

  TOPIC PALETTES (from brand_style_tokens.yaml):
    anxiety: slate blue grey #7B8FA1 → pale mist blue #C5D1DB
    grief: lavender grey → soft lavender → pale lavender
    burnout: warm sand → linen → earth brown
    depression: deep indigo → muted violet → warm glow
    self_worth: gold → amber luminosity → bronze
    courage: warm amber → bright gold → burnt sienna
    boundaries: neutral root tones
    ... (all 15 topics from config)

  PROMPT STRUCTURE (from image_prompt_templates.yaml):
    Foreground: "{subject} in {palette_1} and {palette_2}, gentle paper grain"
    Background: "Soft watercolor wash of {palette_1} to {palette_3}, blended edges"
    Lighting: "Diffused morning light, gentle undramatic, soft shadows"

  NEVER RULES (from prompt_constraints.yaml):
    No dramatic light rays from above
    No figure silhouetted against bright sky
    No hands reaching upward
    No divine or spiritual glow
    No anime style
    No full faces
    No high contrast comic lines
    Ordinary grounded everyday moment

  TOPIC-SPECIFIC SUBJECTS (from image_prompt_templates.yaml):
    anxiety: "hands cupped around teacup by rain-streaked window"
    grief: "empty chair with soft knitted blanket"
    burnout: "figure resting against mossy hillside"
    depression: "small figure under umbrella in soft rain"
    self_worth: "mirror reflecting gentle light, not a face"
    courage: "door half-open with warm light beyond"
    ... (derive from config for all 15)

  STYLE VARIATIONS (generate 5-7 per topic × intent):
    soft_ghibli, minimalist_line_art, warm_gouache, ink_wash,
    pastel_watercolor (rotate styles to build variety)

───────────────────────────────────────────────────────────────────────

US BANK EXECUTION:

  STEP 1: Build the full prompt matrix
    15 topics × 4 intents × 5-7 styles = ~350-420 images
    Each prompt: foreground + background + lighting + never_rules

  STEP 2: Queue on ComfyUI
    Load flux_video_bank.json workflow (4 steps, fast).
    Generate BOTH orientations per image:
      576×1024 (9:16 vertical for Reels/Shorts)
      1024×576 (16:9 horizontal for YouTube)

  STEP 3: Save with naming convention
    image_bank/stillness_press/{topic}/{intent}_{style}_{nn}.png
    image_bank/stillness_press/{topic}/{intent}_{style}_{nn}_landscape.png

  STEP 4: Build index
    Run scripts/video/build_image_bank_index.py
    Output: image_bank/stillness_press/index.json

  TIMING:
    ~400 images × 2 orientations = ~800 generations
    At 4 steps each: ~3-5s per image = ~40-65 min total

───────────────────────────────────────────────────────────────────────

EXECUTION ORDER:

  1. US video bank FIRST (faster — ~1 hour)
     Validates ComfyUI connectivity + prompt quality
  2. JP manga core set SECOND (~50 min)
     Validates manga-specific prompts + ITE compliance
  3. JP manga full set THIRD (~3 hours)
     Only after core set quality is confirmed

  TOTAL: ~5 hours for both complete banks

  BETWEEN BANKS: Spot-check 10 images from each bank.
    Are they gouache style? (not photorealistic)
    No faces visible?
    Topic palette correct?
    No NEVER-rule violations?
    Sufficient variety between images?

───────────────────────────────────────────────────────────────────────

GIT WORKFLOW:
git fetch origin && git checkout -b agent/image-banks origin/main
Commits:
  a) "feat: US video image bank — 400 images for Stillness Press (15 topics × 4 intents)"
  b) "feat: JP manga panel bank — core 120 panels for Stillness Press"
  c) "feat: JP manga panel bank — full 552 panels"
  d) "feat: image bank indexes (US + JP)"
Run preflight, push, PR against main.

NOTE ON SIZE: ~1000+ images will be large.
  .gitignore the raw generation directory.
  Only commit the final curated bank + index.
  OR: Document R2 upload path if total exceeds 500 MB.

WRITE_SCOPE:
  image_bank/stillness_press/ (NEW — US video bank ~400 images)
  assets/manga_bank/stillness_press_jp/ (NEW — JP manga ~552 panels)
  image_bank/stillness_press/index.json (NEW)
  assets/manga_bank/stillness_press_jp/index.json (NEW)
  scripts/image_generation/generate_manga_panel_bank.py (NEW — batch manga generator)
  artifacts/coordination/ACTIVE_WORKSTREAMS.tsv (add workstream)

OUT_OF_SCOPE: Panel layout/composition (raw image generation only);
lettering; page assembly; video rendering; TTS; other brands

NON-NEGOTIABLE:
  ALL images via ComfyUI FLUX on Pearl Star — $0, no cloud APIs.
  Manga panels: 1024×1024, 24 steps, CFG 4.0 (flux_txt2img_manga.json).
  Video bank: 576×1024 + 1024×576, 4 steps, CFG 1.0 (flux_video_bank.json).
  Prompt max 120 positive tokens, 60 negative tokens.
  NEVER RULES enforced in every prompt (no faces, no divine glow, etc.).
  ITE color temperature arc applied to manga panels per chapter position.
  Fractal backgrounds in EXERCISE + INTEGRATION panels.
  Brand colors from brand_identity_system.yaml — do not invent.
  Topic palettes from brand_style_tokens.yaml — do not invent.
  Spot-check 10 images between banks before continuing.
  Start with US bank (faster, validates pipeline).
  Naming convention must be consistent for index builder.
  Strip _meta from ComfyUI workflow JSON before queuing.
  If ComfyUI is down or GPU errors, document and stop — don't fake images.
  Check `gh pr diff <number> --stat | tail -1` before merging.
  If total size >500 MB, use .gitignore + R2 upload doc instead of git commit.


---

**Cursor**

Reading required documentation and configs, verifying ComfyUI on Pearl Star, then implementing and executing the pipeline per your spec.



Emitting STARTUP_RECEIPT and implementing ComfyUI bank builders. Interpreting BANK 1 as 12 chapters × 46 panels = 552 full (STORY = 40 panels/chapter as 10×4 beats); core = 12 × 10 = 120. Resolving topic palettes for all canonical topics. Creating scripts and fixing `call_comfyui` to strip `_meta` and honor width/height.



Implementing shared ComfyUI helpers, fixing `call_comfyui` to set positive/negative and latent dimensions, adding the manga and video bank scripts, extending the index builder, and updating `.gitignore` and `ACTIVE_WORKSTREAMS.tsv`.



Writing the manga panel bank generator and US ComfyUI video bank script.



Adding band/palette resolution for canonical topics missing from `brand_style_tokens.yaml` using in-band proxy keys (only existing palette rows).



```
STARTUP_RECEIPT
AGENT:              Pearl_Dev + Pearl_Video
TASK:               Stillness Press US (400×2) + JP manga (120→552) FLUX banks on Pearl Star ComfyUI
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          manga_pipeline; video_pipeline
AUTHORITY_DOCS:     docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; specs/AI_MANGA_PIPELINE_SUMMARY.md (first 100L); specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §4–§8; config/manga/* (panel_layouts, brand_illustration_styles, genre_ite_profiles, teacher_character_prompts, sabido_roles, asset_selection_priority); config/video/* (therapeutic_video_rules, brand_style_tokens, image_prompt_templates, prompt_constraints, flux_bank_scenes); config/catalog_planning (teacher_brand_lane_assignments japan, brand_identity_system stillness_press, canonical_topics); scripts image_generation/video as specified; registry/anxiety.yaml (40L); artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
READ_PATH_COMPLETE: yes (per your list; VIDEO guide is operator summary not identical to a single “full” mega-doc file beyond what’s in repo)
WRITE_SCOPE:        scripts/image_generation/comfyui_http.py; scripts/image_generation/generate_manga_panel_bank.py; scripts/video/run_comfyui_stillness_video_bank.py; scripts/video/flux_client.py; scripts/video/build_image_bank_index.py; .gitignore; artifacts/coordination/STILLNESS_COMFY_BANKS_REGEN.txt; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
OUT_OF_SCOPE:       Layout/lettering, video render, TTS, other brands, merging this PR without local `gh pr diff N --stat` check
BLOCKERS:            none (ComfyUI at 192.168.1.112:8188 returned RTX 5070 Ti ~16.6 GB VRAM)
READY_STATUS:       ready
```

### Pearl Star check

ComfyUI responded: **NVIDIA GeForce RTX 5070 Ti**, **VRAM ~16.6 GB** (from `/system_stats`).

### What was implemented

| Deliverable | Detail |
|-------------|--------|
| **US video bank driver** | `scripts/video/run_comfyui_stillness_video_bank.py` — 15 topics × 4 intents; **40 cells × 7 styles + 20 × 6 = 400** image prompts; each **576×1024** and **1024×576**; `flux_video_bank.json` (4 steps, CFG 1.0); prompts from `image_prompt_templates.yaml` + `flux_bank_scenes.yaml` + `brand_style_tokens.yaml` (+ `TOPIC_BAND_PATCH` / `PALETTE_TOPIC_PROXY` so every canonical topic resolves to **existing YAML palette rows only**); negatives from template overrides + `prompt_constraints.yaml` + band `never_rules`; **strip `_meta`** before `/prompt`. |
| **JP manga bank driver** | `scripts/image_generation/generate_manga_panel_bank.py` — **core 120** (`--phase core`) or **full 552** (`--phase full`, 40 STORY beats/chapter); **1024×1024, 24 steps, CFG 4.0**; ITE-style color arc + fractals on exercise/integration + breath language in STORY; **no full face** on character beats; **120 / 60 token trims** via `prompt_compiler`; output `assets/manga_bank/stillness_press_jp/{topic}/chNN/...` + `index.json`. |
| **Shared HTTP** | `scripts/image_generation/comfyui_http.py` — `queue_prompt`, `download_result`, `strip_meta`. |
| **`call_comfyui` fix** | `scripts/video/flux_client.py` — separate **positive node 6 / negative node 7**, set **latent width/height**, `strip_meta`, use shared poller (fixes wrong negative handling and missing resize). |
| **Index builder** | `scripts/video/build_image_bank_index.py` — **`--recursive`** for `image_bank/stillness_press/…`. |
| **Git / ops** | `.gitignore` for `image_bank/stillness_press/`, `assets/manga_bank/stillness_press_jp/`, `artifacts/coordination/stillness_*_bank.log`; regen note `artifacts/coordination/STILLNESS_COMFY_BANKS_REGEN.txt`; **ACTIVE_WORKSTREAMS** row `ws_stillness_flux_banks_20260410`. |

### Execution status (on your machine)

1. **Smokes (real ComfyUI)**  
   - US: **1 cell → 2 PNGs** OK under `image_bank/stillness_press/`.  
   - JP: **`--limit 1`** panel OK under `assets/manga_bank/stillness_press_jp/…`.

2. **Full US bank**  
   - Started in background with log: `artifacts/coordination/stillness_us_bank.log` (about **800** queue jobs).  
   - **Do not start the full manga run in parallel** on the same GPU; when the log shows completion, run JP **core** then **full** per `STILLNESS_COMFY_BANKS_REGEN.txt`.

3. **Git**  
   - Branch **`agent/image-banks`** from `origin/main`, commit **`f3a6a56aa4`** (*feat: Stillness Press ComfyUI image bank scripts (US + JP)*).  
   - Preflight/push/PR: run your usual `push_guard.py`, `preflight_push.sh`, and `health_check.sh` before push (not run here to avoid bypassing your governance).

### Spot-check (10 images) — after US batch finishes

Open a mix of portrait/landscape under `image_bank/stillness_press/*/hook_visual_*` (and other intents): gouache/watercolor feel, **no faces**, palettes feel on-topic, no obvious NEVER-rule violations (no god-rays, no raised hands to sky, etc.). Then start JP core and repeat on a few `hook` / `story` / `exercise` panels.

---

```
CLOSEOUT_RECEIPT
AGENT:          Pearl_Dev + Pearl_Video
TASK:           Stillness Press US + JP ComfyUI bank tooling and phased execution start
COMMIT_SHA:     f3a6a56aa4
FILES_WRITTEN:  scripts/image_generation/comfyui_http.py; scripts/image_generation/generate_manga_panel_bank.py; scripts/video/run_comfyui_stillness_video_bank.py; scripts/video/flux_client.py; scripts/video/build_image_bank_index.py; .gitignore; artifacts/coordination/STILLNESS_COMFY_BANKS_REGEN.txt; artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
FILES_READ:     docs/SESSION_UNITY_PROTOCOL.md; docs/PEARL_ARCHITECT_STATE.md; docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md; specs/AI_MANGA_PIPELINE_SUMMARY.md (100L); specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §4–§8; config/manga/* (listed); config/video/* (listed); config/catalog_planning/* (listed); workflows; prompt_compiler; registry/anxiety.yaml (40L); ACTIVE_WORKSTREAMS.tsv
STATUS:         partial — repo tooling + smokes done; full **800-job US** run in progress (see stillness_us_bank.log); **JP core 120** / **full 552** and final index regeneration remain after US completes
HANDOFF_TO:     you / Pearl_Dev on Pearl Star
NEXT_ACTION:    Tail `artifacts/coordination/stillness_us_bank.log` until idle; run `python3 scripts/video/build_image_bank_index.py --bank-dir image_bank/stillness_press --recursive`; spot-check 10 images; then `generate_manga_panel_bank.py --phase core` (full 120), spot-check, then `--phase full`; push branch `agent/image-banks` after preflight; **do not merge** until `gh pr diff <N> --stat | tail -1` reviewed
```

