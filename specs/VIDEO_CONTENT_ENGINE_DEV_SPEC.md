# VIDEO CONTENT ENGINE — Dev Spec v1.0

**Date:** 2026-03-31
**Status:** Dev spec — pending review
**Authority scope:** All video content production across 24 channels, 7 platforms, 12 languages
**Depends on:** `docs/VIDEO_PIPELINE_SPEC.md`, `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md`, `specs/AI_MANGA_PIPELINE_SUMMARY.md`, `config/video/channel_registry.yaml`
**Research basis:** `research/2026-03-30_implicit-therapeutic-visual-media.md`
**Audience:** Pipeline engineers, video producers, platform operations

---

## §1 Purpose & System Overview

### What This Extends

This spec extends two existing systems into a unified video content engine:

1. **VIDEO_PIPELINE_SPEC** (`docs/VIDEO_PIPELINE_SPEC.md`) — the 11-stage metadata-driven pipeline (Script Generator through Distribution Writer) that currently produces therapeutic short-form video from still images + TTS + captions.
2. **Implicit Therapeutic Engine** (`specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md` §10–§11) — camera movement prescriptions, edit rhythm entrainment, soundtrack therapeutic rules, and EI v2 visual-therapeutic scoring.

The Video Content Engine (VCE) adds:
- Six content formats (short, mid, long, motion comic, lofi stream, exercise video)
- 5-layer compositing (extending the current 3-layer FLUX system)
- Animation engine (parallax, Ken Burns, particle, character animation)
- Platform adaptation layer for 7 platforms
- Multi-language pipeline for 12 languages
- Soundtrack generation and therapeutic audio mixing
- Cost model and production scheduling

### Design Principle: Therapeutic-First

Every design decision passes through ITE §2: entertainment-first surface, implicit therapeutic mechanisms in structure. The word "therapy" never appears in any consumer-facing output. Viewers experience compelling video; their nervous systems experience regulation.

### Multi-Platform Output

| Platform | Format | Primary Audience |
|---|---|---|
| YouTube (long) | 16:9, 2–30 min | All 10 personas |
| YouTube Shorts | 9:16, ≤60s | Gen Z, Gen Alpha, Millennial women |
| TikTok | 9:16, 15s–10m | Gen Z, Gen Alpha |
| Instagram Reels | 9:16, ≤90s | Millennial women, Working parents |
| Bilibili | 16:9, 2–30 min | zh-CN speakers |
| Douyin | 9:16, 15s–5m | zh-CN speakers |
| Webtoon (animated) | Vertical scroll | Gen Z, Gen Alpha (manga channels) |

---

## §2 Architecture

### Extended Pipeline (17 Stages)

```
Existing Pipeline (stages 1–11):
  1. Script Generator
  2. Script Preparer
  3. Shot Planner
  4. Asset Resolver
  5. Timeline Builder (FormatAdapter)
  6. CaptionAdapter
  7. Renderer (FFmpeg)
  8. QC / Safety Gates
  9. Provenance Writer
 10. Metadata Writer
 11. Distribution Writer

New Stages (12–17):
 12. Layer Compositor        ← 5-layer build from resolved assets
 13. Animation Engine        ← motion, parallax, character animation
 14. Soundtrack Engine       ← music gen, voice synthesis, audio mixing
 15. Platform Adapter        ← per-platform format, metadata, compliance
 16. Multi-Language Renderer ← 12-language voice + subtitle variants
 17. Analytics Ingestor      ← retention curves → pacing feedback loop
```

### Data Flow

```
Input atoms (SCENE, STORY, HOOK, EXERCISE)
  + manga panels (from AI_MANGA_PIPELINE)
  + audio scripts (from PHOENIX_V4_5_WRITER_SPEC)
        ↓
  Stages 1–6 (existing pipeline: script → shot plan → timeline)
        ↓
  Stage 12: Layer Compositor (5-layer compositing)
        ↓
  Stage 13: Animation Engine (motion applied to layers)
        ↓
  Stage 14: Soundtrack Engine (music + voice + ambient)
        ↓
  Stage 7: Renderer (FFmpeg composite final)
        ↓
  Stage 8: QC Gates (ITE compliance + platform rules)
        ↓
  Stage 15: Platform Adapter (per-platform variants)
        ↓
  Stage 16: Multi-Language Renderer (12 language variants)
        ↓
  Stages 9–11 (provenance, metadata, distribution)
        ↓
  Stage 17: Analytics Ingestor (feedback loop)
```

---

## §3 Content Formats

### Format Specifications

