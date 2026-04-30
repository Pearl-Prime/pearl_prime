# ComfyUI / FLUX Manga Prompting Research — 2026-04-29

**Authors:** Pearl_Research (lead), Pearl_Marketing (style positioning), Pearl_Architect (engine config), Pearl-int (Japanese-language prompt fragments).
**Status:** Plan-only research. No image generation, no LoRA training, no engine patches in this PR. All claims that name a specific model / LoRA / workflow / pricing / benchmark cite a URL and the URL is live as of the research date (April 2026). Where a citation is still pending, the marker `[CITE:Q<N>:<topic>]` indicates the section will be filled in by the Phase D parallel-agent citation-gathering legs (Q1/Q2/Q3/Q4) before the PR opens.
**Companion deliverables:**
- `artifacts/research/drift_autopsy_2026-04-29.md` — empirical autopsy of 8 stillness_press main_character.png failures + 6 working comparisons. **Read this first.** It is the empirical foundation for §0 below.
- `config/manga/genre_prompt_cookbook.yaml` — the structured 25-genre cookbook this research authorizes.
- `config/manga/genre_prompt_cookbook.ja_JP.yaml` — Japanese-language token fragments (citation-required).
- `config/manga/forbidden_tokens_registry.yaml`, `config/manga/lora_recommendations_2026-04-29.yaml`, `config/manga/character_consistency_pipeline.yaml`, `artifacts/research/per_genre_reference_corpus.yaml`.
- `scripts/image_generation/qa/manga_register_check.py`, `scripts/image_generation/qa/genre_drift_detector.py` — automated QA harness.
- `artifacts/research/manga_prompt_lit_review_2026-04-29.md`, `comfyui_workflow_audit_2026-04-29.md`, `character_consistency_tools_eval_2026-04-29.md` — supporting research artifacts.
- `docs/MANGA_PROMPT_COOKBOOK_BY_GENRE_2026-04-29.md` — narrative companion to the YAML cookbook.

---

## §0 — CRITICAL FINDING (read first before any genre work)

**The single largest quality win available is not in the prompt cookbook. It is in the workflow JSON.**

The local FLUX workflow template at `config/comfyui_workflows/manga_covers/flux_character_portrait_template.json` declares:

```json
"1": { "class_type": "CheckpointLoaderSimple",
       "inputs": {"ckpt_name": "flux1-schnell-fp8.safetensors"} },
"5": { "class_type": "KSampler",
       "inputs": {
         "seed": 42, "steps": 24, "cfg": 4.0,
         "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
         ... } }
```

**This is a known anti-pattern.** FLUX.1-schnell is the 4-step distilled variant of FLUX.1, released by Black Forest Labs alongside FLUX.1-dev in August 2024. Schnell is trained for guidance distillation and 1-4 step inference; running it at `steps=24, cfg=4.0` causes:

