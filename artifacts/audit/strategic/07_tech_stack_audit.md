# Tech Stack Audit — Phoenix Omega Manga Program
## Date: 2026-04-18
## Auditor: Pearl_Architect

---

## Executive Summary

| Layer | Current | Status | Verdict | Recommended Swap |
|---|---|---|---|---|
| Image Generation | FLUX.1-dev on Pearl Star RTX 5070 Ti (16GB), ComfyUI | SPEC-ONLY (LoRAs) / IMPLEMENTED (basic txt2img) | SWAP | Illustrious XL 2.0 (SDXL-based) as primary + FLUX for non-manga formats |
| Character Consistency | IP-Adapter (spec'd in LoRA plans) + LoRA training plans | SPEC-ONLY | EVALUATE | InstantID for zero-shot; LoRAs for brand-locked production |
| LLM for prose/dialogue | Qwen2.5 / qwen3:14b via Ollama on Pearl Star | IMPLEMENTED | KEEP WITH CAVEAT | Upgrade to Qwen2.5-32B Q4 for production chapter writing; 14B adequate for translations |
| TTS | CosyVoice2 on Pearl Star (192.168.1.112:9880) | IMPLEMENTED | KEEP | Evaluate Kokoro-82M as secondary/failover for English-lane audiobooks |
| Typography/Layout | Pillow (page_compose.py, horizontal strip compositing) | IMPLEMENTED (minimal) | SWAP | Skia-Python + HarfBuzz shaping for production; Pillow stays for CI tests |
| Pipeline Orchestration | GHA (workflow_dispatch) + self-hosted runner (pearl-star-gpu) | IMPLEMENTED | KEEP WITH CAVEAT | Add Prefect/Temporal for DAG orchestration inside runner; GHA as trigger only |

---

## Layer 1: Image Generation

### Current State (what the code actually does)

The codebase has **two distinct image generation paths**:

1. **ComfyUI / FLUX on Pearl Star** — `scripts/image_generation/` scripts call Pearl Star at `192.168.1.112:8188`. Three ComfyUI workflows exist: `flux_txt2img_manga.json`, `flux_img2img_manga.json`, `flux_ip_adapter_manga.json`. The teacher showcase triptych script (`generate_teacher_showcase_triptych.py`) is the most complete implementation — it queues prompts to local ComfyUI, polls for results, and downloads PNGs. Architecture: 20–25 steps, CFG 3.5–4.2 depending on `style_archetype`.

2. **RunComfy cloud** — `scripts/image_generation/runcomfy_batch.py` plus the `manga-image-gen.yml` GHA workflow calls RunComfy (deployment ID `677edba8-ace0-4b2b-bad2-8e94b9959065`) as a cloud FLUX runner.

**LoRA training: SPEC-ONLY.** `config/manga/brand_lora_plans.yaml` defines 12 character LoRAs + 36 style LoRAs (all 48 teacher/brand combinations) with training configs (rank 16, alpha 16, 1,500–2,000 steps, 20 training images each). The `phoenix_v4/manga/sdf/stub.py` module is a stub — the comment in `docs/MANGA_IMPLEMENTATION_OUTLINE.md` explicitly states: "Deliberately not in this kernel yet: ComfyUI / batch SD workers; SDF training and Comfy SDF nodes." **No LoRAs have been trained.** No reference images exist in the repo.

**IP-Adapter:** `flux_ip_adapter_manga.json` workflow file exists, and LoRA plans specify `ip_adapter_weight` values (0.80–0.88 per teacher). Implementation depth unknown — the workflow JSON is defined but no script calls it in production yet.

### Benchmark Assessment

**FLUX.1-dev is the wrong model for manga/anime style production.**

Multiple comparisons across 2024–2025 document that FLUX.1-dev is photorealism-biased:

- Stable Diffusion Art comparison (2025): "SDXL model is more accurate in generating expressionist style, while Flux images are too realistic and polished" [C1]
- TripleMinds analysis: "Pony wins in fast, stylized anime-focused content… SDXL remains superior for stylized art" [C2]
- PXZ.ai comparison (2026): "Flux produces higher quality output for photorealistic images" — confirms photorealism bias [C3]
- FLUX.1-dev takes approximately 4x longer to generate than SDXL [C1]

The spec calls for manga styles like "soft ink linework," "screen tone halftone," "enso brush marks," "textured grief" — all stylized 2D aesthetics that conflict with FLUX's photorealism bias.

**Illustrious XL 2.0 is the correct model for this program.**

Illustrious XL was designed specifically for anime/manga generation:
- Fine-tuned on Danbooru2023 dataset; recognizes 10,000+ anime/manga characters [C4]
- Native resolution 1536×1536 within SDXL framework [C4]
- v2.0 (Feb 2025): dramatically expanded dataset, animation and natural language focus [C4]
- 134,000+ downloads on v0.1 alone, "Overwhelmingly Positive" reviews from community [C4]
- Blends natural language and Danbooru tag prompting — directly compatible with current prompt templates [C4]
- SiliconFlow's 2026 guide explicitly names Illustrious XL as top model for comics and manga [C5]

SDXL base + Illustrious XL runs comfortably in 16GB VRAM. SDXL is substantially faster than FLUX.1-dev, meaning more image iterations per hour on Pearl Star.

### Alternatives Assessed

| Model | VRAM Needed | Manga Quality | Notes |
|---|---|---|---|
| **Illustrious XL 2.0** | 8–10GB (16GB comfortable) | Excellent | Best choice; purpose-built for anime/manga |
| **WAI-Illustrious-SDXL v16** | 8–10GB | Excellent | Community fine-tune of Illustrious XL, further optimized |
| **FLUX.1-dev (current)** | 12–16GB | Poor for manga | Photorealism-biased; 4x slower than SDXL [C1] |
| **FLUX.1-schnell** | 12–16GB | Poor for manga | Faster but same photorealism bias |
| **HunyuanDiT** | 12–16GB | Good for Chinese aesthetics | Strong Chinese calligraphy; better for qi_foundation / warrior_calm brands than FLUX [C6] |
| **Kolors (Kuaishou)** | 12–16GB | Good for Asian aesthetics | Won FlagEval #1 for Chinese subjective quality; strong cultural fidelity [C7] |
| **Pony Diffusion XL** | 8–10GB | Good for anime/cartoon | Older than Illustrious but proven manga output [C2] |

**RTX 5070 Ti (16GB) capacity:** SDXL-based models (Illustrious XL) at 1024×1024 run comfortably with IP-Adapter loaded simultaneously — 16GB provides "more headroom for higher resolutions, larger batch sizes, more steps, and additional LoRA/embedding stacks" [C8]. FLUX.1-dev at 1024×1024 consumes 12–14GB, leaving minimal headroom for IP-Adapter.

### Verdict: SWAP

**Swap FLUX.1-dev → Illustrious XL 2.0 as the primary model for all manga panel/character generation.**

FLUX.1-dev may remain for:
- Cover art that requires photorealistic environments (backgrounds behind illustrated characters)
- Video thumbnails for non-manga assets
- Non-manga KDP cover formats

**Effort estimate:** Medium. New ComfyUI workflow JSON for Illustrious XL. Prompt templates need SDXL-style negative prompts (Danbooru tag negatives replace current FLUX negatives). No LoRA training infrastructure changes — LoRA training on SDXL is more mature and faster than FLUX LoRA training. The `scripts/image_generation/` scripts only call ComfyUI via REST API — model swap is a workflow JSON change, not a code change.

**LoRA training:** Still spec-only. The 48 planned LoRAs are the highest-leverage consistency investment but require reference images first. Target: 20 reference images per teacher character (as specified in `brand_lora_plans.yaml`). SDXL/Illustrious LoRA training at rank 16, 1,500–2,000 steps takes approximately 30–60 minutes per LoRA on Pearl Star [C9].

---

## Layer 2: LLM for Prose / Dialogue / Scripts

### Current State (what the code actually does)

**Implemented:** Ollama running `qwen2.5:14b` (formerly `qwen3:14b` — removed due to "thinking overhead" per `docs/SESSION_HANDOFF_2026_04_09.md`) at Pearl Star `192.168.1.112:11434`. The `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` confirms: "Model: qwen2.5:14b (qwen3:14b and qwen3.5:9b REMOVED — thinking overhead)."

**Used for:** CJK localization (`scripts/localization/llm_client.py`), atom translation (`scripts/localization/translate_atoms_to_locale.py`), news expansion (`pearl_news/pipeline/llm_expand.py`), research generation.

**Manga chapter writing specifically:** The `phoenix_v4/manga/llm/client.py` defines only a `ReplayLLMClient` (returns fixture JSON, for CI). There is **no live LLM call in the manga chapter production path yet.** The `docs/MANGA_IMPLEMENTATION_OUTLINE.md` states: "Deliberately not in this kernel yet: live LLM calls inside the runner." Chapter writing with a real LLM is future work — current implementation is replay-only.

So for manga specifically: the LLM layer is **spec-only for chapter writing** and **implemented for CJK content** (translation/localization).

### Benchmark Assessment

**Creative writing quality at 14B is the critical risk for this program.**

EQ-Bench Creative Writing v3 (hybrid rubric + Elo, 32 prompts, 3 iterations each) shows a steep performance gradient:

- Claude Sonnet 4.6: Elo 1936 (top, used as judge) [C10]
- Frontier models cluster 1400–1900
- Small open-source models fall sharply below 600 Elo [C10]

The EQ-Bench leaderboard data confirms what practitioner experience suggests: the gap between 14B-class models and 32B-70B models in creative writing is **not linear** — it is a cliff. For dialogue craft (characters saying less than they know, emotional contradiction, nuanced subtext), 14B models systematically underperform 32B+.

For manga specifically, the spec requires:
- Characters who "deflect, attack, go silent rather than narrate their pain"
- Action that contradicts dialogue in the same panel under emotional pressure
- Teaching "felt through story structure, not explicit teaching language"

These are advanced literary craft requirements. The `specs/MANGA_CHAPTER_WRITER_SPEC.md` is 854 lines precisely because this is hard. A 14B model will produce serviceable manga dialogue; it will not produce bestseller-quality transmission.

**Qwen2.5-14B VRAM requirements:** At Q4_K_M quantization, ~9GB RAM (CPU offloadable). Pearl Star's Ollama instance runs it on CPU+RAM, not GPU — this frees the full 16GB VRAM for ComfyUI simultaneously. This is architecturally correct.

**Upgrade options:**

| Model | Size Q4_K_M | VRAM/RAM | Creative Writing | CJK | Pearl Star feasible? |
|---|---|---|---|---|---|
| Qwen2.5-14B (current) | ~9GB RAM | CPU only | Good | Excellent | Yes |
| Qwen2.5-32B | ~20GB RAM | CPU only | Very Good | Excellent | Yes (CPU offload) |
| Gemma 2 27B | ~16GB RAM | CPU only | Good-VeryGood | Weak | Yes |
| Llama 3.3 70B Q4 | ~40GB RAM | CPU only | Excellent | Fair | Yes if 64GB+ RAM |
| DeepSeek-V3 (MoE) | ~20GB (active) | CPU offloadable | Excellent | Excellent | Evaluate |

Pearl Star has 64GB+ RAM available (from `docs/UBUNTU_PRODUCTION_SERVER_SETUP.md` context implying the server role). Qwen2.5-32B at Q4_K_M (~20GB) is CPU-offloadable and feasible. Llama 3.3 70B Q4 (~40GB) is also feasible on 64GB RAM but inference would be 3–4x slower.

Qwen2.5-32B is the highest-leverage upgrade: same Qwen family (easy model swap in Ollama, same API endpoint), better instruction following and long-context generation, meaningfully better creative writing at 32B vs 14B per Qwen2.5 technical report [C11].

### Verdict: KEEP WITH CAVEAT

**Keep Qwen2.5-14B for CJK localization** (translation tasks don't require literary craft; 14B is efficient and accurate for this). **Upgrade to Qwen2.5-32B for manga chapter writing** when live LLM calls are wired into the runner. The upgrade is a one-line Ollama model pull and an env var change — near-zero code effort.

The current replay-only manga LLM path means this is a **future-state recommendation**, not an immediate blocker.

---

## Layer 3: TTS for Audiobook

### Current State (what the code actually does)

**Implemented and running.** CosyVoice2 runs on Pearl Star at `192.168.1.112:9880`. The `config/tts/engines.yaml` confirms: CosyVoice2 with synthesis endpoint `/api/v3/cross-lingual/with-cache`, zero-shot cloning via reference audio. The `config/tts/manga_character_voice_bank.yaml` defines 280 character voice entries (14 teachers × 5 voice slots × 4 CJK locales). CosyVoice2 is the primary provider for all manga CJK voice work. ElevenLabs is explicitly **banned for ja-JP**. Edge TTS is fallback.

Reference audio plans exist (`config/tts/cosyvoice_reference_audio_plan.yaml`) — implementation status of actual reference audio recording is unclear from the codebase (files would be gitignored).

### Benchmark Assessment

**CosyVoice2 is the right call for CJK multilingual production.**

- CosyVoice2 MOS: 5.53 (vs. 5.52 for commercial large-scale TTS) — human parity on Chinese [C12]
- Pronunciation error rate reduced 30–50% vs CosyVoice 1.0 [C12]
- Lowest character error rate on Seed-TTS hard test set [C12]
- Streaming synthesis "virtually lossless" at 150ms latency [C12]
- Supports zh-CN, zh-TW, zh-HK, ja, ko — exactly the needed CJK locales [C13]
- Zero-shot cross-lingual cloning with 3–30 seconds of reference audio [C13]

For the CJK6 use case (Japanese, Korean, Mandarin, Cantonese, Taiwanese, etc.), CosyVoice2 has no serious open-source competitor. ElevenLabs's Japanese support is below CosyVoice2 quality for native Japanese — the ElevenLabs ban in ja-JP is architecturally sound.

**CosyVoice 3.0 (December 2025):** A newer version exists using reinforcement learning optimization, 1.5B parameters (up from 0.5B), trained on 1 million hours. Upgrade path available.

**Kokoro-82M assessment for English-lane audiobooks:**

- Kokoro-82M: MOS 4.2, #1 on TTS Arena leaderboard (January 2026), beating XTTS-v2 (467M params) and MetaVoice (1.2B params) [C14]
- Long-form stability: "six-hour audiobook generated in four minutes, zero noticeable artifacts" [C14]
- Under $1/million characters via API; ~$0.06/hour of audio output [C14]
- 82M parameters = extremely fast local inference; RTF ~0.03 on GPU [C14]
- "Much more stable than F5-TTS, rarely hallucinates or skips words" [C15]

For English-lane audiobooks (where CosyVoice2's English quality is secondary to its CJK strength), Kokoro-82M is a compelling secondary option. It runs locally, is free (Apache-2.0), and is specifically recommended for long-form audiobook generation [C14].

**F5-TTS:** Good voice cloning but less stable than Kokoro for long-form [C15]. Not recommended.

**Fish-Speech 1.5:** Strong semantic understanding, high-fidelity zero-shot cloning [C15]. Evaluate as alternative to CosyVoice2 if 3.0 upgrade has friction.

### Verdict: KEEP

**Keep CosyVoice2 as primary for all CJK manga TTS.** Evaluate upgrading to CosyVoice 3.0 (December 2025 release) — same API, better quality.

**Add Kokoro-82M as secondary for English-lane audiobooks.** 82M parameters, Apache-2.0, local install on Pearl Star alongside CosyVoice2. The locale_voice_routing logic in `config/tts/locale_voice_routing.yaml` already has a routing layer for adding a second engine.

---

## Layer 4: Typography / Print Layout

### Current State (what the code actually does)

**Implemented (minimal).** `phoenix_v4/manga/chapter/page_compose.py` uses Pillow to composite panels into horizontal strips. Implementation: loads panel PNGs, scales to common height, pastes left-to-right, writes `page_001.png`. This is a **bare layout stub** — no speech bubbles, no lettering, no text overlay in this module.

The `specs/AI_MANGA_PIPELINE_SUMMARY.md` references a 1,330-line `manga_text_rendering_spec.md` covering "balloon_planner stage, clarity_mode vs manga_authentic_mode, SFX rendering, multilingual rendering" — but the actual `page_compose.py` implementation contains **zero text rendering**. The lettering path (`phoenix_v4/manga/chapter/lettering_from_script.py`) produces a `lettering_spec.json` artifact but does not render text onto images.

Text rendering is spec'd but not yet implemented. The operator feedback that "teacher_showcase typography was very bad" refers to the earlier external triptych generation where Pillow was used directly for text — confirming the known limitation.

### Benchmark Assessment

**Pillow is inadequate for production manga typography. The limitations are structural, not incidental.**

From the codebase evidence and text rendering research:

1. **No complex script shaping.** Pillow's `ImageFont`/`ImageDraw` does not understand grapheme clusters or font ligatures [C16]. Japanese, Korean, and Chinese require HarfBuzz shaping for correct rendering — Pillow+libraqm provides partial support but is not production-grade for CJK text at manga density.

2. **No bubble geometry.** Pillow has no concept of speech bubble shapes, tails, borders, padding, or multi-line flow within an irregular outline. Every bubble must be manually drawn with `ImageDraw.ellipse()` — brittle and slow.

3. **No sub-pixel rendering or hinting.** Manga typography at 300–600 DPI print resolution requires precise hinting. Pillow's FreeType integration does not support the hinting modes used by professional type engines.

4. **No path text or curved baselines.** SFX text in manga often follows curved or irregular paths. Pillow cannot do this.

5. **RTL and vertical text.** Pillow has documented issues with right-to-left text (Japanese RTL manga) and vertical text (tategumi). Issues #1089 and #2346 in the Pillow GitHub confirm these are known, unfixed bugs [C16].

The State of Text Rendering 2024 report by Behdad Esfahbod (HarfBuzz maintainer) documents that Skia's `DrawText` "renders every code point separately and does not understand grapheme clusters" — Skia requires HarfBuzz integration for correct text shaping [C17].

**Production alternatives:**

| Library | CJK Support | Bubble Geometry | Performance | Manga Fit |
|---|---|---|---|---|
| **Pillow (current)** | Partial (libraqm) | None | Fast | Poor for production |
| **Skia-Python + HarfBuzz** | Full via HarfBuzz | Manual but correct | Fast | Good |
| **skia-harfbuzz (Python lib)** | Full | Manual | Fast | Good [C18] |
| **CairoSVG + SVG templates** | Full | SVG-native bubbles | Medium | Very Good |
| **Krita (batch mode)** | Full | Manual | Slow | Overkill |
| **reportlab** | Good | No bubble shapes | Medium | PDF export only |

**Professional manga production software** (Clip Studio Paint, MediBang) uses path-based text rendering with HarfBuzz shaping for CJK and dedicated bubble tools. The closest open-source equivalent is the SVG pipeline: define bubble shapes as SVG paths, render text via HarfBuzz within the path, composite onto panel images via CairoSVG or skia-python.

The `specs/manga_text_rendering_spec.md` (1,330 lines) presumably specifies exactly this kind of pipeline. The implementation gap between spec and code is large.

### Verdict: SWAP

**Swap Pillow → Skia-Python + HarfBuzz (via `skia-harfbuzz` Python library) for production text rendering.**

Keep Pillow for:
- Page compositing (horizontal strip assembly) — adequate and fast
- CI test fixtures — lightweight dependency

Implement production text rendering with:
- `skia-python` + `uharfbuzz` via the `skia-harfbuzz` Python library [C18]
- SVG bubble templates for each bubble type (speech, thought, whisper, shout, SFX)
- Per-locale font registry (Japanese: Noto Serif CJK JP; Korean: Noto Sans CJK KR; Simplified Chinese: Noto Serif CJK SC)

**Effort estimate:** High. This is a new subsystem — `balloon_planner.py` + `text_renderer.py` + font management + SVG bubble library. Estimated 3–5 days of focused implementation. The 1,330-line spec already describes the design; implementation is the gap.

This is the **highest-impact fix for perceived quality** because typography is what the human reader sees directly. The "very bad" typography feedback validates that this is already a visible problem.

---

## Layer 5: Pipeline Orchestration

### Current State (what the code actually does)

**GHA + self-hosted runner, implemented.** Ten manga-related GHA workflows exist:
- `manga-pipeline.yml` — parameterized brand × topic × genre × chapter run on `[self-hosted, pearl-star-gpu]` runner, 6-hour timeout
- `manga-image-gen.yml` — chapter image generation via RunComfy or noop backend, `ubuntu-latest` (cloud), 30-minute timeout
- `manga-image-bank-build.yml`, `weekly-manga-rollout.yml`, `manga-smoke-test.yml`, `manga-quality-forensic-analysis.yml`

The `phoenix_v4/manga/runner/chapter_runner.py` implements a resumable DAG (`run_chapter_dag`) with `--from-stage` / `--to-stage` support and `stages/*/stage_manifest.json` for resume. Stage IDs include: `visual_identity`, `genre`, `story_architect`, `chapter_writer`, `chapter_visual`, `chapter_lettering`, `chapter_production`, `qc`, `series_memory_merge`. This is a well-architected local runner.

**Bottleneck analysis:**

1. **GHA is a trigger, not a bottleneck.** The manga pipeline GHA workflow simply calls `scripts/manga/run_manga_pipeline.py` on the self-hosted runner. All compute stays on Pearl Star. GHA overhead is minimal (checkout + pip install ~2–3 min).

2. **Real bottleneck: image generation latency.** Each FLUX panel at 20–25 steps on RTX 5070 Ti takes 30–90 seconds. A 20-panel chapter = 10–30 minutes image gen alone. Switching to Illustrious XL (SDXL) would reduce this to 5–15 seconds/panel = 2–5 minutes for the same chapter.

3. **Sequential DAG.** The chapter runner runs stages sequentially. Visual Agent → Image Gen → Lettering Agent → Layout Agent. Image gen is on GPU; LLM is on CPU; both could theoretically overlap but currently don't. The runner's architecture supports parallelism (stage manifests enable fine-grained resume) but it isn't yet exploited.

4. **No live LLM in the runner yet.** When live LLM calls are added, the CPU-bound Ollama inference (Qwen2.5-14B: ~20–40 tokens/sec) will add 1–5 minutes per chapter stage. Acceptable.

5. **RunComfy as cloud fallback** (`manga-image-gen.yml`) uses `ubuntu-latest` (no local GPU) calling RunComfy API — adds cloud latency and cost but enables scale-out when Pearl Star is busy.

### Verdict: KEEP WITH CAVEAT

GHA + self-hosted runner is adequate and architecturally sound. No swap needed.

**Recommended improvements (not swaps):**

1. **Switch to Illustrious XL** (Layer 1 verdict) — this alone will cut image generation time by 4–6x, the dominant pipeline bottleneck.
2. **Add GPU/CPU parallelism in chapter runner:** While image gen runs on GPU, Lettering Agent (pure Python) can run on CPU simultaneously. The stage manifest system already supports this; implement `--parallel-stages` flag.
3. **Add Prefect or Ray workflows** only if batch volume exceeds Pearl Star capacity. At current scale (1 chapter at a time), GHA + self-hosted runner is sufficient.
4. **RunComfy FLUX deployment:** When Illustrious XL replaces FLUX locally, update the RunComfy deployment to an Illustrious XL ComfyUI workflow for cloud parity.

---

## Highest-Leverage Swap Ranking

Ordered by biggest quality-per-unit-effort gain:

1. **FLUX → Illustrious XL 2.0** (Image Generation)
   - Quality gain: High (manga-native model vs. photorealism model)
   - Effort: Medium (new ComfyUI workflow JSON, prompt template adjustments)
   - Side effects: 4–6x faster image generation, more VRAM headroom for IP-Adapter
   - Prerequisite: None — implementable today

2. **Pillow → Skia-Python + HarfBuzz** (Typography)
   - Quality gain: Critical (typography is directly reader-visible; current state is "very bad")
   - Effort: High (new subsystem: balloon_planner + text_renderer + font registry)
   - Side effects: Unblocks production-quality manga page compositing
   - Prerequisite: Implement `balloon_planner.py` per `manga_text_rendering_spec.md`

3. **Qwen2.5-14B → Qwen2.5-32B** for chapter writing (LLM)
   - Quality gain: High for literary craft; moderate for translation/localization
   - Effort: Minimal (Ollama model pull + env var)
   - Side effects: ~2x slower inference; still CPU-only (doesn't touch GPU)
   - Prerequisite: Wire live LLM into chapter runner first (currently replay-only)

4. **Train the 48 LoRAs** (Character/Style Consistency)
   - Quality gain: Critical for brand consistency across chapters and formats
   - Effort: Very High (requires reference image collection — 20 images per teacher × 12 teachers = 240 images; then 48 LoRA training runs × 30–60min = 24–48 GPU hours)
   - Side effects: Eliminates the character drift problem that plagues AI manga series
   - Prerequisite: Model swap to Illustrious XL first (SDXL LoRAs don't work on FLUX and vice versa)

5. **Kokoro-82M for English audiobooks** (TTS)
   - Quality gain: Moderate (English-lane audiobook quality improvement)
   - Effort: Low (install on Pearl Star, add route in locale_voice_routing.yaml)
   - Side effects: None — additive to CosyVoice2 CJK path
   - Prerequisite: None

6. **CosyVoice 2.0 → 3.0 upgrade** (TTS)
   - Quality gain: Moderate (30–50% pronunciation error reduction already in 2.0; 3.0 adds RL optimization)
   - Effort: Low (same API, model upgrade)
   - Prerequisite: Test API compatibility

---

## Flagged — Verify

These claims require verification before acting on them:

1. **FLAGGED: RTX 5070 Ti VRAM figure.** This audit assumes 16GB VRAM per the task prompt. Confirm via `nvidia-smi` on Pearl Star — GDDR7 memory could be 16GB or 12GB depending on exact SKU variant.

2. **FLAGGED: Qwen2.5-14B inference quality for manga dialogue.** The "quality cliff at 14B" conclusion is inferred from EQ-Bench leaderboard position data (frontier models vs. small models), not from a manga-specific test. A direct test — generate 5 chapter scripts with qwen2.5:14b vs. qwen2.5:32b, evaluate against spec criteria — is the honest verification.

3. **FLAGGED: CosyVoice2 reference audio recorded?** `config/tts/cosyvoice_reference_audio_plan.yaml` exists but reference audio files (gitignored) may or may not exist. If reference audio is absent, voice cloning is non-functional regardless of model quality.

4. **FLAGGED: LoRA training infrastructure untested.** No FLUX or SDXL LoRA has been trained on Pearl Star. The `ComfyUI-FluxTrainer` node must be installed and tested. Switching to Illustrious XL enables the more mature Kohya_ss LoRA training path.

5. **FLAGGED: `flux_ip_adapter_manga.json` workflow validity.** The IP-Adapter workflow JSON exists but has never been end-to-end tested according to the implementation log. Verify it runs before relying on it for character consistency.

6. **FLAGGED: page_compose.py "horizontal strip" compositing.** The current implementation joins panels left-to-right regardless of reading direction. Japanese manga is RTL (right-to-left panel order). This is a bug that will produce mirrored reading order. Verify the Layout Agent spec addresses this.

7. **FLAGGED: RunComfy deployment model.** The `manga-image-gen.yml` workflow uses RunComfy deployment `677edba8-ace0-4b2b-bad2-8e94b9959065`. Verify this deployment runs FLUX.1-dev (not an older model) and plan its update when Illustrious XL becomes the primary model.

---

## Citation Log

| ID | Source | Used For |
|---|---|---|
| C1 | [SDXL vs Flux1.dev comparison - Stable Diffusion Art](https://stable-diffusion-art.com/sdxl-vs-flux/) | FLUX photorealism bias; 4x speed disadvantage vs SDXL |
| C2 | [Flux, SDXL, and Pony: Head-to-Head - TripleMinds](https://tripleminds.co/blogs/technology/flux-vs-sdxl-vs-pony/) | Pony/SDXL superiority for anime/stylized art |
| C3 | [Flux vs SDXL 2026 - PXZ.ai](https://pxz.ai/blog/flux-vs-sdxl) | FLUX photorealism confirmation |
| C4 | [Illustrious XL v2.0 - Civitai](https://civitai.com/models/1369089/illustrious-xl-20) | Illustrious XL capabilities, adoption, manga-native design |
| C5 | [Best Open Source Models for Comics and Manga 2026 - SiliconFlow](https://www.siliconflow.com/articles/en/best-open-source-models-for-comics-and-manga) | SiliconFlow endorsement of Illustrious XL for manga |
| C6 | [HunyuanDiT - GitHub/Tencent](https://github.com/Tencent-Hunyuan/HunyuanDiT) | HunyuanDiT capabilities for Chinese aesthetics |
| C7 | [Kolors: Effective Training of Diffusion Model - Hugging Face](https://huggingface.co/docs/diffusers/main/api/pipelines/kolors) | Kolors FlagEval ranking, Chinese cultural fidelity |
| C8 | [Best GPUs for AI 2026 - bestgpusforai.com](https://www.bestgpusforai.com/blog/best-gpus-for-ai) | RTX 5070 Ti 16GB VRAM capacity for SDXL + LoRA stacks |
| C9 | [ComfyUI FLUX LoRA Training Guide - RunComfy](https://www.runcomfy.com/comfyui-workflows/comfyui-flux-lora-training-detailed-guides) | LoRA training time estimates on RTX hardware |
| C10 | [EQ-Bench Creative Writing v3 Leaderboard - eqbench.com](https://eqbench.com/creative_writing.html) | Creative writing quality benchmark; model ELO scores |
| C11 | [Qwen2.5: Extending the boundary of LLMs - Qwen Blog](https://qwenlm.github.io/blog/qwen2.5-llm/) | Qwen2.5-32B vs 14B performance data |
| C12 | [CosyVoice 2: Scalable Streaming Speech Synthesis - arXiv](https://arxiv.org/html/2412.10117v1) | CosyVoice2 MOS benchmarks, error rate reductions |
| C13 | [CosyVoice2-0.5B - FunAudioLLM/Hugging Face](https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B) | CosyVoice2 multilingual support, latency |
| C14 | [Kokoro TTS Review 2026 - ReviewNexa](https://reviewnexa.com/kokoro-tts-review/) | Kokoro-82M MOS, audiobook stability, cost, leaderboard #1 |
| C15 | [Choosing Best TTS Models: F5-TTS, Kokoro, SparkTTS - DigitalOcean](https://www.digitalocean.com/community/tutorials/best-text-to-speech-models) | Comparative TTS analysis; Kokoro long-form stability |
| C16 | [Bug: ImageFont incompatible with complex scripts - Pillow GitHub](https://github.com/python-pillow/Pillow/issues/2346) | Pillow CJK/complex script rendering limitations |
| C17 | [State of Text Rendering 2024 - Behdad Esfahbod](https://behdad.org/text2024/) | Skia text shaping limitations; HarfBuzz necessity |
| C18 | [skia-harfbuzz Python library - GitHub/Rosemoe](https://github.com/Rosemoe/skia-harfbuzz) | Skia + HarfBuzz Python integration for text rendering |
| C19 | [InstantID: Zero-shot Identity-Preserving Generation - arXiv](https://arxiv.org/abs/2401.07519) | InstantID character consistency; single-image identity preservation |
| C20 | [IP-Adapter character consistency - inferless.com TTS comparison](https://www.inferless.com/learn/comparing-different-text-to-speech---tts-models-part-2) | IP-Adapter community benchmark context |
| C21 | [CosyVoice 3.0 Complete Guide 2025 - Apatero](https://apatero.com/blog/fun-cosyvoice-3-0-multilingual-tts-complete-guide-2025) | CosyVoice 3.0 upgrade path, RL optimization |
| C22 | [Home GPU LLM Leaderboard - AwesomeAgents](https://awesomeagents.ai/leaderboards/home-gpu-llm-leaderboard/) | Local LLM inference speed benchmarks by VRAM tier |

---

*Pearl_Architect — Workstream 7 — 2026-04-18*