| # | Format | Duration | Resolution | Aspect | FPS | Audio | Platforms | Therapeutic Mechanisms |
|---|--------|----------|-----------|--------|-----|-------|-----------|----------------------|
| 1 | **Therapeutic Short** | 15–60s | 1080x1920 | 9:16 | 30 | Mono/Stereo, AAC 128k | TikTok, YT Shorts, Reels, Douyin | Hook + rapid parasympathetic arc (§10.3 compressed) |
| 2 | **Therapeutic Mid** | 2–8 min | 1920x1080 | 16:9 | 24 | Stereo, AAC 192k | YouTube, Bilibili | Full 5-section arc (hook→build→peak→release→resolve) |
| 3 | **Therapeutic Long** | 15–30 min | 1920x1080 | 16:9 | 24 | Stereo, AAC 256k | YouTube, audiobook companion | Multiple arcs, chapter markers, extended nature sections |
| 4 | **Motion Comic** | 3–10 min | 1920x1080 + 1080x1920 | 16:9 + 9:16 | 24 | Stereo, AAC 192k | YouTube, Webtoon | Panel breath engine (ITE §5) + gutter pauses in timeline |
| 5 | **Lofi Stream** | 1–4 hrs | 1920x1080 | 16:9 | 15 | Stereo, AAC 192k | YouTube Live, Spotify Canvas | Continuous parasympathetic: 66 BPM, pentatonic, fractal BG |
| 6 | **Exercise Video** | 5–15 min | 1080x1920 + 1920x1080 | 9:16 + 16:9 | 30 | Stereo, AAC 192k | YouTube, TikTok | Somatic cues: breathing visualization, 6 BPM target |

### Per-Format Production Cost Estimate

| Format | AI Image Gen | Animation | Music Gen | Voice | Render | Total Est. |
|--------|-------------|-----------|-----------|-------|--------|-----------|
| Therapeutic Short | $0.10 (3–5 images) | $0.05 | $0.15 | $0.10 | $0.02 | **$0.42** |
| Therapeutic Mid | $0.40 (10–20 images) | $0.20 | $0.30 | $0.40 | $0.05 | **$1.35** |
| Therapeutic Long | $1.20 (40–80 images) | $0.60 | $0.60 | $1.50 | $0.15 | **$4.05** |
| Motion Comic | $0.00 (manga panels) | $1.50 | $0.30 | $0.40 | $0.10 | **$2.30** |
| Lofi Stream | $0.80 (20–30 loop images) | $0.30 | $2.00 | $0.00 | $0.20 | **$3.30** |
| Exercise Video | $0.30 (8–15 images) | $0.40 | $0.30 | $0.80 | $0.08 | **$1.88** |

---

## §4 Layered Image Building System (Extended)

### Current: 3-Layer FLUX

The existing system (`docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md`) generates a single composited image via FLUX with three conceptual parts: foreground subject, background gradient, overall lighting.

### Extended: 5-Layer Compositing

| Layer | Name | Source | Motion Eligible | Z-Order |
|-------|------|--------|----------------|---------|
| L1 | **Background plate** | FLUX gen or image bank. Fractal patterns FD 1.3–1.5 for therapeutic. | Slow pan (≤30px/sec per `motion_policy.yaml`) | 0 (farthest) |
| L2 | **Midground elements** | FLUX gen. Nature objects, atmosphere, environment detail. | Drift (0.5–1px/sec lateral) | 1 |
| L3 | **Character/subject** | Manga character sheets OR FLUX gen. No faces by default. | Ken Burns (≤2%/sec zoom per `motion_policy.yaml`) | 2 |
| L4 | **Foreground elements** | Particle systems, bokeh, depth blur, atmospheric overlay. | Continuous particle motion, parallax (2x BG speed) | 3 |
| L5 | **Overlay** | Color grade LUT (`config/video/color_grade_presets.yaml`), vignette, therapeutic grain (σ≤3). | None (static post-process) | 4 (nearest) |

### Layer Compositing Rules

1. **Parallax ratio:** L1 moves at 1x base speed, L2 at 1.3x, L3 at 1.6x, L4 at 2x. Creates depth.
2. **Alpha blending:** L4 foreground at 30–60% opacity. L5 overlay at 15–25% opacity.
3. **Caption safe:** Captions render between L4 and L5. Caption bar from `config/video/caption_policies.yaml`.
4. **Per-format layer count:** Shorts may use 3 layers (L1+L3+L5) for render speed. Long-form uses all 5.

### Manga Panel → Video Layer Conversion

| Manga Component | Video Layer | Conversion Method |
|----------------|-------------|-------------------|
| Panel background | L1 (Background plate) | Upscale to 1920x1080, extend edges with outpainting |
| Background objects | L2 (Midground) | Segment via SAM/RMBG, place on transparent layer |
| Character art | L3 (Character/subject) | Extract from character sheet; match pose to scene |
| Speed lines, SFX | L4 (Foreground) | Convert to particle/overlay animation |
| Panel border | Transition trigger | Panel edge → transition type (cut, iris, page turn) |

---

## §5 Animation Engine

### Motion Types

| Motion Type | Parameters | Therapeutic Use | Max Speed | FPS |
|------------|-----------|-----------------|-----------|-----|
| **Parallax scroll** | direction, layer_speeds[] | Depth perception, immersion | 30px/sec (L1) | 24 |
| **Ken Burns** | start_rect, end_rect, easing | Slow reveal, contemplation | 2%/sec zoom | 24 |
| **Particle system** | count, speed, size, opacity, drift | Atmosphere (rain, dust, fireflies) | 60px/sec | 30 |
| **Breathing pulse** | scale_min, scale_max, bpm | Respiratory entrainment (ITE §10.2) | 6 cycles/min | 30 |
| **Water/nature loop** | loop_duration, blend_frames | Fractal regulation (FD 1.3–1.5) | seamless loop | 24 |
| **Text reveal** | chars_per_sec, fade_in_ms | Caption pacing, reading rhythm | 15 chars/sec | 30 |
| **Camera pan** | angle, speed, easing | Scene exploration | 5°/sec (ITE §10.1) | 24 |
| **Scale drift** | amplitude, period | Subtle breathing feel on elements | ±3% over 10s | 24 |