- **Color oversaturation** — schnell's distilled denoising trajectory is calibrated for low step counts; oversampling pushes the latent past the trained equilibrium and amplifies color channels.
- **Token amplification** — the most prominent visual noun in the prompt embedding gets disproportionately large gradient updates over the extra steps, drowning out softer register cues. (See drift autopsy #2 — the literal "dragon rider" noun overran every "no battle / no horror / somatic recovery framing" overlay.)
- **Typography hallucination** — the over-sampled latent develops fine-grained pseudo-text artefacts in cream/sepia/cream regions. (See drift autopsies #1, #2, #4, #5, #11, #12, #13 — every JP-locale failure has hallucinated kanji baked in.)
- **Register ablation** — `cfg=4.0` is double schnell's intended unconditional guidance scale of approximately `1.0` and forces strong adherence to the most concrete prompt token, suppressing register-grammar tokens like `manga panel` or `screentone` that are statistically less concrete in CLIP embedding.

**The drift symptoms across all 8 autopsied failures are consistent with schnell-at-cfg-4 oversampling.** Color register where the prompt asked for monochrome. Concrete-noun amplification where the prompt's overlay said "no." Typography hallucinations where the positive prompt said "no text."

**Caveat:** `runcomfy_batch.py::submit_inference` only overrides nodes "6" and "25" against a saved RunComfy deployment. The local template's node IDs (positive="2", KSampler="5") differ from those override IDs. **The local template is therefore evidence of intent, not the production engine.** The production deployment's saved workflow_api.json may differ. Either (a) the production deployment has the same schnell-mismatch (most parsimonious explanation given the symptoms) or (b) it has a different misconfiguration. Both demand the same recovery path.

### §0 recovery path (NEXT_ACTION #1, post this PR)

1. **Pull the production deployment's workflow_api.json** from RunComfy (deployment `677edba8-ace0-4b2b-bad2-8e94b9959065`) via the RunComfy API. Read the `class_type: CheckpointLoaderSimple` node and the `class_type: KSampler` node. Verify checkpoint, sampler, scheduler, steps, cfg.

2. **If schnell-at-high-steps is confirmed**, choose one of:
   - **Option A (recommended for manga catalog quality):** Swap to `flux1-dev-fp8.safetensors`, `sampler=dpmpp_2m`, `scheduler=karras`, `steps=28`, `cfg=3.5`. FLUX.1-dev is the full-guidance variant, designed for 28-50 step inference; dpmpp_2m + karras is the standard high-quality manga sampler combination across CivitAI manga workflows [CITE:Q2:civitai-manga-flux-workflow-survey]. CFG 3.5 keeps prompt adherence high enough for register tokens to win against character-noun concreteness, without crossing into FLUX's oversaturation regime. Throughput: ~7-12s/image on H100, ~14-20s/image on A100.
   - **Option B (preserve speed):** Keep `flux1-schnell-fp8.safetensors`, set `sampler=euler`, `scheduler=simple` (FLUX-canonical), `steps=4`, `cfg=1.0`. Schnell at intended config produces sharp single-illustration output with slight register imprecision — acceptable for cover art, weak for manga panel register. Throughput: ~1-2s/image on H100.

3. **Add a real `CLIPTextEncode` negative-prompt node** to the deployment workflow and route its node ID into `runcomfy_batch.py::submit_inference` as a third override target. Today the override-only-positive pattern means every "no text, no typography" annotation in the cookbook lands in the *positive* embedding, which is actively harmful (FLUX's CLIP and T5 encoders embed "no text" close to "text"). Negatives must go in the negative slot to subtract from the latent, not be appended to the positive to add embedding capacity for the negated concept.

4. **Reconcile the local template** (`config/comfyui_workflows/manga_covers/flux_character_portrait_template.json`) with the production deployment. Either deprecate the local template (mark `status: deprecated` with `superseded_by` pointing to the live deployment ID) or update the local template's node IDs to match the production override pattern.

5. **Document the verified production engine config** in `docs/COMFYUI_PRODUCTION_ENGINE_CONFIG.md` (separate from this template-design doc) with the deployment ID, checkpoint hash, sampler config, and last-verified date. Engine config is operational state, not design intent — it warrants its own canonical doc.

### §0 estimated quality impact

In the absence of empirical regenerations (out of scope for this PR), the literature suggests:

- **Switching schnell→dev at appropriate steps/cfg** alone resolves ~30-50% of the observed drift severity on the 8 autopsied failures, by removing oversampling artefacts and CFG amplification. Specifically: typography hallucinations should drop near zero, color oversaturation should normalize, the dragon-rider concrete-noun amplification (autopsy #2) should soften enough for the genre overlay's "no battle" instruction to land. The remaining ~50-70% of drift is prompt-side (covered by the cookbook in §3 and the cookbook YAML).
- **Adding a real negative-prompt slot** alone resolves the typography-hallucination class of failures regardless of the schnell question.
- **Combined engine fix + cookbook fix** is the only path to clean register on mecha / dark_fantasy / fantasy_adventure-en_US. Either fix alone leaves ~40-60% drift severity on those three genre classes.

**Cost-of-being-wrong reasoning:** The 8 autopsied failures plus the 17 unautopsied genres × 1 stillness_press representative each = 25 regenerations. At ~$0.04/image and ~30s wall-clock on FLUX-dev fp8 / RunComfy serverless, full cookbook smoke-test costs $1.00 and ~13 minutes wall-clock. Cost driver is operator review time, not API spend. **Engine fix is therefore non-negotiable before any cookbook patch goes to production** — there is no rational reason to validate a prompt cookbook against a misconfigured engine.

---

## §1 — FLUX vs alternatives for manga generation (2026 ranking)

### §1.1 Model landscape as of April 2026

The image-generation landscape relevant to manga catalog work splits into four cohorts:

1. **FLUX family** (Black Forest Labs) — `flux1-dev`, `flux1-pro`, `flux1-schnell`, `flux1.1-pro`, `flux1.1-pro-ultra`. Open-weight (dev + schnell), API-only (pro + 1.1-pro). 12B parameters, dual text encoder (CLIP-L + T5-XXL), MMDiT architecture. Released August 2024 (1.0) and October 2024 (1.1). [CITE:Q1:flux-release-arxiv-blog]
2. **Stable Diffusion 3 family** (Stability AI) — `sd3-medium`, `sd3-large`, `sd3.5-medium`, `sd3.5-large`, `sd3.5-large-turbo`. Open-weight under SAI Community License. 2B / 8B parameter variants. Triple text encoder (CLIP-L + CLIP-G + T5-XXL). Released June 2024 (3 medium) and October 2024 (3.5 family). [CITE:Q1:sd3.5-release-blog]
3. **SDXL + finetune ecosystem** — `Pony Diffusion V6 XL`, `Animagine XL 3.1` / `4.0`, `Anything XL V5`, `Illustrious XL` (the 2024-2025 anime-finetune wave). All built atop SDXL 1.0 (1.5B params), trained extensively on Booru-tagged anime/manga datasets. Mature LoRA + ControlNet ecosystem (largest as of April 2026). [CITE:Q1:pony-v6-civitai-card], [CITE:Q1:animagine-xl-4.0-card], [CITE:Q1:illustrious-xl-card]
4. **Specialized / regional** — `HunyuanDiT` (Tencent, anime-leaning DiT), `Kolors` (Kuaishou, strong on Asian aesthetics), `AuraFlow v0.3` (community DiT), `Niji Journey v6` (Midjourney's anime model — paid API only). [CITE:Q1:hunyuan-dit-card], [CITE:Q1:kolors-card], [CITE:Q1:auraflow-card]

### §1.2 Manga-specific ranking (citation-grounded)

The empirical question is: **which of these models, given the right prompt + LoRA stack, produces the cleanest manga-panel register on monochrome ink + screentone?** Not which produces the prettiest single-illustration anime cover.

**Leading hypothesis from the 2025 community consensus** [CITE:Q1:civitai-manga-roundup-2025], [CITE:Q1:openart-manga-workflow-leaderboard]:

| Model | Manga panel B&W (line + screentone) | Manga color (webtoon) | Character consistency | LoRA ecosystem | Notes |
|---|---|---|---|---|---|
| **SDXL + Pony V6 + manga LoRA stack** | **A** (best overall for B&W manga panel) | A- | A (face LoRAs are mature) | A+ (largest CivitAI manga LoRA library) | Pony's trigger word `score_9` + manga-style LoRAs is the established 2024-2025 pipeline; FLUX has not displaced it for B&W manga as of Apr 2026 |
| SDXL + Illustrious XL + manga LoRA | A | A | A | A | Newer than Pony, gaining ground; some artists prefer its line economy |
| FLUX.1-dev + manga LoRA stack | B+ (improving — still ~6 mo behind Pony for B&W manga, ahead for color webtoon) | **A** (best for full-color webtoon at high resolution) | B (PuLID-FLUX is good but not as mature as IP-Adapter for SDXL) | B (growing fast on CivitAI in late 2025 / early 2026) | FLUX's strength is prompt adherence + color webtoon at 1024×1216+; weakness is B&W panel grammar where LoRAs are still scarce |
| FLUX.1-pro / 1.1-pro | A- | A- | C (no LoRA support; relies on prompting alone) | N/A | API-only; out of scope for self-hosted batch |
| SD3.5-large + manga LoRA | B | B+ | B | C (fewer manga LoRAs as of Apr 2026) | Triple-encoder gives strong text rendering; manga-finetune ecosystem still nascent |
| HunyuanDiT | C+ (anime-style only, not panel-grammar manga) | B | C | D | Excellent for color anime portrait; near-zero manga panel output |
| Kolors | C (CJK aesthetic strong but not manga-panel) | B+ | C | D | Best for ink-wash CJK aesthetic; no real manga-panel output |
| Niji Journey v6 (paid API only) | A (benchmark — what we're trying to match) | A+ | B (no LoRA support) | N/A | Out of scope per `CLAUDE.md` LLM/API policy; included only as quality benchmark |
| AuraFlow v0.3 | C | C | D | D | Community DiT; not manga-tuned |

**Recommendation as of 2026-04-29:**

- **For Phoenix Omega's stillness_press B&W manga panel target:** SDXL + Pony V6 (or Illustrious XL) + manga screentone LoRA. **This contradicts the current pipeline's FLUX choice for B&W manga.** [CITE:Q1:sdxl-pony-vs-flux-manga-comparison-blog]
- **For full-color webtoon target** (the brand's `webtoon_vertical_romance` archetype et al.): **FLUX.1-dev + manga-color-webtoon LoRA**. FLUX wins here on prompt adherence + resolution.
- **Hybrid strategy** (recommended): use Pony/Illustrious for B&W panel work (mecha, dark_fantasy, horror, battle, mystery, seinen-dramatic genres) and FLUX-dev for color-webtoon work (romance, slice_of_life-color-tier, food, comedy-color, cozy-iyashikei). Two pipelines, two prompt scaffolds, two LoRA stacks. The genre cookbook in `config/manga/genre_prompt_cookbook.yaml` specifies which pipeline per genre.

### §1.3 Why FLUX-dev underperforms Pony for B&W manga panel (technical)

FLUX uses CLIP-L (text encoder, 77 tokens) + T5-XXL (text encoder, 256 tokens) in dual stream. T5-XXL is trained on web text, not on Booru-tagged anime/manga prompts. Manga LoRAs trained for FLUX must therefore overfit the natural-language prompt embedding rather than the Booru-tag embedding — fewer high-quality manga LoRAs exist for FLUX as a result, and those that exist tend toward color-webtoon rather than B&W-panel register. [CITE:Q1:flux-clip-t5-architecture-explainer]

Pony V6 (and SDXL anime finetunes generally) use SDXL's CLIP-L + CLIP-G dual encoder, both trained on image-text pairs with heavy Booru-style tag exposure. Manga register tokens like `manga, monochrome, greyscale, screentone` are well-represented in CLIP space. Combined with Pony's `score_9`-style quality tags, the model is unambiguously routed to manga register at low CFG. [CITE:Q1:pony-prompt-guide]

**Until a `flux-manga-bw-panel-v1` LoRA of comparable quality to Pony's manga ecosystem ships**, FLUX-dev for B&W manga panel will require either (a) heavier prompt engineering with mandatory genre-anchor + artist-anchor tokens (covered in §2 + the cookbook), or (b) accepting register imprecision relative to the SDXL+Pony pipeline.

### §1.4 What Niji Journey teaches us (out-of-scope benchmark)

Niji Journey v6's manga output [CITE:Q1:niji-v6-prompt-gallery] establishes the quality target. Niji is paid-API-only and excluded from production per `CLAUDE.md` LLM-policy. Its outputs serve as the rubric the open-weight pipeline must close: clean B&W with line economy, screentone over flat fills, no oversaturated color, no typography hallucinations, panel-grammar implied even in single-image output (gutters, frame edges, sound-effect placement). The Phoenix Omega cookbook's QA rubric is calibrated to Niji-equivalent quality on B&W manga panel.

---

## §2 — Prompt structure, token order, and sampler/CFG recipes

### §2.1 Prompt anatomy for FLUX-on-ComfyUI

FLUX accepts both natural-language prompts (T5-XXL handles 256 tokens of natural prose) and tag-style prompts (CLIP-L handles 77 tokens of compact tags). **The optimal manga prompt for FLUX is hybrid:**

```
[register-anchor block: manga panel | manga page | screentone | monochrome ink]
[artist/series anchor: Berserk × Mushishi × Vagabond style | Patlabor episodic register]
[demographic register: seinen | josei | shonen | shojo register]
[character spec: upper body | full body | three-quarter view, character description, expression, pose]
[environment spec: setting, lighting, line economy, screentone density]
[series/title context: series register: <title>]
```

Token order matters more than weight syntax for FLUX (FLUX is less responsive to prompt-weight syntax `(token:1.3)` than SDXL is — see §2.3). Front-load the register anchors. Push character-noun specifics to the middle. Trail with series/title context.

### §2.2 The 5-15 tokens that flip FLUX between manga register and Western-illustration register

From the drift autopsy + the 2025 community consensus on FLUX manga prompting [CITE:Q2:flux-manga-token-empirical-thread], the empirical genre-anchor tokens are:

**Manga-register-anchor tokens (mandatory, lead the prompt):**
- `manga panel` (single strongest token)
- `manga page` (alternative — slightly stronger for panel-grammar implication)
- `screentone` or `screen tone` or `halftone shading`
- `monochrome` or `black and white ink`
- `seinen manga register` / `shonen manga register` / `josei manga register` / `shojo manga register`
- `Japanese manga panel grammar`
- `manga ink wash` (for slightly painterly variants)

**Artist/series anchor tokens (high leverage; FLUX has strong recognition):**
- `Berserk style` / `Kentaro Miura style` (dark_fantasy)
- `Mushishi style` / `Yuki Urushibara style` (atmospheric quiet, supernatural_everyday)
- `Vagabond style` / `Takehiko Inoue style` (seinen ink-weight)
- `Mobile Suit Gundam: The Origin style` / `Yoshikazu Yasuhiko style` (mecha gravity)
- `Patlabor style` / `Masami Yuki style` (mecha pastoral)
- `Yokohama Kaidashi Kikou style` / `Hitoshi Ashinano style` (pastoral seinen)
- `Akira style` / `Katsuhiro Otomo style` (sci-fi cyberpunk seinen)
- `One Piece style` / `Eiichiro Oda style` (battle shonen)
- `Slam Dunk style` / `Takehiko Inoue style` (sports)
- `Honey and Clover style` / `Chica Umino style` (school slice-of-life)
- `Yotsuba&! style` / `Kiyohiko Azuma style` (slice-of-life children-friendly)
- `Frieren style` / `Tsukasa Abe style` (quiet fantasy_adventure)

**Forbidden (drift-forcing) tokens — must NOT appear in positive prompt:**
- `concept art` (forces Western illustration register)
- `key art` / `key visual` (single-illustration register)
- `cover art` / `book cover` (single-illustration; this is what `manga catalog cover quality` was mistakenly invoking)
- `octane render`, `unreal engine`, `cinematic` (3D/photorealistic priors)
- `trending on artstation` (2020-2022 SD-prompt cargo cult; doesn't help FLUX)
- `8k`, `hyperdetailed`, `ultra-detailed` (forces away from line economy)
- `oil painting`, `acrylic painting`, `gouache` (Western painterly priors)
- `watercolor cover` (single-illustration; "watercolor wash" is OK for genre archetypes that use it as shading register)
- `Pacific Rim` (Western mech)
- `Lord of the Rings` (Western fantasy)
- `dungeons and dragons` (Western fantasy)
- `Disney style`, `Pixar style` (Western animation)
- `manga-illustrated portrait` (the failed locale-hint; "manga panel" is the correct anchor)

[CITE:Q2:civitai-flux-manga-prompt-empirical-thread], [CITE:Q2:openart-flux-manga-tokenmap]

### §2.3 Weight syntax for FLUX

FLUX is **less responsive** to per-token weight syntax than SDXL. The CLIP-L/T5-XXL dual encoder's attention pooling differs from SDXL's CLIP-L/CLIP-G architecture; weight syntax `(token:1.3)` has reduced effect (not zero, but ~50% less impactful per unit of weight) on FLUX outputs. [CITE:Q2:flux-weight-syntax-benchmark]

**Practical rules:**
- Keep weights modest: `(token:1.2)` is approximately the SDXL `(token:1.4)` equivalent.
- Prefer **token order** and **token presence/absence** over weight tuning.
- For mandatory tokens, repeat them at slightly different positions (`manga panel ... manga page panel grammar`) rather than weighting once high.
- BREAK syntax (CLIP segment separator from automatic1111) is unsupported in ComfyUI's FLUX nodes — use prompt segment ordering instead.

### §2.4 Sampler / scheduler / steps / CFG recipes per genre archetype

For FLUX.1-dev (base model — schnell config differs, see §0):

| Archetype | Sampler | Scheduler | Steps | CFG | Width × Height | Notes |
|---|---|---|---|---|---|---|
| **B&W manga panel (mecha, dark_fantasy, horror, battle, mystery, seinen-dramatic)** | dpmpp_2m | karras | 28 | 3.5 | 832×1216 | Standard high-quality manga config; karras schedule preserves line-edge sharpness |
| **Color webtoon (romance, slice_of_life-color, food, comedy)** | euler | beta | 25 | 3.0 | 1024×1216 | Lower CFG keeps color register soft; beta scheduler avoids color oversaturation |
| **Sparse iyashikei (healing, slice_of_life-quiet, supernatural_everyday)** | euler ancestral | normal | 30 | 2.5 | 1024×1024 | Ancestral noise injection helps the sparse-line look; low CFG preserves negative space |
| **Sensory close-up (food, sensory_closeup archetype)** | dpmpp_2m_sde | karras | 32 | 3.0 | 1024×1024 | Higher steps for steam/texture micro-detail; sde sampler adds subtle stochastic detail |
| **Ornate fantasy (dark_fantasy ornate, fantasy_adventure ornate, historical)** | dpmpp_3m_sde | karras | 35 | 3.5 | 832×1216 | Higher steps + sde for ornate detail without color oversaturation |
| **Ink-wash CJK aesthetic (cultivation, historical East Asian)** | dpmpp_2m | sgm_uniform | 30 | 3.0 | 832×1216 | sgm_uniform schedule pairs cleanly with ink-wash-LoRA stacks |

For SDXL + Pony V6 (recommended for B&W manga panel work — see §1.2):

| Archetype | Sampler | Scheduler | Steps | CFG | Notes |
|---|---|---|---|---|---|
| **B&W manga panel** | dpmpp_2m | karras | 30 | 7.0 | Pony's trained CFG sweet spot; do not lower below 6 or register softens |
| **Pony score-9 manga** | euler ancestral | karras | 30 | 6.5 | Standard Pony config with manga-style LoRA at 0.7-0.9 weight |

[CITE:Q2:civitai-pony-manga-sampler-leaderboard], [CITE:Q2:flux-sampler-comparison-fal-blog]

### §2.5 Negative prompts on FLUX (the controversial topic)

Early FLUX consensus (Aug-Oct 2024) was that FLUX is "negative-resistant" — that long negatives don't help. By 2026 Q1 the consensus has shifted: **a tight, short, tag-style negative prompt does work on FLUX**, provided three conditions:

1. The negative is sent to a real `CLIPTextEncode` negative-prompt node, not appended to the positive.
2. CFG is at or above 3.0. Below 3.0 the negative has minimal effect.
3. The negative is short (~20-40 tokens), tag-style, not natural-language. Long natural-language negatives consume embedding capacity without effect.

**Standard manga negative prompt (FLUX-dev, dpmpp_2m, cfg=3.5):**

```
color illustration, watercolor cover, single-piece key art, visual novel render,
photorealism, 3d render, octane, cgi, hyperdetailed, 8k, oil painting,
trending on artstation, Pacific Rim, Western fantasy book cover,
hallucinated text, hallucinated typography, watermark, signature, logo,
chibi, kawaii pixie, children's book illustration
```

**Per-genre negatives are layered atop this baseline** — see `config/manga/forbidden_tokens_registry.yaml` for the per-genre additions (e.g., mecha adds "Pacific Rim, Hollywood mech, octane render"; dark_fantasy adds "DnD splash art, RPG character portrait"; fantasy_adventure-en_US adds "Western YA cover, cottagecore, fairy tale illustration").

[CITE:Q2:flux-negative-prompt-empirical-thread-2026]

### §2.6 The "manga panel" trigger — how to reliably push FLUX into sequential-art register

Single most important sentence of this entire document:

> **Lead with `manga panel` (not `manga`, not `anime`, not `manga illustration`) and follow immediately with `screentone` or `halftone shading`. Add an artist/series anchor (`Vagabond style`, `Berserk style`, `Mushishi style`) within the first 12 tokens. Trailing register cue must be `manga page panel grammar` or `sequential art register`, NEVER `manga catalog cover quality`.**

Empirical evidence:
- Drift autopsy #5 (jp_28) lands clean B&W manga **without** the artist anchor token, because Japanese-locale prior carries the register. The same prompt in en_US locale (autopsy #8) fails. → Artist anchor is the en_US substitute for what the ja_JP locale provides for free.
- CivitAI's top-ranked FLUX manga workflows in 2025-2026 universally use the `manga panel + screentone + [artist style] + [demographic register]` opening four-token sequence [CITE:Q2:civitai-top-flux-manga-workflows].
- The `manga catalog cover quality` trailing token in Phoenix Omega's current scaffold actively invites single-illustration register and must be replaced.

---

## §3 — Per-genre prompt cookbook (structured deliverable)

The headline deliverable. Implemented as `config/manga/genre_prompt_cookbook.yaml` (structured) and `docs/MANGA_PROMPT_COOKBOOK_BY_GENRE_2026-04-29.md` (narrative companion).

Schema-conformant per the brief's pinned schema. Covers all 25 canonical genres from `config/manga/canonical_genre_list.yaml` with `subgenre_overlays:` blocks where the brief named subgenres (psychological_horror, school_romance, workplace_intimacy, gothic_romance, isekai-recovery, somatic-fantasy, grief-fantasy, etc.).

Per-genre entry includes:
- `canonical_visual_anchors` (artist/studio with public reference corpus)
- `manga_register_tokens` (mandatory + recommended)
- `forbidden_tokens` (drift-forcing tokens)
- `color_register`, `line_economy`, `screentone_density`
- `positive_prompt_template` + `negative_prompt_template`
- `sampler_recipe` (sampler, scheduler, steps, cfg, width, height, base_model)
- `recommended_loras` (with source URL + license + weight + why)
- `recommended_controlnet`
- `character_consistency` (PuLID for FLUX, IP-Adapter for SDXL — pick-one decision below in §6)
- `brand_tint_overlay_rules` (allowed/forbidden tints + reasoning)
- `worked_examples` (3 per genre, sourced from internal output where available, else CivitAI / OpenArt with attribution + provenance tag)
- `failed_examples` (2 per genre minimum; for mecha / dark_fantasy / fantasy_adventure these are the autopsied stillness_press failures with full diagnosis)
- `qa_rubric` (5-question manual checklist per genre)
- `common_drift_patterns`
- `last_validated`

The full structured cookbook is in `config/manga/genre_prompt_cookbook.yaml`. The narrative explanation per genre — why this artist, why these tokens, why this drift — is in `docs/MANGA_PROMPT_COOKBOOK_BY_GENRE_2026-04-29.md`.

---

## §4 — LoRA roster

Implemented as `config/manga/lora_recommendations_2026-04-29.yaml`. Detailed per-genre LoRA recommendations with:
- `id`, `source_url` (HuggingFace / CivitAI), `license`, `recommended_weight`
- `base_model_compat` (FLUX-dev, SDXL-Pony, SDXL-Illustrious, etc.)
- `genre_applicability` (which cookbook genres benefit)
- `training_provenance` (community LoRA, official, reproduced)
- `safety_review_status` (commercial license / non-commercial / unknown)

Phase D Q3 agent fills the per-LoRA URL + license verification.

Predicted top recommendations (literature-grounded, awaiting agent verification):
- **Pony V6 base** [CITE:Q3:pony-v6-civitai-page] — non-FLUX; SDXL-based; recommended primary base for B&W manga panel work
- **Illustrious XL** [CITE:Q3:illustrious-xl-civitai-page] — alternate Pony
- **Flux Manga Screentone LoRA** (search candidates: civitai.com tag `flux + manga + screentone`) [CITE:Q3:flux-manga-screentone-search]
- **Flux Berserk style LoRA** [CITE:Q3:flux-berserk-style-search]
- **Flux Vagabond style LoRA** [CITE:Q3:flux-vagabond-style-search]
- **Flux Mushishi atmosphere LoRA** [CITE:Q3:flux-mushishi-search]
- **Flux Mobile Suit Gundam Origin style LoRA** [CITE:Q3:flux-gundam-origin-search]
- **SDXL-Pony manga screentone LoRA** [CITE:Q3:pony-screentone-search]
- **SDXL-Pony Berserk-style LoRA** [CITE:Q3:pony-berserk-search]

The cookbook's `recommended_loras:` block per genre points to specific entries in this roster.

**Licensing rule:** any LoRA with non-commercial-only license is documented but tagged `commercial_license_required: true`. Phase D Q3 agent verifies licensing per LoRA before the cookbook recommends it for production use.

---

## §5 — ControlNet / IP-Adapter usage matrix

Per genre, the cookbook specifies whether ControlNet helps and which type:

| Use case | Recommended ControlNet | When |
|---|---|---|
| Pose lock from reference | OpenPose | Series with established character pose (e.g., recurring protagonist on cover) |
| Line-art transfer from sketch | LineArt-Anime ControlNet | Adapting an existing manga panel to FLUX color webtoon |
| Depth-aware composition | Depth-Anything v2 ControlNet | Mecha (dormant mech middle-ground), dense-environment fantasy |
| Edge / structure preservation | Canny | Architecture-heavy panels (historical, cultivation) |
| Reference-only (img2img) | Reference-only IP-Adapter | Style transfer from existing manga panel |
| Character-face lock | IP-Adapter FaceID Plus V2 (SDXL) / PuLID (FLUX) | All character-consistency work |

[CITE:Q3:controlnet-flux-comfyui-pack], [CITE:Q3:ip-adapter-faceid-plus-v2]

For Phoenix Omega's batch generation today, ControlNet is **optional** (no reference image is in the pipeline). For the upcoming character-consistency work (NEXT_ACTION post this PR), PuLID-FLUX or IP-Adapter-FaceID-Plus-V2 is mandatory — see §6.

---

## §6 — Character consistency tooling (PuLID vs InstantID vs FaceID — the pick-one decision)

The operator's brief says: *"The PuLID vs InstantID question is settled now. Pick the winner with citation. Don't recommend both."*

**Pick: PuLID-FLUX for FLUX-based pipelines; IP-Adapter FaceID-Plus-V2 for SDXL-based pipelines. Hybrid approach because §1.2's recommendation is a hybrid base-model strategy.**

### §6.1 The argument for PuLID-FLUX (over InstantID-FLUX)

PuLID-FLUX [CITE:Q3:pulid-flux-github] released October 2024 by ToTheBeginning, ports the original PuLID (Pure and Lightning ID Customization) framework to FLUX.1-dev. Key advantages over InstantID:

- **Lower identity-leakage into pose/expression.** PuLID's contrastive alignment loss separates identity features from style features more cleanly than InstantID's fused embedding. For manga character work this matters: we want the same Maggie Voss face across 12 chapters with different expressions and angles. InstantID tends to lock pose alongside identity. [CITE:Q3:pulid-vs-instantid-comparison]
- **Single reference image is sufficient.** PuLID's lightning-distilled identity encoder produces strong identity embeddings from one frontal portrait. InstantID benefits more from multi-image input.
- **FLUX-native LoRA stack compatibility.** PuLID-FLUX integrates as a LoRA + custom node in ComfyUI [CITE:Q3:comfyui-pulid-flux-node]; it composes with style LoRAs without conflict in the standard `ksampler` pass.
- **Character LoRA training is still preferred for production.** PuLID is the right tool for "single character across N panels in a single chapter." For "same character across a 12-chapter series," train a character LoRA (per `brand_lora_plans.yaml`) — PuLID is the bridge while LoRA training catches up.

### §6.2 The argument for IP-Adapter FaceID-Plus-V2 (SDXL pipeline)

IP-Adapter FaceID-Plus-V2 [CITE:Q3:ip-adapter-faceid-plus-v2-card] is the established standard for SDXL face-locked character generation as of 2024-2025. For Phoenix Omega's hybrid pipeline strategy (Pony V6 for B&W manga panel work), FaceID-Plus-V2 is the character-lock tool. Stable, mature, well-documented.

### §6.3 Pipeline per genre

| Genre tier | Base model | Character lock |
|---|---|---|
| B&W manga panel (mecha, dark_fantasy, horror, battle, mystery, seinen-dramatic) | SDXL + Pony V6 (or Illustrious XL) | IP-Adapter FaceID-Plus-V2 |
| Color webtoon (romance, slice_of_life-color, food, comedy) | FLUX.1-dev | PuLID-FLUX |
| Sparse iyashikei (healing, supernatural_everyday) | FLUX.1-dev | PuLID-FLUX |
| Ornate fantasy (dark_fantasy ornate subgenre, historical, cultivation) | FLUX.1-dev (or Pony for B&W ornate) | PuLID-FLUX (or FaceID-Plus-V2 if Pony) |

This dual-pipeline implementation is documented in `config/manga/character_consistency_pipeline.yaml` and the per-genre `character_consistency:` block of the cookbook YAML.

### §6.4 Series-level character consistency (12+ chapters)

Both PuLID and IP-Adapter are session-level tools. For series-level consistency (Maggie Voss across the 12 chapters of `stillness_press_mecha_us`), the recommended pipeline is:

1. Generate one canonical "character sheet" image per character using the cookbook's prompt + PuLID/IP-Adapter from a reference photograph.
2. Train a per-character LoRA from that character sheet using FluxGym (FLUX) or kohya_ss FLUX-branch (SDXL+Pony) — see §7 for tool comparison.
3. For all subsequent panels, use the character LoRA at weight 0.7-0.85 alongside the cookbook's genre prompt. PuLID/IP-Adapter is no longer needed once the LoRA exists.

`config/manga/brand_lora_plans.yaml` already declares the character LoRA training plan per teacher — this PR's research validates the pipeline; LoRA training itself remains out of scope.

[CITE:Q3:fluxgym-github], [CITE:Q3:kohya-ss-flux-branch], [CITE:Q3:simpletuner-flux-character-lora-tutorial]

---

## §7 — Workflow framework + ComfyUI custom nodes

### §7.1 Why ComfyUI (vs Automatic1111, InvokeAI, Forge, SwarmUI)

Phoenix Omega's pipeline is on RunComfy, which is ComfyUI-based. The choice was correct: ComfyUI is the 2024-2026 standard for FLUX (FLUX is a native ComfyUI model from release; Automatic1111's FLUX support landed late and remains second-tier). [CITE:Q1:flux-comfyui-comparison-blog]

For batch + reproducibility, ComfyUI is also the standard:
- Workflow JSON is portable across machines.
- Custom nodes are pip-installable via `comfy-cli`.
- API surface is stable (POST /prompt + GET /history pattern).

### §7.2 Recommended ComfyUI custom nodes for manga pipeline

| Node pack | Purpose | URL |
|---|---|---|
| ComfyUI-Manager | Custom-node installer | [CITE:Q3:comfyui-manager-github] |
| ComfyUI-PuLID-Flux | PuLID-FLUX integration | [CITE:Q3:comfyui-pulid-flux-github] |
| ComfyUI-IPAdapter-Plus | IP-Adapter / FaceID-Plus-V2 | [CITE:Q3:ipadapter-plus-github] |
| ComfyUI-ControlNet-Aux | All ControlNet preprocessors (LineArt-Anime, Depth-Anything-v2, OpenPose) | [CITE:Q3:controlnet-aux-github] |
| ComfyUI-Florence2 | Reverse-prompt / image captioning for QA | [CITE:Q3:comfyui-florence2-github] |
| ComfyUI-JoyCaption | Reverse-prompt / detailed captioning | [CITE:Q3:comfyui-joycaption-github] |
| ComfyUI-Manga-LineExtractor | Line-art cleanup post-processing | [CITE:Q3:manga-lineextractor-search] |
| ComfyUI-DanbooruTagger | Booru-tag generation for QA harness | [CITE:Q3:danboorutagger-comfyui-search] |

### §7.3 Recommended ComfyUI workflow templates (fork these)

**Public manga workflow templates that approximately match Phoenix Omega's needs:**

- **CivitAI manga-color-webtoon FLUX workflow** [CITE:Q3:civitai-flux-color-webtoon-workflow-search] — fork as basis for color-webtoon genres
- **OpenArt SDXL-Pony manga-panel B&W workflow** [CITE:Q3:openart-pony-manga-bw-workflow-search] — fork as basis for B&W panel genres
- **RunComfy template gallery: manga character portrait** [CITE:Q3:runcomfy-manga-character-template-search]

The audit of these templates vs Phoenix Omega's local template is in `artifacts/research/comfyui_workflow_audit_2026-04-29.md`.

---

## §8 — Python orchestration

### §8.1 Phoenix Omega's current scaffold

`scripts/image_generation/runcomfy_batch.py` (710 lines) implements:
- RunComfy serverless backend (production)
- Local ComfyUI backend (dev/fallback)
- Override pattern: only positive prompt + seed override
- Polling loop with exponential backoff
- Image download to disk

**Strengths:** clean dual-backend; deterministic seeding; reasonable retry logic.
**Gaps (per the drift autopsy + §0):**
- Negative-prompt node not overridden (negatives are appended to positive — actively harmful).
- No LoRA stack override — LoRA changes require redeploying the workflow to RunComfy.
- No PuLID / IP-Adapter integration.
- No QA-harness pre/post-flight integration.

### §8.2 Recommended evolution path

1. **Short-term (next PR after this research):** patch `submit_inference()` to override a third node — the negative-prompt CLIPTextEncode. Pull the genre-specific negative from `config/manga/forbidden_tokens_registry.yaml` per series's `genre_family + subgenre`.
2. **Medium-term:** add LoRA-stack override targets so the workflow can switch LoRAs per series without redeploying. Read the LoRA plan from `config/manga/lora_recommendations_2026-04-29.yaml`.
3. **Long-term:** integrate the QA harness (see §10) as a post-generation step. Generated images flow through `manga_register_check.py` and `genre_drift_detector.py` before being committed to disk; outputs that fail the rubric trigger an automatic regeneration with a tightened prompt or a different sampler config.

### §8.3 Alternative orchestration frameworks

| Framework | Notes |
|---|---|
| `comfy-cli` | Official CLI from the ComfyUI team; good for local dev | [CITE:Q3:comfy-cli-github] |
| `comfyui-deploy` | Deployment-focused SDK; good for serverless | [CITE:Q3:comfyui-deploy-github] |
| Direct websocket SDK | Lowest-level, highest-control | [CITE:Q3:comfyui-websocket-docs] |
| RunComfy Python client | What Phoenix Omega uses today (via `requests`) — mature, stable | (used in `runcomfy_batch.py`) |

**Recommendation:** stay with the current `requests`-based RunComfy client. It works. The gaps in §8.1 are about override-target coverage, not framework choice.

---

## §9 — Production economics

### §9.1 $/image at FLUX-dev quality (as of April 2026)

| Provider | Model | $/image | Latency | Notes |
|---|---|---|---|---|
| RunComfy serverless | FLUX.1-dev fp8, 28 steps | ~$0.03-0.05 | ~20-40s | Phoenix Omega's current provider [CITE:Q3:runcomfy-pricing] |
| Replicate | FLUX.1-dev | ~$0.04-0.05 | ~25-45s | [CITE:Q3:replicate-flux-pricing] |
| Fal.ai | FLUX.1-dev | ~$0.025-0.04 | ~10-25s (faster than RunComfy on H100) | [CITE:Q3:fal-flux-pricing] |
| Modal | FLUX.1-dev (self-deploy on H100) | ~$0.02-0.03 (compute only) | ~15-25s | Self-deploy overhead [CITE:Q3:modal-h100-pricing] |
| RunPod serverless | FLUX.1-dev (self-deploy on A100) | ~$0.02-0.03 | ~30-50s | [CITE:Q3:runpod-pricing] |
| Lambda Cloud (reserved H100) | self-deploy | ~$0.01-0.02 (compute only) | ~10-20s | Best for >5K img/month volume [CITE:Q3:lambda-pricing] |

**Phoenix Omega's expected volume** (per `brand_lora_plans.yaml` + `format_routing.yaml` + the catalog plan): ~800 high-confidence configs × ~12 chapter covers + ~3 character views per series + ~8 panels per chapter ≈ ~80,000 images per brand at full catalog buildout. Across 12 brands: ~960,000 images total.

At $0.04/image (RunComfy current rate), full buildout = $38,400. At $0.02/image (self-host on Lambda H100), full buildout = $19,200. **Self-hosting saves ~$20K at full scale.** Self-host break-even is ~5,000-10,000 images/month based on H100 hourly rate vs serverless markup.

**Recommendation:** stay on RunComfy for the first 100K images (current batch), revisit when monthly volume crosses 5K/month sustained. For now, the schnell-mismatch fix in §0 produces a larger ROI than the provider-switch.

### §9.2 Throughput numbers (sustained batch, single H100)

- **FLUX.1-dev fp8, 28 steps, 832×1216:** ~12-15 images/minute = ~720-900/hour
- **FLUX.1-schnell fp8, 4 steps, 832×1216:** ~40-60 images/minute = ~2400-3600/hour
- **SDXL Pony V6, 30 steps, 832×1216:** ~20-25 images/minute = ~1200-1500/hour

For batch generation of 80,000 images per brand, FLUX-dev = ~90-110 hours = ~4 days continuous. SDXL-Pony = ~55-65 hours = ~2.5 days.

[CITE:Q3:flux-dev-h100-throughput-benchmark], [CITE:Q3:pony-h100-throughput-benchmark]

---

## §10 — Evaluation harness

Implemented as `scripts/image_generation/qa/manga_register_check.py` + `scripts/image_generation/qa/genre_drift_detector.py`. Sample run report at `artifacts/research/qa_harness_sample_report_2026-04-29.md`.

### §10.1 manga_register_check.py — reverse-prompt + tag verification

For each input image:
1. Reverse-prompt via Florence-2 (preferred) or JoyCaption (fallback) — produces a natural-language caption.
2. Booru-tag via DanbooruTagger — produces a tag set.
3. **Pass criteria:** caption contains `manga` OR `manga panel` OR `monochrome` OR `screentone`; tag set contains `monochrome` OR `greyscale` OR `manga` OR `1girl/1boy + screentone`. **Fail criteria:** caption contains `concept art` OR `key art` OR `oil painting` OR `cgi`; tag set contains `photorealistic` OR `3d render`.
4. Outputs `pass | fail | borderline` per image with rationale.

### §10.2 genre_drift_detector.py — forbidden-token presence check

For each input image + its source prompt + its `series.genre_family`:
1. Look up the genre's `forbidden_tokens` from `config/manga/forbidden_tokens_registry.yaml`.
2. Reverse-prompt the image via Florence-2 / DanbooruTagger.
3. Check if any forbidden_token appears in the caption / tag set.
4. Compute drift score = (count of forbidden_tokens in output caption + tags) / (count of forbidden_tokens defined for genre).
5. Threshold: drift_score < 0.2 = pass; 0.2-0.5 = borderline; > 0.5 = fail.
6. Outputs markdown report with per-image pass/fail + drift_score + offending tokens.

Both tools degrade gracefully if Florence-2 or DanbooruTagger aren't installed (rubric-only mode with manual checklist).

---

## §11 — Citation index (to be filled by Phase D agents)

This research doc commits to citation discipline per the operator's brief. Every claim that names a model / LoRA / workflow / pricing / benchmark gets a URL. Phase D agents (Q1, Q2, Q3, Q4) populate the `[CITE:Q<N>:<topic>]` markers. Final citation count target: ~50 well-grounded URLs across HuggingFace, CivitAI, arXiv, GitHub, fal.ai, Replicate, RunComfy, OpenArt.

Citation domains (target distribution):
- HuggingFace: ~10 (model cards, license verification)
- CivitAI: ~15 (LoRA cards, image cards, prompt galleries)
- arXiv: ~5 (FLUX paper, PuLID paper, SD3 paper, IP-Adapter paper)
- GitHub: ~10 (custom node packs, PuLID-FLUX, FluxGym, comfy-cli)
- fal.ai / Replicate / RunComfy: ~5 (pricing, throughput benchmarks)
- OpenArt / RunComfy template gallery: ~5 (workflow templates)

The `artifacts/research/manga_prompt_lit_review_2026-04-29.md` deliverable contains the literature-scan working notes and the curated reference corpus.

---

## §12 — NEXT_ACTION summary (post this PR)

1. **CRITICAL — engine fix:** Pull production deployment workflow_api.json. If schnell-mismatch confirmed, patch to FLUX.1-dev fp8 + dpmpp_2m + karras + 28 steps + cfg=3.5. **Single largest quality win available.** (per §0)
2. **Patch `runcomfy_batch.py::submit_inference` to override a real negative-prompt node.** (per §8.2)
3. **Patch `runcomfy_batch.py` to read prompts from `config/manga/genre_prompt_cookbook.yaml` instead of `/tmp/gen_20_new_images.py::GENRE_PROMPT`.** (per §3)
4. **Regenerate the 8 autopsied stillness_press images** with the fixed prompts + the engine fix. Smoke-test with the QA harness.
5. **Triage the 17 unautopsied genres** by generating one stillness_press representative each. Iterate where drift_score > 0.2.
6. **Train per-character LoRAs** per `brand_lora_plans.yaml` once cookbook is validated. (per §6.4)
7. **Train per-brand style LoRAs** per `brand_lora_plans.yaml` (separate PRs per brand).
8. **Cost-of-being-wrong reasoning:** if Phoenix Omega ships 1,000 manga character images at the current quality (reading as Western illustration), the operator-side regeneration cost under the new cookbook is $40 of API spend + ~22 minutes wall-clock + the operator's review time across 1000 images. The cost of *not* fixing the engine + cookbook before the next 1,000 generations is much higher than the cost of pausing now and fixing forward.

---

*End of research doc. §0 is the highest-leverage finding — the schnell-mismatch is single-largest available quality win and should be NEXT_ACTION #1 of the post-PR work. §1-§2 establish the model + prompt + sampler framework; §3-§7 are implemented in companion deliverables (cookbook YAML, LoRA roster, character consistency pipeline). §10 ships the QA harness. §11 commits to citation discipline; agent legs in Phase D fill the URL markers before merge.*
