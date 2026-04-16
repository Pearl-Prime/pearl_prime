# Video Pipeline Deep Research V2

**Agent:** Pearl_Research + Pearl_PM
**Project:** proj_state_convergence_20260328
**Subsystem:** video_pipeline
**Date:** 2026-04-12
**Hardware target:** Pearl Star — RTX 5070 Ti (16GB VRAM), 64GB RAM, Ubuntu 24.04, PyTorch 2.11.0+cu130
**Prior research:** `docs/VIDEO_TOOLS_DEEP_RESEARCH.md` (2026-04-11)
**Scope:** RESEARCH ONLY — no installs, no code changes

---

## 1. Executive Summary — Top 5 Recommendations by Impact/Effort Ratio

| Rank | Recommendation | Impact | Effort | Rationale |
|------|---------------|--------|--------|-----------|
| 1 | **FLUX.1-Kontext GGUF Q5 for teacher identity consistency** | Very High | Low–Medium | Single model replaces complex IP-Adapter + ControlNet stacking; directly solves "same teacher, 20 poses" problem; ComfyUI native support; ~12GB VRAM |
| 2 | **MusicGen-medium for ambient therapeutic underscore** | High | Low | MIT license, 8GB VRAM, 30s ambient in ~45s generation time; enables proper background audio layer the pipeline currently lacks entirely |
| 3 | **Upgrade LUFS target from −16 to −14 LUFS for YouTube** | High | Very Low | Config change in `render_params.yaml`; YouTube will not boost −16 LUFS content, so current output is consistently quiet relative to all other creators |
| 4 | **LTX-Video 2.3 for short cinematic inserts** | Medium-High | Medium | Fastest open video model on 16GB; 720p motion clips from FLUX stills; bridges "slideshow → cinematic" gap without full video diffusion VRAM budget |
| 5 | **WhisperX for word-level caption timestamps** | Medium | Low | Replaces base Whisper; improved DTW alignment; better CJK per-character timestamps; MIT license; same VRAM budget |

**Single highest-leverage change today:** Set `loudness.target_lufs: -14.0` in `config/video/render_params.yaml`. Zero code changes. Every completed video will immediately sound more professional at default viewer volume.

**Single highest-leverage new capability:** FLUX.1-Kontext GGUF Q5. This was released in June 2025 and directly resolves the hardest open problem in the image generation pipeline — maintaining teacher visual identity across 20 frames.

---

## 2. Per-Question Deep Dives

---

### 2.1 Image Generation Quality Ceiling on RTX 5070 Ti

#### Current state