### AI-Assisted Animation

| Tool | Use Case | Input | Output | Cost/sec |
|------|----------|-------|--------|----------|
| Runway Gen-3 | Style-consistent motion from stills | Single FLUX image + motion prompt | 4s video clip | $0.05 |
| Kling 1.6 | Long-duration motion, camera moves | Image + text prompt | 5–10s clip | $0.03 |
| Live2D Cubism | Character idle animation (blink, breathe, mouth) | Character sheet + rigging mesh | Real-time | $0.00 (pre-rigged) |

### Character Animation (Live2D/Spine)

For motion comic and exercise video formats, characters use pre-rigged Live2D models:

| Animation | Trigger | Parameters |
|-----------|---------|-----------|
| Idle breathing | Always active | chest_amplitude: 3%, period: 10s (6 BPM) |
| Blink | Random interval | interval: 3–7s, duration: 150ms |
| Mouth sync | TTS audio | viseme mapping from ElevenLabs phoneme stream |
| Emotion shift | Script segment emotion tag | blend shape transition over 500ms |

### Transition Library

| Transition | Duration | Use Case | Therapeutic Effect |
|-----------|----------|----------|-------------------|
| Crossfade | 500–1500ms | Default between scenes | Smooth, calming |
| Cut | 0ms | High-energy, hook sections | Alerting, engagement |
| Dip-to-black | 1000–2000ms | Section/chapter boundary | Processing pause (ITE §8 gutter analog) |
| Iris wipe | 800ms | Motion comic panel focus | Genre nostalgia |
| Page turn | 600ms | Motion comic page boundary | Reader metaphor |
| Panel slide | 400ms | Motion comic panel-to-panel | Sequential flow |
| Zoom dissolve | 1000ms | Dream/memory sequences | Dissociative, contemplative |

---

## §6 Therapeutic Video Engine Integration

This section maps ITE §10–§11 prescriptions to VCE implementation.

### §6.1 Camera Movement → Animation System Mapping

| ITE §10.1 Camera Technique | VCE Animation Implementation |
|---|---|
| Slow steady pan (≤5°/sec) | `camera_pan` motion type, speed=5, easing=ease_in_out |
| Slow tracking forward | `ken_burns` zoom_in at 1.5%/sec |
| Static wide shot (≥5s hold) | No motion. `static` type. Duration ≥5000ms. |
| Slow dolly out | `ken_burns` zoom_out at 1%/sec |
| Handheld sway | `scale_drift` amplitude=2%, period=2s + random offset |
| Rapid cuts | Transition type=`cut`, segment duration 1.5–2.5s |

### §6.2 Edit Rhythm Entrainment Implementation

The Timeline Builder applies cut rhythm per ITE §10.2, driven by arc position:

| Arc Section (ITE §10.3) | % of Video | Cut Interval | BPM Equiv | Motion Budget |
|---|---|---|---|---|
| HOOK | 0–15% | 2–4s | 15–30 | 50% motion shots |
| BUILD | 15–55% | 4–6s | 10–15 | 30% motion shots |
| PEAK | 55–70% | 8–12s | 5–7.5 | 15% motion shots |
| RELEASE | 70–85% | 8–15s | 4–7.5 | 10% motion shots (slow pan only) |
| RESOLVE | 85–100% | ≥15s unbroken | <4 | 0% (static + slow dolly-out only) |

Config: `config/video/pacing_by_content_type.yaml` extended with `arc_section_pacing` key.

### §6.3 Color Temperature Arc

Applied as FFmpeg `colorbalance` filter, shifting across the video timeline:

| Arc Section | Color Temp Target | FFmpeg Implementation |
|---|---|---|
| HOOK | Warm (3200K–4000K) | `colorbalance=rs=0.1:gs=0.0:bs=-0.1` |
| BUILD | Neutral (4500K–5500K) | `colorbalance=rs=0.0:gs=0.0:bs=0.0` |
| PEAK | Cool (5500K–6500K) | `colorbalance=rs=-0.05:gs=0.0:bs=0.05` |
| RELEASE | Cool-warm blend (5000K–5500K) | `colorbalance=rs=0.02:gs=0.02:bs=0.0` |
| RESOLVE | Warm glow (3500K–4500K) | `colorbalance=rs=0.08:gs=0.03:bs=-0.05` |

Keyframes interpolated linearly between section boundaries. One grade preset per video from `config/video/color_grade_presets.yaml` is applied first; temperature arc is additive.

### §6.4 Fractal Regulation Layer

Backgrounds in RELEASE and RESOLVE sections must contain fractal imagery per ITE §7:

| Section | FD Target | Source Category (ITE §7.3) | Min Coverage |
|---|---|---|---|
| HOOK | 1.4–1.6 | Any | Optional |
| BUILD | Any | Any | Optional |
| PEAK | 1.3–1.5 | Arboreal, Aquatic, Atmospheric | ≥30% BG area |
| RELEASE | 1.3–1.5 | Arboreal, Aquatic, Atmospheric | ≥50% BG area |
| RESOLVE | 1.2–1.4 | Atmospheric, Aquatic | ≥70% BG area |

### §6.5 Breathing Visualization

For exercise videos and select therapeutic mid/long content, a subtle scale pulse on visual elements entrains viewer breathing:

- **Target:** 6 BPM (10s cycle: 4s inhale, 2s hold, 4s exhale)
- **Implementation:** `breathing_pulse` motion type on L3 (character) or L2 (midground element)
- **Amplitude:** ±2–4% scale (subtle; viewer does not consciously notice)
- **Onset:** Begins in BUILD section, strongest in PEAK and RELEASE
- **Exercise video override:** Amplitude ±5–8%, visible breathing guide overlay on L4

### §6.6 Nature Footage Integration

Per ITE §10.4, nature footage minimums by format:

| Format | Min Nature Duration | Placement |
|--------|-------------------|-----------|
| Therapeutic Short (15–60s) | 5s | Final 15% |
| Therapeutic Mid (2–8 min) | 15–45s | Release + Resolve |
| Therapeutic Long (15–30 min) | 90s+ | ≥3 distributed + extended Resolve |
| Motion Comic | 10s per chapter | Chapter endings |
| Lofi Stream | Continuous | Fractal nature backgrounds throughout |
| Exercise Video | 30s | Resolve section, between exercise sets |

### §6.7 Strategic Silence

Per ITE §11.4, silence insertion in audio track:

| Format | Silence Rule |
|--------|-------------|
| Short (≤60s) | Final 2–3s fade to silence |
| Mid (2–8 min) | ≥1 silence period 5–10s in Release section |
| Long (15–30 min) | ≥1 silence period 8–15s per 5 min of content |
| Lofi Stream | 5s silence every 20–30 min (natural break) |
| Exercise Video | 3–5s silence between exercise segments |

---

## §7 Soundtrack Engine

### §7.1 Music Generation

| Component | API | Parameters | Cost |
|-----------|-----|-----------|------|
| Pentatonic therapeutic music | Suno v4 API | Tempo 60–72 BPM (calming) / 80–100 BPM (hook), pentatonic scale, instrumental only, 10s phrase length | $0.05/30s |
| Tension/build music | Suno v4 API | Tempo 72–90 BPM, minor key permitted, strings/piano | $0.05/30s |
| Lofi ambient loops | Suno v4 API | 66 BPM, lo-fi hip-hop/ambient, 2-min loops | $0.05/30s |
| Nature ambience | Sound library (pre-licensed) | Rain, forest, ocean, wind. FD-matched to visual. | $0.00 (library) |

Config: `config/video/music_policy.yaml` maps `arc_to_mood` and `emotional_band_overrides`.

### §7.2 Voice Synthesis

| Feature | Provider | Spec |
|---------|----------|------|
| Narration (12 languages) | ElevenLabs Turbo v2.5 | Per-channel voice from `channel_registry.yaml → tts_voice_id` |
| Phoneme stream (mouth sync) | ElevenLabs | Viseme timestamps for Live2D character animation |
| Multilingual cloning | ElevenLabs | Clone base voice → 12 language variants per channel |
| Pronunciation lexicon | Custom | Per-topic term pronunciation overrides |

**Supported languages:** en, zh-CN, zh-TW, zh-HK, ja, ko, es, fr, de, hu, pt-BR, id

### §7.3 Audio Mixing Spec

| Track | Level | Pan | Notes |
|-------|-------|-----|-------|
| Primary narration (TTS) | -6 dB | Center | Ducking: music drops -6 dB when narration active |
| Music bed | -12 dB (under narration), -8 dB (solo) | Stereo | Tempo arc per ITE §11.2 |
| Nature ambience | -18 dB | Wide stereo | Continuous under narration + music |
| Therapeutic sublayer (isochronic) | ≤-18 dB | Center | 6–10 Hz per ITE §11.3. Optional, config-gated. |
| Therapeutic sublayer (sub-bass) | ≤-18 dB | Center | 30–40 Hz sustained. Optional, config-gated. |

**Master output:** -1 dBTP (true peak), -14 LUFS (YouTube/Spotify loudness target).

### §7.4 Dynamic Audio Automation

Volume and EQ automation follows the visual edit rhythm:

| Visual Event | Audio Response | Latency |
|---|---|---|
| Scene cut | Music micro-swell (+2 dB, 200ms) | 0ms (pre-calculated) |
| Nature footage onset | Ambience fade up to -12 dB over 2s | 0ms |
| Silence insertion point | All tracks fade to -40 dB over 1s | 0ms |
| Breathing pulse peak | Sub-bass +3 dB on exhale phase | Synced to animation |
| Caption reveal | Narration onset, music duck | 200ms pre-duck |

---

## §8 Platform Adaptation Layer

### §8.1 Platform Format Specs