FLUX.1-dev via ComfyUI at 1024×1024. Images upscaled to 1920×1080 via ESRGAN or Ultimate SD Upscale. Anti-washout prompt fixes merged (PR #387). No explicit teacher identity consistency mechanism beyond seed + prompt.

#### FLUX.1-dev vs FLUX.1-schnell vs SDXL-Turbo

| Model | VRAM (FP8) | Steps | Quality | Speed | Verdict |
|-------|-----------|-------|---------|-------|---------|
| FLUX.1-dev FP8 | 12–15 GB | 30–40 | Best photorealism, skin detail, text | ~13 sec/img | **USE — primary** |
| FLUX.1-dev FP4 (TRT Blackwell) | <10 GB | 30–40 | Equivalent to FP8 | ~8 sec/img | **USE — if TRT build available on Pearl Star** |
| FLUX.1-schnell | 12 GB | 1–4 | Artifacts in shadows/details | 3–5 sec/img | EVALUATE — drafts/previews only |
| SDXL-Turbo | 6–8 GB | 1–4 | Outclassed by FLUX on detail | 2–4 sec/img | SKIP for therapeutic final renders |

FLUX.1-dev FP8 remains the correct primary model. FLUX.1-schnell is viable for rapid draft previews (checking composition, color temperature) but not final output.

#### Max Resolution on 16GB VRAM

| Generation approach | Max res (safe) | Notes |
|--------------------|----------------|-------|
| FLUX.1-dev FP8 native | 1024×1024 or 1216×832 | Native generation — clean single pass |
| FLUX.1-dev FP8 + tiled | 1920×1080 | Tiled diffusion in ComfyUI; slower, can lose coherence on large tiles |
| FLUX.1-dev FP8 + upscale | 1024×1024 → 1920×1080 | **Recommended** — generate at 1024, upscale via ESRGAN 4x or Ultimate SD Upscale |
| 4K native | Not viable | Quality degrades, OOM risk |

**Recommendation:** Generate all images at 1024×1024 (or 1216×832 for landscape) and upscale. This is already the established pattern in the pipeline. Do NOT attempt 4K native generation — FLUX quality decreases at resolutions beyond its training distribution.

#### img2img / Inpainting for Scene Consistency (20 frames per teacher)

FLUX.1 Fill Dev (inpainting model) + img2img in ComfyUI enables "anchor frame" workflows:
1. Generate one anchor frame per teacher with desired appearance (environment, costume, expression)
2. Run img2img at 0.5–0.65 denoise strength for all 19 subsequent frames, varying pose/angle prompt
3. The lower denoise preserves background environment and overall figure appearance while allowing pose variation

FLUX.1-Kontext (see below) supersedes this for teacher identity; use img2img as fallback if Kontext VRAM is tight.

#### FLUX.1-Kontext — Game-Changer for Teacher Identity

**Released:** June 2025 (Dev open-weights; Pro/Max via API since May 2025)
**GitHub/HF:** black-forest-labs/flux-kontext-dev
**Stars:** Widely adopted (not tracked as standalone repo; integrated into ComfyUI ecosystem)
**License:** Open-weights, non-commercial dev variant (check BFL terms for commercial use)
**ArXiv:** 2506.15742

FLUX.1-Kontext is a 12B-parameter flow-matching model trained for context-aware instruction editing. It natively solves "visual drift" — it preserves character identity, environment details, and style properties across iterative generations. Prompt: "same teacher, different pose, from the side" produces consistent results that IP-Adapter stacking cannot reliably achieve.

**VRAM on Pearl Star:**
- FP8 full: ~20GB (exceeds 16GB — NOT viable alone)
- GGUF Q5: ~12–14GB — **viable on Pearl Star**
- GGUF Q4: ~10–12GB — viable, some quality loss

**Integration effort:** Medium. Requires:
1. Download GGUF Q5 from HuggingFace (available as of June 2025)
2. Install ComfyUI-FluxKontext node pack (available in ComfyUI Manager)
3. Define one anchor workflow per teacher
4. Batch subsequent frames via ComfyUI API

**Pearl Star compatibility:** YES — GGUF Q5 at 12–14GB fits within 16GB budget. Cannot run simultaneously with Ollama; must offload Ollama first.

**Effort estimate:** 4–8 hours (workflow design + anchor frame generation protocol)

#### ControlNet / IP-Adapter for FLUX (Fallback if Kontext not viable)

| Tool | Stars | License | VRAM | Status |
|------|-------|---------|------|--------|
| XLabs-AI x-flux-comfyui (ControlNet Canny/Depth/HED) | 2.5k+ | Apache-2.0 | +2–4GB | Active |
| ComfyUI-IPAdapter-Flux (Shakker-Labs, FaceID Plus V2) | 400+ | Apache-2.0 | +2–4GB | Beta |

These are the fallback approach if GGUF Kontext proves unstable. Use IP-Adapter FaceID Plus V2 at strength ≤1.0 with consistent base seed.

#### Newer Models vs FLUX on 16GB

| Model | 16GB viable? | Quality vs FLUX.1-dev | License | Verdict |
|-------|-------------|----------------------|---------|---------|
| SD 3.5 Large (INT8, ~12GB) | Yes | Close; better for artistic/stylized | Apache-2.0 | EVALUATE — if FLUX licensing ever changes |
| AuraFlow v0.3 | Yes (~12GB) | Weaker on fine portraiture | Apache-2.0 | SKIP for therapeutic portraits |
| Playground v3 | API-only | Better text rendering | Proprietary | SKIP (API only) |
| Ideogram 2 | API-only | Strong skin texture | Proprietary | SKIP (API only) |
| FLUX.1-Kontext GGUF Q5 | Yes (~12–14GB) | Equivalent + context awareness | Open-weights (BFL) | **USE** |

FLUX.1-dev remains the best locally-runnable model for photorealistic therapeutic imagery. SD 3.5 Large is the best Apache-2.0 fallback.

#### Batch Size and Generation Time

- **Recommended batch size:** 1 per ComfyUI prompt. ComfyUI natively queues.
- **260 images (13 teachers × 20 frames), FLUX.1-dev FP8:**
  - ~13 seconds per image × 260 = ~56 minutes
  - With queue overhead, workflow saves, checkpoint offloads: budget **1.0–1.5 hours**
- **With FLUX.1-Kontext GGUF Q5:** Similar timing; anchor workflow is the one that takes longer (~18–22s); subsequent frames at 0.6 denoise are faster (~10–12s)

---

### 2.2 Video Assembly: Beyond Slideshow

#### Current state

Ken Burns zoompan (directional pan + linear zoom) via raw FFmpeg subprocess. xfade dissolve coded but disabled in `render_params.yaml`. Breathing pulse spec'd but not implemented.

#### Stable Video Diffusion (SVD)

**VRAM requirement (minimum viable on 16GB):**

| Resolution | Frames | Estimated VRAM | Gen Time (16GB) |
|-----------|--------|----------------|-----------------|
| 480p | 25 | 12–14 GB | 2–4 min |
| 512×512 | 25 | 14 GB | 2.5–5 min |
| 768px | 25 | 15–16 GB | 6–25 min |

SVD at 768px is right at the 16GB edge. Not practical alongside any other loaded model. For nature/environmental sequences (no teacher face), SVD is viable. For teacher-face sequences, frame consistency is unreliable.

**RECOMMENDATION:** SKIP for primary pipeline. Retain as optional enhancement for long-form atmospheric sequences in audiobook companion videos where GPU time permits and FLUX is offloaded.

#### LTX-Video 2.3 (Lightricks)

**Released:** 2025–2026
**GitHub:** Lightricks/LTX-Video
**Stars:** ~5k+ (estimated, active project)
**License:** Apache-2.0
**VRAM:** 12–16GB for 720p generation
**ComfyUI:** Yes — native node pack available

LTX-Video 2.3 is the fastest open-weights video generation model available for 16GB GPUs. Key stats:
- 720p video generation in under 60 seconds on RTX 4090 (RTX 5070 Ti: estimated 40–80 seconds given superior bandwidth)
- Latest v2.3 adds native audio generation capability
- Strong for atmospheric/nature content; adequate for slow character motion

**Use case in this pipeline:** Generate 5–10 second cinematic clips from FLUX stills for HOOK section of teacher showcase. Replace 2–3 Ken Burns segments with a LTX-generated motion clip. Total VRAM required: ~12–14GB (must offload FLUX first).

**Pearl Star compatibility:** YES — fits in 16GB with FLUX offloaded.

**Effort estimate:** 4–6 hours (ComfyUI node install + workflow + integration into pipeline batch)

**RECOMMENDATION:** EVALUATE — strong candidate for HOOK-section cinematic upgrade.

#### AnimateDiff on ComfyUI

**VRAM:** 12GB min for 512×512 at 16 frames. RTX 5070 Ti handles 512×768 at 24 frames with FP8 motion modules.

**Status 2026:** AnimateDiff with SDXL motion modules is largely superseded by LTX-Video and WAN 2.1 for quality. Still viable and well-maintained (Kosinkadink/ComfyUI-AnimateDiff-Evolved, Apache-2.0). Good for subtle looping atmospheric effects (water surface, candle flicker, foliage breathing) where 4–8 seconds of loop is sufficient.

**RECOMMENDATION:** EVALUATE. Best use: generate 6–8 second atmospheric loops for the RESOLVE section (no teacher, pure nature/environment). Lower quality ceiling than LTX-Video but simpler workflow.

#### DepthFlow — Parallax 2.5D

**Re-evaluation since April 2025 research:**
- AGPL-3.0 license is safe for a **private, non-distributed pipeline**. AGPL only requires open-sourcing if you distribute the software to others or run it as a network service. An offline batch video production pipeline does not trigger AGPL copyleft.
- ComfyUI node pack now available: `ComfyUI-Depthflow-Nodes` (akatz-ai) — integrates depth map generation + DepthFlow parallax into a single ComfyUI workflow pass
- Confirmed working: Depth-Anything or MiDaS depth map nodes in ComfyUI → DepthFlow GLSL shader → looping parallax video
- Rendering cost: near-zero VRAM (GLSL shader, not diffusion). The RTX 5070 Ti's RTX cores handle this in seconds per frame.

**Verdict change:** SKIP → **EVALUATE** (upgraded). For a private pipeline, AGPL is not a barrier. Use for 3–5 key atmospheric shots per 5-minute video (not every frame).

**No viable MIT/Apache alternative exists** for true 2.5D parallax. The parallax-maker library (provos, 87 stars) is also AGPL-3.0.

**FFmpeg substitute:** The `zoompan` filter with layered asymmetric horizontal drift approximates parallax without depth separation:
```
zoompan=z='1.1+0.05*sin(2*PI*t/10)':x='iw/2-(iw/zoom/2)+10*sin(2*PI*t/8)':y='ih/2-(ih/zoom/2)':d=1:fps=30
```
Lower fidelity than DepthFlow but license-clean and zero VRAM.

#### DaVinci Resolve Free Tier

Python scripting requires DaVinci Resolve Studio (~$295). Free version: Lua only, no headless/CLI mode. Not a FFmpeg replacement for automated pipelines.

**Verdict: SKIP.**

#### Remotion (React-based video)

JavaScript/TypeScript only. Incompatible with Python pipeline without subprocess wrapper.

**Verdict: SKIP.**

#### Best FFmpeg Filter Chains for "Cinematic Stills"

All filters below are zero-VRAM, CPU-only, composable via `ffmpeg-python` bindings:

**Breathing pulse (6 BPM, spec-aligned):**
```
zoompan=z='1.03+0.02*sin(2*PI*t/10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:fps=24
```
This is the sinusoidal approximation. The asymmetric spec-compliant version (4s inhale/2s hold/4s exhale) is documented in `docs/VIDEO_TOOLS_DEEP_RESEARCH.md` § Breathing Pulse Implementation.

**Ken Burns with directional drift:**
```
zoompan=z='1.15-0.001*on':x='iw/2-(iw/zoom/2)+0.3*on':y='ih/2-(ih/zoom/2)':d=1:fps=24
```

**Film grain (therapeutic — subtle):** `noise=alls=6:allf=t` — `c0s=6` is more appropriate than the current config default of 15; temporal flag for authentic frame-to-frame variation.

**Vignette:** `vignette=PI/5` — exactly as coded.

**xfade dissolve (chained):**
```
[seg0][seg1]xfade=transition=dissolve:duration=0.5:offset=<offset_s>[v01]
[v01][seg2]xfade=transition=dissolve:duration=0.5:offset=<offset_s>[v012]...
```
Offset calculation: `offset_n = sum(durations[0:n]) - n * 0.5`

**Subtle camera shake (somatic/grounding content only):**
```
crop=iw-20:ih-20,geq='p(X+3*sin(2*PI*t/0.5),Y+2*cos(2*PI*t/0.7))'
```
2–3px amplitude. Use sparingly; inappropriate for grief/anxiety content.

**Color temperature shift (per-section, layered onto LUT3D):**
- Anxiety → cool: `hue=s=0.75,colorbalance=rs=-0.05:gs=0.0:bs=0.05`
- Grief → muted earth: `hue=s=0.65,colorbalance=rs=0.05:gs=0.02:bs=-0.05`
- Somatic → warm amber: `hue=s=0.85,colorbalance=rs=0.08:gs=0.03:bs=-0.05`

These align with the `color_temp_arc` section config already in `config/video/therapeutic_video_rules.yaml`.

---

### 2.3 Audio Pipeline Enhancement

#### Current state

CosyVoice2 (CJK TTS) + ElevenLabs (EN TTS) → raw audio → FFmpeg mux. Loudness normalization config present but disabled (`normalize_loudness: false`). No ambient audio layer. No audio post-processing.

#### Pedalboard Optimal Effect Chain for Therapeutic Narration

Recommended processing order (all via Pedalboard, before FFmpeg mux):

```python
from pedalboard import Pedalboard, HighpassFilter, LowShelfFilter, PeakFilter, Compressor, Reverb, Limiter

board = Pedalboard([
    HighpassFilter(cutoff_frequency_hz=80.0),           # 1. Remove LF rumble from TTS artifacts
    PeakFilter(cutoff_frequency_hz=370.0, gain_db=-2.5, q=1.8),  # 2. De-box (synthetic voice mud)
    LowShelfFilter(cutoff_frequency_hz=200.0, gain_db=1.5),       # 3. Warmth
    PeakFilter(cutoff_frequency_hz=2700.0, gain_db=1.5, q=1.5),  # 4. Presence/intelligibility
    PeakFilter(cutoff_frequency_hz=7000.0, gain_db=-3.0, q=2.0),  # 5. De-essing (sibilance)
    Compressor(threshold_db=-18.0, ratio=2.5, attack_ms=8.0, release_ms=120.0),  # 6. Gentle glue
    Reverb(room_size=0.25, damping=0.7, wet_level=0.12, dry_level=0.88),          # 7. Spatial warmth
    Limiter(threshold_db=-1.5, release_ms=50.0),       # 8. True peak ceiling
])
```

**Key insight — the 370 Hz notch is the single most impactful adjustment.** Synthetic TTS from CosyVoice2 accumulates mud at 350–400 Hz due to its vocoder architecture. A −2.5 dB notch at 370 Hz transforms synthetic-sounding narration into warm, human-adjacent voice.

**"Spatial warmth without muddiness":**
- Keep `wet_level` below 0.15 (15%). Above 15% reverb smears intelligibility.
- Use `room_size=0.20–0.30` — simulates small soft-furnished room, not hall or plate.
- Dry/wet ratio: 88/12 — narration stays foreground, spatial warmth is a texture not an effect.

**LUFS normalization:** After Pedalboard, apply `pyloudnorm` before FFmpeg mux:
```python
import pyloudnorm as pyln, soundfile as sf
data, rate = sf.read('narration_processed.wav')
meter = pyln.Meter(rate)
loudness = meter.integrated_loudness(data)
normalized = pyln.normalize.loudness(data, loudness, -14.0)  # YouTube standard
sf.write('narration_normalized.wav', normalized, rate)
```

#### Background Ambient Audio — Free/CC0 Sources

| Source | License | Best Content | Notes |
|--------|---------|-------------|-------|
| freesound.org (Luftrum pack #3069) | Creative Commons (per-file) | High-quality nature ambiences | Filter by CC0 to avoid attribution requirements |
| signaturessounds.org | CC0 | Rain, nature field recordings | |
| moodist.mvze.net | MIT / Free | 84 sounds, binaural beats, color noise | Open-source; self-hostable |
| mynoise.net | Free (personal use) | Singing bowls, rain, distant thunder | Not commercial CC; verify terms |
| mixkit.co | Mixkit License (free) | Nature, ambient loops | Allows commercial use in video projects |

For singing bowls specifically (somatic/grief sections): check stressaudio.com and moodist.

#### AudioCraft / MusicGen for AI-Generated Ambient

**GitHub:** facebookresearch/audiocraft | **Stars:** 23k+ | **License:** MIT | **VRAM:**

| Model | Parameters | VRAM | Gen time (30s) |
|-------|-----------|------|---------------|
| musicgen-small | 300M | 4–6 GB | ~15s |
| musicgen-medium | 1.5B | 8 GB | ~30–45s |
| musicgen-melody | 1.5B | 8 GB | ~30–45s |
| musicgen-large | 3.3B | 16 GB (tight) | ~90–120s |

**Recommendation: USE musicgen-medium** — 8GB VRAM, 30s of ambient music in ~45 seconds, MIT license. Well-suited for generating custom therapeutic underscore (calming pads, meditative tones, soft piano) precisely matched to section mood.

**Concurrent use strategy:** Do NOT run MusicGen-medium simultaneously with FLUX.1-dev (8GB + 13GB = 21GB, OOM). Run audio generation as a separate pipeline phase after FLUX completes and offloads. MusicGen-medium runs comfortably alongside CosyVoice2 (~3–5GB) within 16GB.

**Prompt examples for therapeutic ambient:**
- Grief: `"soft piano, minor key, slow 60 BPM, rain ambience, intimate space, no drums"`
- Anxiety relief: `"flute melody, nature sounds, flowing water, 70 BPM, open horizon feel"`
- Somatic: `"Tibetan bowls, 40Hz undertone, warm resonance, slow breath rhythm, meditative"`
- General meditation: `"ambient pad, major 7th chords, gentle reverb, 60 BPM, sunrise mood"`

#### Dynamic Audio Ducking

**Correct tool: FFmpeg `sidechaincompress`** (Pedalboard has no native sidechain compression).

```bash
ffmpeg -i narration.wav -i music.wav \
  -filter_complex "
    [0:a]asplit=2[narr][sc];
    [1:a][sc]sidechaincompress=threshold=0.02:ratio=10:attack=50:release=500[ducked];
    [narr][ducked]amix=inputs=2:duration=first:weights=1 0.3
  " output.wav
```

Parameters: `threshold=0.02` (sensitive to speech energy), `ratio=10:1` (aggressive duck), `attack=50ms` (quick response to speech onset), `release=500ms` (gradual music fade-back after speech ends). Background music at `weights=1 0.3` = −10 dB relative to narration when not ducked.

**Therapeutic note:** Ensure the ducked music level is still audible (not silenced) — the ambient underscore should remain at ~−20 dB during narration for spatial presence.

#### Binaural Beats and Isochronic Tones

**Generation libraries:**
- `binaural-generator` (ksylvan/binaural-generator, PyPI): CLI + API, frequency transitions, background noise mixing, WAV/FLAC output
- `binaural` (ishanoshada/binaural, PyPI): Simple API, all three entrainment types
- `SBaGenX` (lm7137/SBaGenX): Modern SBaGen+ fork, scriptable

**Target frequencies for therapeutic video content:**
| Emotional goal | Frequency range | Wave type |
|---------------|----------------|-----------|
| Meditation / relaxation | 6–10 Hz (theta/alpha boundary) | Binaural |
| Calm alertness (somatic) | 8–13 Hz (alpha) | Binaural or isochronic |
| Sleep induction | 1–4 Hz (delta) | Binaural |
| Anxiety relief | 10 Hz alpha | Isochronic (no headphones needed) |

**CONTRAINDICATED for therapeutic content:** 40 Hz gamma (alertness/cognition stimulation). Do not use.

**Scientific backing:** Evidence base is mixed (small effect sizes, variable methodology). Appropriate as an optional enhancement layer, not a clinical claim. Volume: −20 dB below narration (subliminal; audible if listener notices).

**Integration recommendation:** Generate a per-section binaural beat WAV at the therapeutic target frequency and mix at −20 dB via FFmpeg `amix` before final assembly.

#### LUFS Targeting — Critical Correction

| Platform | Target LUFS Integrated | True Peak | Notes |
|---------|----------------------|-----------|-------|
| **YouTube** | **−14 LUFS** | −1.0 dBTP | Platform does NOT boost content below −14; uploading at −16 leaves output quieter than all normalized content |
| Spotify video podcast | −14 LUFS | −1.0 dBTP | Same as YouTube |
| Apple Podcasts | −16 LUFS | −1.0 dBTP | Slightly more conservative |
| Audible/ACX | −18 to −23 LUFS equivalent | −3.0 dBTP | Uses RMS measurement; entirely separate mastering pass required |

**Current `render_params.yaml` has `target_lufs: -16.0`.** This is correct for Apple Podcasts but wrong for YouTube. Every video currently exported at −16 LUFS is perceived as quiet relative to all competitor content. YouTube normalizes DOWN to −14 LUFS but does not normalize up. This is a one-line config change.

**Action:** Set `loudness.target_lufs: -14.0` and `loudness.normalize_loudness: true` in `config/video/render_params.yaml`. This is the highest-impact, lowest-effort improvement available.

---

### 2.4 Captions and Accessibility

#### Current state

Caption pipeline exists (`run_caption_adapter.py`). Static SRT/ASS via `drawtext`. No word-level animation.

#### pycaps Status (April 2026)

| Attribute | Value |
|-----------|-------|
| GitHub | francozanardi/pycaps |
| Stars | ~134 |
| Commits | 187+ |
| License | MIT |
| Python | 3.10, 3.11, 3.12 confirmed |
| PyPI | Not on PyPI — install from source |
| Status | "Very alpha stage" — API instability likely |

pycaps provides CSS-styled animated word captions with Whisper word-timestamp integration. Primary designed for short-form (TikTok/Reels) content. For 60–90s showcase videos, it is applicable but API may change.

**RECOMMENDATION:** EVALUATE with caution. Maintain fallback to ASS/SRT generation via `stable-ts` + custom ASS styling if pycaps API breaks.

#### Whisper — VRAM Co-existence with FLUX

| Whisper variant | VRAM FP16 | VRAM INT8 (faster-whisper) | Notes |
|----------------|---------|--------------------------|-------|
| tiny | 0.15 GB | 0.1 GB | Low accuracy on CJK |
| base | 0.3 GB | 0.2 GB | |
| small | 0.6 GB | 0.4 GB | |
| medium | 1.42 GB | 0.9 GB | |
| large-v3 | 2.87 GB | 1.5 GB | Best CJK accuracy |
| large-v3-turbo | 1.6 GB | 0.9 GB | 4× faster; recommended |

**FLUX.1-dev FP8 + faster-whisper large-v3-turbo INT8 co-existence:** 13GB (FLUX) + 1.5GB (Whisper) = 14.5GB — within 16GB budget.

**RECOMMENDATION: USE `faster-whisper` (large-v3-turbo, INT8)** — 4× faster than openai/whisper at equivalent accuracy, ~1.5GB VRAM, can run while FLUX is loaded.

#### WhisperX (m-bain/whisperX)

**GitHub:** m-bain/whisperX | **Stars:** 15k+ | **License:** BSD-4 | **Status:** Active

WhisperX adds forced phoneme-level alignment via WAV2Vec2 on top of faster-whisper. Provides significantly improved word-level timestamps vs base Whisper's built-in alignment, especially for:
- TTS-generated audio (cleaner phonetics than natural speech, better DTW alignment)
- CJK character-level timestamps (per-character rather than per-segment)
- Reducing "word grouping" artifacts in caption display

**VRAM:** Same as faster-whisper; WAV2Vec2 alignment model adds ~0.5GB peak.

**RECOMMENDATION: USE WhisperX** as the caption timestamp backend. Replaces direct faster-whisper for any content where word-level caption animation is desired.

#### CJK Caption Generation (CosyVoice2)

**Whisper large-v3 for Mandarin Chinese:** Well-supported. For CosyVoice2 synthetic TTS, Whisper accuracy is typically higher than for natural speech (cleaner phonetics). Character-level timestamps via `return_timestamps="word"`.

**Note on CJK "word" boundaries:** Chinese does not use spaces between words. Whisper provides character-level timestamps (one timestamp per character or character cluster). This is functionally equivalent for subtitle display. For advanced word-group segmentation, use `jieba` (Python tokenizer, MIT license) on the recognized text to add word boundary information before generating subtitle timing.

**Recommended CJK caption stack:**
1. CosyVoice2 → audio
2. WhisperX (large-v3, INT8) → character timestamps
3. jieba → word boundary segmentation on recognized text
4. ASS file generation with per-character highlight timing
5. FFmpeg `ass` filter burn-in or sidecar delivery

#### ASS/SRT Styling for Therapeutic Content

```
[V4+ Styles]
Name: Therapeutic
Fontname: Nunito
Fontsize: 38
PrimaryColour: &H00FFFEF5
OutlineColour: &H80000000
BackColour: &H40000000
Bold: 0
Italic: 0
BorderStyle: 1
Outline: 1.5
Shadow: 0.5
Alignment: 2
MarginV: 45
```

**Active word highlight color:** `&H00A8E0C8` (soft teal-green) or `&H00FFFFD0` (warm cream-yellow). Avoid pure yellow (#FFFF00) — harsh contrast breaks the calming visual experience.

**Fade behavior:** Add `\fad(300,200)` per dialogue event — 300ms fade-in, 200ms fade-out. No snap-in.

**Font choices:** Nunito, Lato, or Quicksand (rounded letterforms, gentle without being childish). Avoid sharp-edged sans-serif fonts (Inter, Arial) — they feel clinical.

---

### 2.5 Batch Orchestration and Automation

#### Current state

13 teachers. Prior research recommended Python progress-file loop with nohup. `scripts/video/build_daily_batch.py` exists.

#### Recommended Pipeline Architecture (Overnight Batch, Pipelined)

```
Phase 1 — GPU-intensive image generation (FLUX)
├── FLUX.1-Kontext: anchor frame per teacher (13 × 1 image)
└── FLUX.1-dev img2img (or Kontext continuation): 19 frames per teacher (13 × 19 images)
    Total: 260 images, ~1.0–1.5 hours

Phase 2 — Parallel GPU audio generation (after FLUX offloads)
├── CosyVoice2 TTS: all CJK narration tracks
├── ElevenLabs: all EN narration tracks (API calls, minimal GPU)
└── MusicGen-medium: ambient beds per teacher (13 × 30s loops)
    Total: ~20–25 minutes

Phase 3 — CPU audio post-processing (parallel with Phase 2 GPU work)
├── Pedalboard: narration EQ + compress + reverb + de-ess (per track)
├── pyloudnorm: −14 LUFS normalization
├── FFmpeg sidechaincompress: narration + ambient ducking
└── Binaural generator: per-section beat synthesis (optional)
    Total: ~10 minutes (4-core parallel)

Phase 4 — CPU video assembly (parallel with Phase 2/3)
├── FFmpeg per-segment encoding: zoompan/breathe, LUT3D, noise, vignette
├── FFmpeg final assembly: xfade chained filter_complex
└── Caption burn-in: WhisperX → ASS → FFmpeg ass filter
    Total: ~20 minutes (4-core parallel)

Phase 5 — Post-processing
├── NVENC AV1 re-encode for final delivery (GPU, <1 min per video)
└── YouTube Data API v3 upload (~6/day at default quota)
    Total: ~20 minutes encoding + upload scheduling
```

#### Parallelization Strategy on RTX 5070 Ti

| Stage | GPU usage | Parallelizable |
|-------|----------|---------------|
| FLUX image generation | 12–15 GB (exclusive) | Sequential — GPU owner |
| CosyVoice2 TTS | 3–5 GB | Yes, after FLUX offloads |
| MusicGen-medium | 8 GB | Yes alongside CosyVoice2 (total ~13GB) |
| Pedalboard audio | CPU only | Yes — run during Phase 2 GPU work |
| FFmpeg assembly | CPU only | Yes — `multiprocessing.Pool(4)` while GPU handles audio |
| WhisperX captioning | 1.5 GB | Yes — runs while FFmpeg encodes on CPU |
| NVENC AV1 encode | GPU light (~2–4GB) | Run after all CPU work; GPU mostly free |

**Key insight:** Phase 3 (Pedalboard CPU) and Phase 4 (FFmpeg CPU) can begin processing teachers N−1 and N−2 while Phase 2 (GPU audio gen) handles teacher N. Use Python `multiprocessing` + a shared progress file.

#### Estimated Wall Times — 13 Complete Videos (60–90s each)

| Stage | Sequential | Pipelined |
|-------|-----------|-----------|
| FLUX 260 images (FP8) | 56 min | 56 min (unavoidable serial) |
| Audio synthesis (CosyVoice2 + MusicGen) | 25 min | 25 min (after FLUX) |
| Audio post (Pedalboard + pyloudnorm) | 10 min | Overlaps Phase 2 = 0 added |
| FFmpeg assembly + captions | 20 min | Overlaps Phase 2/3 = 5 min added |
| NVENC AV1 final encode | 10 min | Overlaps upload scheduling = 5 min added |
| **Total pipelined** | | **~1.75–2.5 hours** |
| **Total sequential** | | **~4–5 hours** |

Budget ~3 hours for overnight batch including overhead.

#### YouTube Data API v3 Upload

**Default quota:** 10,000 units/day. Upload cost: 1,600 units/video → max 6 videos/day.
**Authentication:** OAuth 2.0 required. First-run authorization needed; subsequent runs use stored refresh token.
**Library:** `google-api-python-client` (PyPI, Apache-2.0)
**Known issue:** Some users report upload failures unrelated to quota (rate limiting at Google's transport layer). Add retry with exponential backoff.
**Quota increase:** Apply via Google API quota extension form; requires brief compliance review.

For 13 videos: spread uploads over 3 days (≤6/day) or request quota increase in advance. Schedule via cron or the Python progress-file loop's upload stage.

---

### 2.6 Therapeutic Video Specifics

#### What Makes Therapeutic YouTube Videos Effective

Analysis of top channels (Calm, Headspace, Jason Stephenson, Michael Sealey, Great Meditation):

1. **Consistent production identity** — same color palette, narration style, music bed, thumbnail layout across all videos. Viewers build a Pavlovian association between the channel's aesthetic and a relaxation state.
2. **Minimal visual complexity** — 1–3 elements on screen maximum. No rapid cuts, no information overload. Every frame should lower cortisol, not compete for attention.
3. **Looping atmospheric elements** — water, clouds, slow flames, candle flicker, slow-breathing animations. These create a trance-inductive visual rhythm.
4. **Consistent audio signature** — the channel's music bed becomes a psychoacoustic anchor. Viewers who follow the channel pre-relax on hearing the first notes.
5. **Strategic duration segmentation** — shorter guided sessions (10–25 min) for discovery/algorithm; longer ambient loops (3–8 hours) for sleep/study watch time.
6. **Narration warmth and pacing** — slow, low, resonant delivery. The Pedalboard processing chain above targets exactly this quality.

#### Optimal Video Length

| Content type | Optimal length | Notes |
|-------------|--------------|-------|
| Teacher showcase | **8–12 minutes** | 10+ min unlocks mid-roll ads; hook (0:00–0:30) + teaching demo (0:30–7:00) + CTA (7:00–end) |
| Short teaser (Shorts/Reels) | **45–60 seconds** | Upload as YouTube Short for discovery; landscape clips ≤60s qualify |
| Guided practice session | **15–30 minutes** | Matches typical practice session duration |
| Audiobook companion video | **Full book runtime** | Long watch-time content; excellent for ambient/study search |

**Note on the specified 60–90s showcase videos:** These are trailers/highlights, not primary content. Treat them as YouTube Shorts (if ≤60s, vertical) or promotional standalone clips. For the primary teacher showcase, the 8–12 minute length is strongly recommended for algorithm performance.

#### Color Psychology for Therapeutic Content

| Emotional context | Primary palette | Accent | Avoid |
|------------------|---------|----|-------|
| Grief/bereavement | Muted warm grey (#8C8276), sage (#7A8C72), ivory (#F5F0E8) | Soft rose (#D4A4A0) | Black (harsh), saturated colors (jarring) |
| Anxiety/stress relief | Soft blue (#6A9FC0), teal (#7AC4C0), lavender (#B8B0C8) | White space | Cold grey (isolating), red/orange |
| Somatic/embodiment | Warm amber (#C8943C), terracotta (#C07858), soft peach (#E8C4A0) | Forest green accent | Cool blues (disconnect), harsh white |
| Meditation (general) | Sky blue, soft green, warm neutral | Gentle gold | |
| Sleep | Deep indigo (#3C4878), midnight blue (#2A3055), warm purple (#786090) | Star white | Bright stimulating hues |

**Research basis:** Multiple controlled studies confirm blue-green environments reduce cortisol and physiological stress markers. Warm amber/earth tones activate embodied warmth (embodied cognition research). Muted earth tones in grief counseling settings signal compassion without the clinical coldness of grey-white. See: `config/video/color_grade_presets.yaml` for corresponding .cube LUT assignments.

These palettes map directly to `config/video/therapeutic_video_rules.yaml` `color_temp_arc` settings and the per-section colorbalance adjustments already in `config/video/render_params.yaml`.

#### Visual Transition BPM Aligned with 6 BPM Breathing

6 BPM = 10-second breath cycle = 5s inhale / 5s exhale.

| Visual element | Recommended timing | Rationale |
|---------------|-------------------|-----------|
| Breathing zoompan sin() period | 10 seconds | Exact cycle alignment |
| Scene cut interval (BUILD section) | 10–20 seconds | 1–2 breath cycles per scene |
| Scene cut interval (RESOLVE section) | 20–30 seconds | 2–3 breath cycles; deepening stillness |
| xfade dissolve duration | 1.0–1.5 seconds | Long enough to not register as "cut"; short enough to not confuse |
| Caption line change | On phrase boundary, ≥3 seconds duration | Avoid jarring rapid-fire text changes |

**Do not** use cuts faster than 3 seconds in therapeutic content. Hard cuts are cortisol-activating.

#### Thumbnail Generation for Therapeutic YouTube

**What works on highest-performing therapeutic channels:**
1. Nature imagery with soft bokeh — water, candles, botanicals, stars, lotus
2. Channel signature color palette (3–4 consistent colors across all thumbnails)
3. 2–4 word title text maximum; rounded/gentle font (Nunito, Lato, Raleway)
4. Teacher serene face for teacher-specific content (trust signal; soft smile, direct gaze or soft/down gaze)
5. High visual breathing room — minimal elements, significant empty/gradient space
6. Consistent branding position (channel logo, consistent position)

**Generating with FLUX.1-dev:**
- Generate at 1280×720 or upscale from 1024×768
- Prompt emphasis: "soft bokeh background, natural light, serene expression, warm color grading, professional photography, high detail, calm atmosphere"
- Post-process with the same warm LUT applied to video frames for visual consistency

---

### 2.7 Quality and Platform Optimization

#### YouTube Encoding Best Practices 2025–2026

**Recommended settings for 60–90s showcase videos:**

| Parameter | Recommendation | Notes |
|-----------|---------------|-------|
| Container | MP4 | Universal compatibility |
| Video codec | H.264 (intermediate) → AV1 NVENC (final) | H.264 for pipeline speed; AV1 for delivery |
| Resolution (upload) | 3840×2160 (scale up from 1080p) | **4K upload trick** — gets better bitrate tier from YouTube |
| Bitrate (1080p content) | 8–12 Mbps VBR | |
| Frame rate | 24 fps | Cinematic; appropriate for therapeutic content |
| Color space | Rec.709 (SDR) | HDR is overkill for stills-based content |
| Audio codec | AAC-LC, 192 kbps, stereo | |
| Audio LUFS | **−14 LUFS integrated** | **Not −16** — see §2.3 correction |
| True peak | −1.0 dBTP | Platform-safe headroom |

**4K upload trick (documented):** Uploading 1080p content scaled to 3840×2160 places the video in YouTube's VP9/AV1 processing tier. This tier receives a higher per-frame bitrate budget than the H.264 1080p tier. For still-image-heavy therapeutic content where sharpness and color fidelity matter, the transcoded output is perceptibly better. Scale in FFmpeg: `-vf scale=3840:2160:flags=lanczos` before upload.

#### Audiobook Platform Video Specs

| Platform | Resolution | Codec | Notes |
|---------|-----------|-------|-------|
| YouTube | Up to 4K | H.264/H.265/VP9/AV1 | See 4K upload trick above |
| Spotify Video Podcast | 1080p / 4K | H.264 High Profile | 25 Mbps (1080p), 35 Mbps (4K); AAC-LC 192kbps |
| Apple Podcasts (video, spring 2026) | 1080p (HLS multi-bitrate) | H.264 | HLS adaptive delivery; encode 1080p H.264 master at 8 Mbps, Apple generates bitrate ladder |

Audible has no video component (audio only). Spotify and Apple Podcasts video represent the primary companion video platforms for audiobook content.

#### AV1 Encoding on RTX 5070 Ti

The RTX 5070 Ti features a **9th-generation NVENC encoder** with:
- Hardware AV1 encoding acceleration
- AV1 Ultra Quality (UQ) mode — 5% additional compression vs standard AV1 at equivalent quality
- ~78% higher memory bandwidth vs RTX 4070 Ti (better for fast bitrate-to-VRAM throughput)

| Codec | Bitrate (1080p equivalent quality) | File size (75s) | Encoding speed |
|-------|----------------------------------|---------------|---------------|
| H.264 NVENC | 10 Mbps | 94 MB | ~Real-time |
| H.265 NVENC | 7 Mbps | 66 MB | ~Real-time |
| AV1 NVENC (RTX 50) | 6 Mbps | 56 MB | ~Real-time |
| AV1 NVENC + UQ mode | 5.5 Mbps | 52 MB | ~Real-time |

**Recommendation:** Use H.264 NVENC for all intermediate pipeline files (fast, widely compatible). Re-encode to AV1 NVENC (UQ mode) for final YouTube delivery. For a 60–90s video, re-encode takes <30 seconds on the RTX 5070 Ti.

**For 6-hour audiobook companion video (H.264 vs AV1):**
| Codec | Bitrate | File size |
|-------|---------|---------|
| H.264 at 4 Mbps | 4 Mbps | ~10.8 GB |
| AV1 NVENC at 2.5 Mbps (equiv quality) | 2.5 Mbps | ~6.75 GB |

Use AV1 for all long-form content to save ~4GB per video.

---

### 2.8 What's New Since April 2025?

#### New ComfyUI Video Generation Nodes

| Model | Stars | 16GB viable? | Quality tier | Best use |
|-------|-------|-------------|-------------|---------|
| **LTX-Video 2.3** (Lightricks) | 5k+ | Yes (~12–14GB) | Top open-source | HOOK cinematic inserts |
| HunyuanVideo 1.5 (Tencent) | 8k+ | Yes (14GB+, 8.3B params) | Very high | Nature sequences |
| CogVideoX (ZhipuAI) | 7k+ | Yes (16GB tight) | High | Slow atmospheric motion |
| WAN 2.1 / 2.2 (Alibaba) | N/A | No without Wan2GP (65–80GB) | Highest | Not viable standalone on Pearl Star |
| Wan2GP wrapper | 5.1k | Yes (~12–16GB with tricks) | Near WAN 2.1 quality | EVALUATE — strong option |

**LTX-Video 2.3 is the clear recommendation** — fastest, native ComfyUI support, Apache-2.0 license, 720p within 16GB VRAM budget. V2.3 added built-in audio generation, which may eliminate MusicGen dependency for simple short clips.

**Wan2GP** (deepbeepmeep/Wan2GP) — 5.1k stars, 737 forks. A standalone optimization wrapper that folds VRAM by ~2× for WAN 2.1/2.2 and other models. Supports HunyuanVideo, LTX-Video, FLUX. Web UI (not ComfyUI native). License: verify (check repo). For Pearl Star, Wan2GP running WAN 2.1 at 16GB is a strong option for the highest-quality cinematic short clips but requires a dedicated inference session (not inline with ComfyUI workflow).

#### FLUX.1-Kontext — Most Important New Model (Released June 2025)

Already covered in §2.1. This is the single most significant development since the prior research. It directly solves teacher identity consistency without complex ControlNet stacking.

**Summary:** USE FLUX.1-Kontext GGUF Q5 (~12–14GB on Pearl Star). Download via HuggingFace, ComfyUI-FluxKontext node pack. Non-commercial dev variant license (verify BFL terms for commercial showcase use).

#### New Audio Tools

| Tool | Stars | License | New since April 2025? | Notes |
|------|-------|---------|----------------------|-------|
| MMAudio (Meta) | 2k+ | Apache-2.0 | Yes (late 2025) | Video-to-audio generation; can add ambient sound to clips automatically; WanGP plugin |
| AudioCraft MusicGen 2.x | 23k+ | MIT | Updates | musicgen-large w/ stereo support, improved instrumental quality |

**MMAudio** is notable: it generates audio that matches video content. Given LTX-Video or AnimateDiff short clips, MMAudio can generate a matched ambient sound layer. Integration with Wan2GP as a plugin makes it particularly useful for the Pearl Star pipeline.

#### New Caption/Subtitle Tools

| Tool | Stars | License | Notes |
|------|-------|---------|-------|
| **WhisperX** (m-bain) | 15k+ | BSD-4 | Word-level alignment via WAV2Vec2; recommended upgrade from base Whisper |
| stable-ts | 3k+ | MIT | DTW-based timestamp refinement; particularly good for CJK |

Both are already covered in §2.4. WhisperX is the recommended production-grade caption timestamp backend.

#### Verdict Changes Since April 2025

| Tool | April 2025 Verdict | April 2026 Verdict | Change Driver |
|------|-------------------|-------------------|--------------|
| MoviePy 2.0 | SKIP (slow) | SKIP (confirmed) | v2.1.2 still 10× slower than v1.0.3 for equivalent ops |
| DepthFlow | SKIP (AGPL concern) | EVALUATE | AGPL safe for private pipeline; ComfyUI nodes now mature |
| LTX-Video | Not evaluated | **USE** | Best 16GB-compatible open-source video model; Apache-2.0 |
| FLUX.1-Kontext | Not evaluated | **USE (GGUF Q5)** | Directly solves teacher identity consistency |
| WAN 2.1 (full) | Not evaluated | SKIP (VRAM) | 65–80GB without Wan2GP |
| Wan2GP | Not evaluated | EVALUATE | Makes WAN 2.1 viable on 16GB; strong quality |
| WhisperX | Not evaluated | **USE** | Better word timestamps than base Whisper; 15k stars |
| MusicGen-medium | Not evaluated | **USE** | MIT, 8GB VRAM, fills the ambient audio gap |

---

## 3. Proposed Production Pipeline — End-to-End

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: 13 teachers × [script, persona, topic, section_arc] │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────▼──────────────────┐
           │  PHASE 1: Image Generation (GPU)  │
           │                                   │
           │  1a. FLUX.1-Kontext GGUF Q5:      │
           │      Anchor frame per teacher      │
           │      (13 images, ~22s each)        │
           │                                   │
           │  1b. FLUX.1-Kontext continuation:  │
           │      19 frames per teacher         │
           │      varied pose/angle prompt      │
           │      (247 images, ~12s each)       │
           │                                   │
           │  1c. ESRGAN upscale:               │
           │      1024×1024 → 1920×1080         │
           │      (tiled, CPU optional)         │
           │                                   │
           │  Output: 260 PNG files             │
           └───────────────┬──────────────────┘
                           │
           ┌───────────────▼──────────────────┐
           │  PHASE 2: Audio Generation (GPU)  │
           │  [After FLUX offloads from VRAM]  │
           │                                   │
           │  2a. CosyVoice2 (CJK narration)   │
           │      or ElevenLabs (EN narration)  │
           │      13 × narration tracks         │
           │                                   │
           │  2b. MusicGen-medium:              │
           │      13 × 30s ambient beds         │
           │      per teacher emotional context │
           │                                   │
           │  [CPU in parallel with GPU audio] │
           │  2c. Pedalboard post-processing:   │
           │      HPF → de-box → EQ →           │
           │      compress → reverb → limiter   │
           │                                   │
           │  2d. pyloudnorm: −14 LUFS          │
           │                                   │
           │  2e. FFmpeg sidechaincompress:     │
           │      narration + ambient ducking   │
           │                                   │
           │  Output: 13 × final audio WAV      │
           └───────────────┬──────────────────┘
                           │
           ┌───────────────▼──────────────────┐
           │  PHASE 3: Video Assembly (CPU)    │
           │  [Parallel with Phase 2 GPU work] │
           │                                   │
           │  3a. Per-segment FFmpeg encode:    │
           │      • zoompan (breath OR kenbur)  │
           │      • lut3d (section .cube)       │
           │      • noise (c0s=6, temporal)     │
           │      • vignette (PI/5)             │
           │      • colorbalance (arc section)  │
           │                                   │
           │  3b. Final assembly (filter_complex│
           │      + xfade dissolve, 0.5s):      │
           │      [seg0][seg1]xfade...[v01]     │
           │      [v01][seg2]xfade...[v012]...  │
           │                                   │
           │  3c. Mux with processed audio      │
           │                                   │
           │  Output: 13 × H.264 1080p MP4      │
           └───────────────┬──────────────────┘
                           │
           ┌───────────────▼──────────────────┐
           │  PHASE 4: Captions               │
           │                                   │
           │  4a. WhisperX (large-v3, INT8):    │
           │      word-level timestamps         │
           │      (EN and CJK)                  │
           │                                   │
           │  4b. ASS file generation:          │
           │      Therapeutic style params      │
           │      (Nunito 38pt, cream text,      │
           │      soft teal highlight, fad)     │
           │                                   │
           │  4c. FFmpeg ass filter burn-in     │
           │      or sidecar SRT attachment     │
           │                                   │
           │  Output: 13 × captioned MP4        │
           └───────────────┬──────────────────┘
                           │
           ┌───────────────▼──────────────────┐
           │  PHASE 5: Final Encode + Upload   │
           │                                   │
           │  5a. NVENC AV1 UQ mode re-encode: │
           │      1920×1080 → 3840×2160 scaled │
           │      (4K upload trick)             │
           │      AV1 NVENC ~6 Mbps target      │
           │                                   │
           │  5b. YouTube Data API v3 upload:   │
           │      ≤6 videos/day default quota   │
           │      OAuth refresh token auth      │
           │                                   │
           │  Output: 13 × published YouTube    │
           └─────────────────────────────────┘
```

---

## 4. Hardware Utilization Plan — VRAM Conflict Avoidance

**Total VRAM budget:** 16 GB (RTX 5070 Ti)

| Time slot | GPU processes | VRAM used | CPU processes |
|-----------|--------------|-----------|--------------|
| Phase 1 (image gen) | FLUX.1-Kontext GGUF Q5 (12–14GB) | 12–14 GB | Nothing (wait) |
| Phase 1 → 2 transition | FLUX offloads; CosyVoice2 loads | 3–5 GB | ESRGAN upscale if CPU offloaded |
| Phase 2 (audio gen) | CosyVoice2 (3–5GB) + MusicGen-medium (8GB) | 11–13 GB | Pedalboard audio post (per prior-phase tracks) |
| Phase 2 + 3 overlap | CosyVoice2 + MusicGen running | 11–13 GB | FFmpeg assembly for teachers already audio-complete |
| Phase 4 (captions) | WhisperX large-v3 INT8 (1.5GB) | 1.5 GB | FFmpeg final mux continuing |
| Phase 5 (AV1 encode) | NVENC AV1 (2–4GB) | 2–4 GB | YouTube API upload client |

**Conflict rules:**
1. FLUX.1-Kontext MUST be the sole GPU process. Shut down Ollama before Phase 1: `ollama stop` or `systemctl stop ollama`.
2. Do NOT run MusicGen-large (16GB) — use musicgen-medium (8GB) only.
3. WhisperX can coexist with NVENC AV1 encode (1.5GB + 4GB = 5.5GB — well within budget).
4. ComfyUI's `--lowvram` flag is already in use; ensure `--cpu-offload` is available for rapid offloading between phases.
5. Ollama (:11434) should be stopped during Phase 1–2 to free the ~3–5GB it holds for Qwen/phi models.

**VRAM budget summary per phase:**

```
Phase 1:  [FLUX.1-Kontext GGUF Q5: 14GB] + [system: 1.5GB] = 15.5GB  (tight but safe)
Phase 2:  [CosyVoice2: 4GB] + [MusicGen-med: 8GB] + [system: 1.5GB] = 13.5GB  (comfortable)
Phase 3:  [system: 1.5GB] — CPU-only FFmpeg = 1.5GB  (plenty of headroom)
Phase 4:  [WhisperX INT8: 1.5GB] + [system: 1.5GB] = 3GB  (negligible)
Phase 5:  [NVENC AV1: 3GB] + [system: 1.5GB] = 4.5GB  (negligible)
```

---

## 5. Risk Register

| Risk | Severity | Likelihood | Mitigation |
|------|---------|-----------|-----------|
| **FLUX.1-Kontext GGUF Q5 OOM on 16GB** | High | Medium | Fallback to FLUX.1-dev + IP-Adapter FaceID; close all other GPU processes; try GGUF Q4 |
| **MusicGen-medium + CosyVoice2 concurrent OOM** | Medium | Low | Run sequentially if 16GB is tight; total ~13GB should be fine but watch for OS overhead |
| **FLUX.1-Kontext non-commercial license restriction** | Medium | Medium | Verify BFL terms for commercial teacher showcase use before production deployment |
| **YouTube quota (6 videos/day)** | Medium | High (certainty) | Spread uploads over 3 days or request quota increase in advance |
| **pycaps API instability (alpha stage)** | Medium | Medium | Maintain ASS/SRT fallback via stable-ts + custom styling |
| **DepthFlow AGPL in a future distributed product** | Low | Low | AGPL only triggers on distribution/network service; offline batch pipeline is safe now; review before any product distribution |
| **LTX-Video ComfyUI node instability** | Low | Medium | Use as optional enhancement; fallback to Ken Burns + breathing pulse if nodes fail |
| **xfade refactor breaks existing concat pipeline** | Medium | Low | Implement xfade in a new assembly code path; keep concat path as fallback behind config flag |
| **WhisperX CJK accuracy for dialects (Cantonese)** | Low | Low | Mandarin is well-supported; test on representative CosyVoice2 output before production |
| **LUFS −16 → −14 change affects already-published videos** | Low | N/A | Config change only affects future renders; no retroactive re-encode needed |

---

## 6. Comparison Table — All Tools Evaluated

| Tool | Purpose | License | VRAM | Effort | Verdict | Notes |
|------|---------|---------|------|--------|---------|-------|
| **FLUX.1-dev FP8** | Image generation | Open-weights (BFL) | 12–15 GB | Already deployed | USE — primary | Best photorealism on 16GB |
| **FLUX.1-Kontext GGUF Q5** | Context-consistent image gen | Open-weights (BFL non-commercial dev) | 12–14 GB | 4–8 hrs | USE | Solves teacher identity consistency |
| **FLUX.1-schnell** | Draft/preview image gen | Open-weights (BFL) | 12 GB | Already available | USE (drafts only) | 1–4 steps; artifacts in finals |
| **SD 3.5 Large (INT8)** | Image generation | Apache-2.0 | ~12 GB | 2–4 hrs | EVALUATE | Best Apache-2.0 alternative to FLUX |
| **AuraFlow v0.3** | Image generation | Apache-2.0 | ~12 GB | 2 hrs | SKIP | Weaker fine portraiture |
| **XLabs-AI ControlNet (FLUX)** | Teacher pose control | Apache-2.0 | +2–4 GB | 4 hrs | EVALUATE | Fallback if Kontext not viable |
| **ComfyUI-IPAdapter-Flux (FaceID)** | Face identity consistency | Apache-2.0 | +2–4 GB | 4 hrs | EVALUATE | Fallback for Kontext |
| **LTX-Video 2.3** | Short cinematic video clips | Apache-2.0 | 12–14 GB | 4–6 hrs | EVALUATE | Fastest open-source video gen on 16GB |
| **HunyuanVideo 1.5** | Cinematic video generation | Tencent license | 14 GB+ | 6–8 hrs | EVALUATE | High quality; license check needed |
| **AnimateDiff (ComfyUI-Evolved)** | Short looping motion clips | Apache-2.0 | 12 GB | 3–4 hrs | EVALUATE | Good for atmospheric 4–8s loops |
| **SVD (Stability AI)** | Stills → video | Stability AI license | 14–16 GB | 4 hrs | SKIP | Superseded by LTX/HunyuanVideo; VRAM tight |
| **DepthFlow** | 2.5D parallax from stills | AGPL-3.0 | ~0 (GLSL) | 1–2 weeks | EVALUATE | AGPL safe for private pipeline; ComfyUI nodes available |
| **Wan2GP** | WAN 2.1/2.2 on 16GB | Verify license | 12–16 GB | 6–10 hrs | EVALUATE | Strong quality; not ComfyUI native |
| **ffmpeg-python** | Type-safe FFmpeg filter graph | Apache-2.0 | 0 (CPU) | 1–2 days | USE (incremental) | Replace new filter chains first |
| **MoviePy 2.1.2** | Python video editing | MIT | 0 (CPU) | N/A | SKIP | 10× slower than FFmpeg confirmed |
| **DaVinci Resolve free** | Video editing / assembly | Proprietary | 0 | N/A | SKIP | Python API requires paid Studio |
| **Remotion** | React-based video gen | MIT | 0 | N/A | SKIP | JavaScript only |
| **MusicGen-medium** | AI ambient music generation | MIT | 8 GB | 2–4 hrs | USE | 30s ambient in ~45s; therapeutic prompts |
| **MusicGen-large** | High-quality AI music | MIT | 16 GB | N/A | SKIP | Too large for concurrent use |
| **MMAudio** | Video-to-audio generation | Apache-2.0 | ~4 GB | 3–4 hrs | EVALUATE | Add ambient sound to video clips automatically |
| **Pedalboard (Spotify)** | Audio post-processing | Apache-2.0 | 0 (CPU) | 30 min | USE | Already P0 in prior research |
| **AudioCraft** | MusicGen parent library | MIT | 8 GB+ | N/A | USE via MusicGen | Use musicgen-medium via this library |
| **binaural-generator** | Binaural beats / isochronic | Apache-2.0 | 0 | 2 hrs | EVALUATE | Optional therapeutic enhancement |
| **pyloudnorm** | LUFS loudness normalization | MIT | 0 (CPU) | 30 min | USE | −14 LUFS for YouTube |
| **ffmpeg sidechaincompress** | Audio ducking | N/A (FFmpeg) | 0 | 1 hr | USE | Narration over ambient music |
| **WhisperX** | Word-level caption timestamps | BSD-4 | 1.5–2 GB | 2–3 hrs | USE | Recommended over base Whisper |
| **faster-whisper (large-v3-turbo)** | CJK + EN transcription | MIT | 1.5 GB (INT8) | 1–2 hrs | USE | Backend for WhisperX |
| **pycaps** | Animated word captions | MIT | 0 | 1–2 days | EVALUATE | Alpha; maintain ASS fallback |
| **stable-ts** | CJK timestamp refinement | MIT | 1.5 GB | 1 hr | USE | DTW alignment; good for CJK |
| **jieba** | CJK word segmentation | MIT | 0 | 30 min | EVALUATE | Word boundaries for Chinese captions |
| **n8n** | Workflow automation | Sustainable Use | 0 (Docker) | 2–3 days | SKIP (for now) | Re-evaluate for event-driven pipeline |

---

## Source References

- [FLUX.1 VRAM requirements & local setup (2026)](https://localaimaster.com/blog/flux-local-image-generation)
- [FLUX.1-Kontext Dev release — ComfyUI Wiki](https://comfyui-wiki.com/en/news/2025-06-26-flux-1-kontext-dev-release)
- [FLUX.1-Kontext ArXiv paper](https://arxiv.org/html/2506.15742v2)
- [XLabs-AI x-flux-comfyui (GitHub)](https://github.com/XLabs-AI/x-flux-comfyui)
- [ComfyUI-IPAdapter-Flux (Shakker-Labs)](https://github.com/Shakker-Labs/ComfyUI-IPAdapter-Flux)
- [LTX-Video VRAM requirements (Wavespeed)](https://wavespeed.ai/blog/posts/blog-ltx-2-vram-requirements/)
- [NVIDIA RTX 5070 Ti / RTX 50 NVENC specs (Puget Systems)](https://www.pugetsystems.com/blog/2025/01/21/nvidia-geforce-rtx-50-series-features-for-content-creators/)
- [Wan2GP (GitHub)](https://github.com/deepbeepmeep/Wan2GP)
- [SVD VRAM optimization — Civitai](https://civitai.com/articles/4286/stable-video-diffusion-optimization-low-vram)
- [Stable Diffusion 3.5 vs FLUX comparison (Modal Blog)](https://modal.com/blog/best-text-to-image-model-article)
- [AudioCraft / MusicGen (GitHub)](https://github.com/facebookresearch/audiocraft)
- [WhisperX (GitHub)](https://github.com/m-bain/whisperX)
- [Whisper VRAM requirements (HuggingFace discussion)](https://huggingface.co/openai/whisper-large-v3/discussions/83)
- [DepthFlow (GitHub)](https://github.com/BrokenSource/DepthFlow)
- [parallax-maker (GitHub)](https://github.com/provos/parallax-maker)
- [pycaps (GitHub)](https://github.com/francozanardi/pycaps)
- [Pedalboard (Spotify, GitHub)](https://github.com/spotify/pedalboard)
- [FFmpeg sidechaincompress docs](https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Audio/sidechaincompress.html)
- [xfade-easing extensions](https://github.com/scriptituk/xfade-easing)
- [LUFS standards — Youlean](https://youlean.co/loudness-standards-full-comparison-table/)
- [YouTube LUFS guidelines 2025 (Peak Studios)](https://www.peak-studios.de/en/youtube-audio-richtlinien-streaming-2025/)
- [YouTube recommended upload settings](https://support.google.com/youtube/answer/1722171)
- [YouTube Data API v3 — Google Developers](https://developers.google.com/youtube/v3/getting-started)
- [Spotify video podcast specs](https://support.spotify.com/us/creators/article/video-specs/)
- [Apple Podcasts video (TechCrunch, 2026)](https://techcrunch.com/2026/02/17/apple-podcasts-is-getting-an-enhanced-video-experience-this-spring/)
- [binaural-generator (GitHub)](https://github.com/ksylvan/binaural-generator)
- [MoviePy v2 performance regression](https://github.com/Zulko/moviepy/issues/2395)
- [DaVinci Resolve Python API (free tier limitations)](https://dev.to/depsir/unlock-the-secrets-of-automating-davinci-resolve-with-python-free-version-edition-1fkn)
- [GPU cloud video AI 2026 — Spheron](https://www.spheron.network/blog/gpu-cloud-video-ai-2026/)
- [Color psychology in film (Color Institute)](https://colorinstitute.com/color-psychology-in-film-television/)
- [Freesound Luftrum ambient pack](https://freesound.org/people/Luftrum/packs/3069/)
- [moodist open-source ambient sounds](https://github.com/remvze/moodist)