| Platform | Resolution | Aspect | Max Duration | Codec | Container | Captions |
|----------|-----------|--------|-------------|-------|-----------|---------|
| YouTube | 1920x1080 | 16:9 | 12 hrs | H.264 High, CRF 23 | MP4 | SRT sidecar + chapters |
| YouTube Shorts | 1080x1920 | 9:16 | 60s | H.264 High, CRF 23 | MP4 | Burnt-in (drawtext) |
| TikTok | 1080x1920 | 9:16 | 10 min | H.264 Main, CRF 21 | MP4 | Burnt-in + platform auto-captions |
| Instagram Reels | 1080x1920 | 9:16 | 90s | H.264 Main, CRF 21 | MP4 | Burnt-in |
| Bilibili | 1920x1080 | 16:9 | 4 hrs | H.264 High, CRF 20 | MP4 | zh-CN SRT required + danmaku-safe zone |
| Douyin | 1080x1920 | 9:16 | 5 min | H.264 Main, CRF 21 | MP4 | zh-CN burnt-in |
| Webtoon | 800xN (vertical) | Variable | N/A (scroll) | WebP sequence | ZIP | In-panel text |

### §8.2 Thumbnail Generator

| Platform | Thumbnail Spec | Variants per Video |
|----------|---------------|-------------------|
| YouTube | 1280x720, JPG, ≤2MB. Text overlay: title_template from `channel_registry.yaml`. Hook band palette. | 3 (A/B/C test) |
| TikTok | First-frame capture + text overlay | 1 |
| Bilibili | 1280x720, JPG, zh-CN text overlay | 2 |

Thumbnail generation uses hook-band palette from `config/video/brand_style_tokens.yaml → bands → hook`.

### §8.3 Metadata Generator

Per platform, auto-generate from distribution manifest:

| Field | Source | Platform Variation |
|-------|--------|-------------------|
| Title | `channel_registry.yaml → title_templates → {tmpl_id}` | Platform char limits (YT: 100, TT: 150) |
| Description | Atom STORY text + topic tags + CTA | YT: chapters + links. TT: hashtags. Bilibili: zh-CN. |
| Tags | Topic + persona + emotional_band + locale | YT: 15 tags max. TT: 5 hashtags. |
| Hashtags | Trending + evergreen per platform API | TT/Douyin: 3–5. IG: 20–30. |

### §8.4 Platform Compliance Rules

| Platform | Rule | Implementation |
|----------|------|---------------|
| TikTok | Mental health content restrictions | No suicide/self-harm imagery. No diagnostic claims. QC gate BLOCKER. |
| Bilibili | Content review (shenhe) | zh-CN subtitles mandatory. No sensitive political topics. Pre-review queue. |
| Douyin | China-specific compliance | Separate API (not TikTok). ICP requirements. Content review lag 24–72h. |
| YouTube | Community guidelines | No misleading health claims. Therapeutic mechanisms are structural, never claimed. |
| Webtoon | Format guidelines | Vertical scroll only. Panel-by-panel progressive load. Max 100 panels/episode. |

### §8.5 Upload Scheduling

Per `channel_registry.yaml → upload_window_offset_hours` and `daily_upload_cap`:
- No two channels upload within the same 2-hour window on the same platform.
- Max 3 uploads per channel per day at launch (§15.5 rule 6).
- Stagger across timezones: schedule by persona's peak engagement hours.

---

## §9 Multi-Language Pipeline

### §9.1 Voice Synthesis per Language

| Language Code | Language | Voice Provider | Voice Count (24 channels) | Notes |
|---|---|---|---|---|
| en | English | ElevenLabs | 24 (unique per channel) | Base voices from `channel_registry.yaml` |
| zh-CN | Mandarin (Simplified) | ElevenLabs | 6 (Bilibili/Douyin channels) | Priority for Bilibili |
| zh-TW | Mandarin (Traditional) | ElevenLabs | 3 | Taiwan market |
| zh-HK | Cantonese | ElevenLabs | 2 | Hong Kong market |
| ja | Japanese | ElevenLabs | 4 | Manga/anime channel alignment |
| ko | Korean | ElevenLabs | 3 | Webtoon alignment |
| es | Spanish | ElevenLabs | 4 | LATAM + Spain |
| fr | French | ElevenLabs | 2 | France + West Africa |
| de | German | ElevenLabs | 2 | DACH region |
| hu | Hungarian | ElevenLabs | 1 | Niche market test |
| pt-BR | Brazilian Portuguese | ElevenLabs | 3 | Brazil market |
| id | Indonesian | ElevenLabs | 2 | SEA market |

### §9.2 Subtitle Generation

| Subtitle Type | Use Case | Format |
|---|---|---|
| SRT sidecar | YouTube, Bilibili | `.srt` per language |
| Burnt-in (drawtext) | TikTok, Douyin, Reels, Shorts | FFmpeg `drawtext` with per-language font |
| ASS/SSA | Bilibili (styled) | `.ass` with danmaku-safe positioning |
| In-panel | Webtoon | Rendered into panel image |

Font selection per language: CJK → Noto Sans CJK. Latin → Inter. Arabic → Noto Sans Arabic.

### §9.3 Cultural Adaptation of Visual Metaphors

| Locale | Metaphor Adaptation | Config |
|--------|-------------------|--------|
| zh-CN/zh-TW | Replace Western nature (oak trees) with East Asian (bamboo, plum blossom, mountain pine) | `config/video/visual_metaphor_library.yaml → locale_overrides` |
| ja | Seasonal references (sakura=spring, momiji=autumn) per topic emotional arc | Align with existing iyashikei style channels |
| ko | Korean aesthetics (hanok architecture, Korean garden elements) | New metaphor entries |
| es/pt-BR | Tropical/warm climate nature (palm, ocean, sun) for LATAM | Override temperate defaults |
| id | SEA tropical nature (rice terrace, rainforest, ocean) | New metaphor entries |

### §9.4 Music Selection per Locale

| Locale Group | Instrument Additions (over pentatonic base) | Source |
|---|---|---|
| en (default) | Piano, acoustic guitar, ambient synth | Suno generation |
| zh-CN/zh-TW/zh-HK | Guzheng, erhu, dizi, pipa | Suno + library |
| ja | Koto, shakuhachi, shamisen | Suno + library |
| ko | Gayageum, daegeum | Suno + library |
| es/pt-BR | Nylon guitar, pan flute, cajón (subtle) | Suno generation |
| id | Gamelan (soft), angklung | Library |

Pentatonic scale is universal (ITE §11.1). Locale instruments are additive, not replacements.

---

## §10 Production Pipeline (Technical)

### §10.1 Batch Processing Targets

| Format | Daily Target (Phase 1) | Daily Target (Phase 2) | Parallel Workers |
|--------|----------------------|----------------------|-----------------|
| Therapeutic Short | 500 | 5,000 | 20 |
| Therapeutic Mid | 20 | 100 | 5 |
| Therapeutic Long | 5 | 20 | 3 |
| Motion Comic | 3 | 10 | 2 |
| Lofi Stream | 1 | 3 | 1 |
| Exercise Video | 5 | 20 | 3 |

### §10.2 Render Farm Specs

| Resource | Spec | Provider |
|----------|------|----------|
| GPU (render) | NVIDIA A10G (24GB VRAM) or equivalent | AWS g5.xlarge / RunPod |
| GPU (AI gen) | NVIDIA A100 (40GB VRAM) for FLUX batch | AWS p4d / RunPod |
| CPU (FFmpeg) | 8-core, 32GB RAM per worker | AWS c6i.2xlarge |
| Render time (short) | ~30s per video (FFmpeg composite) | CPU worker |
| Render time (mid) | ~3 min per video | GPU worker (animation) + CPU (FFmpeg) |
| Render time (long) | ~15 min per video | GPU + CPU |

### §10.3 Storage & CDN

| Tier | Storage | Retention | Purpose |
|------|---------|-----------|---------|
| Hot (render) | Local NVMe | 48 hours | Active render pipeline |
| Warm (staging) | Cloudflare R2 | 30 days | QC review + distribution staging |
| Cold (archive) | Backblaze B2 | Indefinite | Master renders + provenance |
| CDN (delivery) | Cloudflare R2 + CDN | Per distribution | Platform upload staging |
| Image bank | Cloudflare R2 | Indefinite | 9,600 images (24 channels x 400) |

### §10.4 Version Control for Video Assets

- Image bank assets: immutable, versioned by `style_version` (from `image_bank_asset_v1.schema.json`)
- Rendered videos: `video_id` + `render_version` in provenance
- Config changes: git-tracked in `config/video/`
- Soundtrack stems: stored alongside video provenance, referenced by `audio_asset_id`

### §10.5 A/B Testing Framework

| Test Variable | Implementation | Measurement |
|---|---|---|
| Thumbnail variant (3 per video) | Upload 3 thumbnails, rotate via platform API (YT) | CTR at 24h, 72h |
| Hook type | `hook_type` in distribution manifest telemetry | Retention at 3s, 15s |
| Cut rhythm (fast vs standard) | `pacing_variant` field in provenance | Average view duration |
| Music mood | `music_mood` field in provenance | Completion rate |
| Color grade | `color_grade_preset` in provenance | Like/save ratio |

### §10.6 Analytics Feedback Loop

```
Platform analytics (YT Analytics API, TT Analytics) → video_performance_v1 schema
  → Stage 17: Analytics Ingestor
    → Retention curve analysis (drop-off points → pacing adjustment)
    → Hook effectiveness ranking (CTR by hook_type)
    → Completion rate by format/topic/persona
    → Feed back into Shot Planner heuristics and pacing config
```

---

## §11 QC Gates

Extends existing QC gate pattern from `docs/VIDEO_PIPELINE_SPEC.md` §12 and manga pipeline `specs/AI_MANGA_PIPELINE_SUMMARY.md`.

### BLOCKER Gates (must pass before publish)

| Gate ID | Check | Applies To |
|---------|-------|-----------|
| VCE-B01 | Video duration within format range (§3) | All formats |
| VCE-B02 | Resolution matches platform target (§8.1) | All |
| VCE-B03 | Audio present and ≥-20 LUFS | All |
| VCE-B04 | No video ends on high-arousal pacing (ITE §10.3 final rule) | All ≥60s |
| VCE-B05 | No lyrics in calming/resolution sections (ITE §11.1) | All with music |
| VCE-B06 | Platform compliance rules pass (§8.4) | Per platform |
| VCE-B07 | ITE_score ≥ 0.50 (ITE §12.3) | All therapeutic content |
| VCE-B08 | vt_stealth ≥ 0.50 — no explicit therapy language | All |
| VCE-B09 | Cross-channel asset isolation — 0 shared assets (`cross_video_dedup.yaml → cross_channel`) | All |
| VCE-B10 | TTS voice unique per channel (no voice_id collision) | All |

### WARN Gates (logged, human review queue)

| Gate ID | Check | Applies To |
|---------|-------|-----------|
| VCE-W01 | Motion budget exceeds 25% overall (should be 70–80% static per `motion_policy.yaml`) | All |
| VCE-W02 | ITE_score < 0.70 (below target, above pass) | All therapeutic |
| VCE-W03 | Caption truncated >50% of original text (per `caption_policies.yaml`) | All with captions |
| VCE-W04 | Nature footage below minimum for format (§6.6) | All ≥60s |
| VCE-W05 | Silence duration below minimum for format (§6.7) | All ≥60s |
| VCE-W06 | Music tempo exceeds 78 BPM in calming section (ITE §11.1) | All with music |
| VCE-W07 | Consecutive motion shots (violates `no_consecutive_motion` in `motion_policy.yaml`) | All |

### INFO Gates (telemetry only)

| Gate ID | Check | Logged Field |
|---------|-------|-------------|
| VCE-I01 | Fractal dimension of background images | `fractal_fd_avg` |
| VCE-I02 | Color temperature arc slope | `color_temp_arc_slope` |
| VCE-I03 | Edit rhythm BPM per section | `cut_bpm_by_section` |
| VCE-I04 | Layers used per video | `layer_count` |
| VCE-I05 | AI generation cost per video | `ai_cost_usd` |

---

## §12 EI v2 Integration

### §12.1 Video-Specific Scoring

EI v2 visual-therapeutic dimensions from ITE §12 apply to all video content. Additional video-specific inputs:

| EI v2 Dimension | Video-Specific Scoring Inputs |
|---|---|
| `vt_parasympathetic` | Edit rhythm BPM in resolve section, nature footage duration, color temp in final 15% |
| `vt_processing` | Transition duration (longer = more processing space), silence placement count |
| `vt_somatic` | Breathing pulse amplitude and consistency, soundtrack tempo arc compliance |
| `vt_stealth` | Scan all captions, titles, descriptions for forbidden terms. Scan TTS transcript. |

### §12.2 Therapeutic Value Threshold for Publish

| ITE_score Range | Action |
|---|---|
| ≥ 0.70 | Auto-publish eligible (still requires BLOCKER gates pass) |
| 0.50–0.69 | Human review queue. May publish with approval. |
| < 0.50 | BLOCKER. Do not publish. Return to Shot Planner for re-planning. |

### §12.3 Engagement Scoring from Platform Feedback

| Metric | Source | Weight in Engagement Score |
|--------|--------|--------------------------|
| Completion rate | YT/TT/Bilibili analytics | 0.35 |
| Like ratio | Platform API | 0.20 |
| Save/bookmark ratio | Platform API | 0.20 |
| Comment sentiment | NLP on comments | 0.15 |
| Share count (normalized) | Platform API | 0.10 |

**Combined score:** `content_score = (ITE_score × 0.5) + (engagement_score × 0.5)`. Used for content planning prioritization, not publish gating.

---

## §13 Cost Model

### §13.1 Per-Video Cost Breakdown

| Cost Component | Short ($) | Mid ($) | Long ($) | Motion Comic ($) | Lofi ($) | Exercise ($) |
|---|---|---|---|---|---|---|
| FLUX image generation | 0.10 | 0.40 | 1.20 | 0.00 | 0.80 | 0.30 |
| Runway/Kling animation | 0.05 | 0.20 | 0.60 | 1.50 | 0.30 | 0.40 |
| ElevenLabs TTS | 0.10 | 0.40 | 1.50 | 0.40 | 0.00 | 0.80 |
| Suno music generation | 0.15 | 0.30 | 0.60 | 0.30 | 2.00 | 0.30 |
| FFmpeg render (compute) | 0.02 | 0.05 | 0.15 | 0.10 | 0.20 | 0.08 |
| **Subtotal (1 language)** | **0.42** | **1.35** | **4.05** | **2.30** | **3.30** | **1.88** |
| Per additional language | +0.15 | +0.50 | +1.60 | +0.50 | +0.00 | +0.85 |

### §13.2 Daily Batch Cost (Phase 1)

| Format | Daily Count | Unit Cost | Daily Cost |
|--------|-----------|-----------|-----------|
| Therapeutic Short | 500 | $0.42 | $210 |
| Therapeutic Mid | 20 | $1.35 | $27 |
| Therapeutic Long | 5 | $4.05 | $20 |
| Motion Comic | 3 | $2.30 | $7 |
| Lofi Stream | 1 | $3.30 | $3 |
| Exercise Video | 5 | $1.88 | $9 |
| **Daily total (en only)** | **534** | — | **$276** |
| Multi-language overhead (4 priority langs) | — | — | +$135 |
| **Daily total (5 languages)** | — | — | **$411** |

### §13.3 Infrastructure Costs (Monthly)

| Resource | Spec | Monthly Cost |
|----------|------|-------------|
| GPU render farm (5x g5.xlarge) | On-demand, 12h/day | $2,700 |
| GPU AI gen (2x p4d.xlarge) | Spot, 8h/day | $3,200 |
| CPU workers (10x c6i.2xlarge) | On-demand, 12h/day | $1,800 |
| Cloudflare R2 (10TB) | Storage + egress | $150 |
| Backblaze B2 (50TB archive) | Storage | $250 |
| ElevenLabs (Pro plan x2) | 2M chars/month | $198 |
| Suno (Pro plan) | API access | $96 |
| **Monthly infrastructure** | — | **$8,394** |

---

## §14 Acceptance Criteria

### Phase 1 — MVP (end of Q2 2026)

| Criterion | Measurement |
|-----------|-------------|
| Therapeutic Short pipeline operational | 100 shorts/day, single language (en), 3 channels |
| 5-layer compositing working | Layer compositor produces valid FFmpeg filter chain |
| Parallax + Ken Burns animation | 2 motion types applied per `motion_policy.yaml` |
| TTS narration integrated | ElevenLabs TTS in render pipeline, 3 voices |
| ITE compliance scoring | VCE-B04, VCE-B07, VCE-B08 gates operational |
| YouTube + TikTok upload | Platform adapter produces valid format + metadata |
| QC gates pass rate ≥90% | BLOCKER gates automated in CI |

### Phase 2 — Full (end of Q4 2026)

| Criterion | Measurement |
|-----------|-------------|
| All 6 formats operational | Each format rendering at daily target (§10.1 Phase 2) |
| 24 channels active | All channels from `channel_registry.yaml` producing content |
| 12 languages | Voice + subtitles for all 12 languages |
| 7 platforms | All platform adapters operational (§8.1) |
| Motion Comic from manga panels | Manga → 5-layer → animated video pipeline end-to-end |
| Live2D character animation | Mouth sync + idle animation in motion comic + exercise video |
| Analytics feedback loop | Retention curve data feeding pacing config adjustments |
| Daily batch: 5,000 shorts + 150 long-form | Render farm scaled to Phase 2 targets |
| ITE_score average ≥0.70 | Across all published content |
| A/B test framework | Thumbnail + hook A/B tests running, results feeding content planning |

---

## §15 Timeline

### Q2 2026 (Apr–Jun): Foundation

| Week | Milestone |
|------|-----------|
| W1–2 | Layer Compositor (Stage 12): 5-layer FFmpeg filter chain from image bank assets |
| W3–4 | Animation Engine (Stage 13): parallax + Ken Burns on composited layers |
| W5–6 | Soundtrack Engine (Stage 14): Suno API integration, ElevenLabs TTS, audio mixing |
| W7–8 | Platform Adapter (Stage 15): YouTube + TikTok format + metadata generation |
| W9–10 | QC gates (§11) BLOCKER + WARN gates automated |
| W11–12 | Phase 1 MVP launch: 100 shorts/day, 3 channels, YouTube + TikTok |

### Q3 2026 (Jul–Sep): Scale + Formats

| Week | Milestone |
|------|-----------|
| W1–3 | Motion Comic pipeline: manga panel → layer conversion → animated video |
| W4–5 | Live2D character rigging + mouth sync integration |
| W6–7 | Therapeutic Mid + Long format pipelines |
| W8–9 | Lofi Stream generator (loop engine, continuous render) |
| W10–11 | Exercise Video format (breathing visualization, somatic cue overlay) |
| W12 | Scale to 500 shorts/day + 50 mid/long per day, 12 channels |

### Q4 2026 (Oct–Dec): Multi-Language + Full Scale

| Week | Milestone |
|------|-----------|
| W1–3 | Multi-Language Renderer (Stage 16): 12 languages, voice cloning, subtitle pipeline |
| W4–5 | Bilibili + Douyin + Webtoon platform adapters |
| W6–7 | Analytics Ingestor (Stage 17): retention curve feedback loop |
| W8–9 | A/B testing framework: thumbnail + hook + pacing variants |
| W10–11 | Scale to Phase 2 targets: 5,000 shorts + 150 long-form daily, 24 channels |
| W12 | Full system audit, ITE compliance review, Phase 2 acceptance sign-off |

---

## References

| Document | Path | Relevance |
|----------|------|-----------|
| Video Pipeline Spec | `docs/VIDEO_PIPELINE_SPEC.md` | Base 11-stage pipeline this extends |
| Video Image Master Prompt Spec | `docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md` | FLUX 3-layer image generation |
| Implicit Therapeutic Engine | `specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md` | §10–§11 video/soundtrack therapeutic rules, §12 EI v2 |
| AI Manga Pipeline | `specs/AI_MANGA_PIPELINE_SUMMARY.md` | Manga panel source for Motion Comic format |
| Therapeutic Visual Media Research | `research/2026-03-30_implicit-therapeutic-visual-media.md` | Evidence base for therapeutic mechanisms |
| Channel Registry | `config/video/channel_registry.yaml` | 24 channels, styles, voices, upload windows |
| Image Prompt Templates | `config/video/image_prompt_templates.yaml` | Per-style FLUX prompt templates |
| Brand Style Tokens | `config/video/brand_style_tokens.yaml` | Color bands, palettes, never_rules |
| Motion Policy | `config/video/motion_policy.yaml` | 70–80% static, speed limits |
| Music Policy | `config/video/music_policy.yaml` | Arc-to-mood mapping |
| Pacing by Content Type | `config/video/pacing_by_content_type.yaml` | Duration/hook timing rules |
| Color Grade Presets | `config/video/color_grade_presets.yaml` | Per-video EQ presets |
| Caption Policies | `config/video/caption_policies.yaml` | Char limits, truncation rules |
| Cross-Video Dedup | `config/video/cross_video_dedup.yaml` | Asset reuse caps, publishing windows |
