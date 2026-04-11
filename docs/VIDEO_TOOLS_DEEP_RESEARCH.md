# Video Pipeline Tools Deep Research

**Agent:** Pearl_Research
**Project:** proj_state_convergence_20260328
**Subsystem:** video_pipeline
**Date:** 2026-04-11
**Scope:** RESEARCH ONLY — no installs, no code changes

---

## Executive Summary

### Top 3 Tools to Adopt Immediately

1. **ffmpeg-python** (kkroening) — Replace raw subprocess f-string filter chains with a typed Python API. 11k+ stars, Apache-2.0, widely used in production. Your zoompan + lut3d + noise + vignette + xfade filter chains become composable, inspectable Python objects instead of fragile string concatenation. Trivial-to-moderate integration. **P0.**

2. **Pedalboard** (Spotify) — Add ambient reverb to CosyVoice2 narration audio in ~5 lines of Python before FFmpeg assembly. Actively maintained (PyCon 2025 talk), 300× faster than other Python audio libs, supports VST3/AU plugins. Therapeutic effect: spatial warmth, naturalizes dry TTS. **P0.**

3. **pycaps** (francozanardi) — Word-level animated captions using Whisper timestamps + CSS highlight-as-spoken. MIT license, Python 3.10–3.12. Matches the Descript-style caption spec. **P1.**

### Top 3 Effects to Add to the Pipeline

1. **Breathing Pulse via zoompan sin() expression** — Spec'd in `config/video/therapeutic_video_rules.yaml` but not implemented. Pure FFmpeg, zero new dependencies. Exact expression derivable from confirmed `zoompan` `ot` variable support. See § Breathing Pulse Implementation below.
2. **xfade Dissolve** — Already coded in `scripts/video/vce_ffmpeg_builders.py`, disabled in `config/video/render_params.yaml`. Requires refactoring final assembly from concat demuxer to filter_complex chain. 2–4 hours.
3. **Pedalboard Reverb on Narration** — 30 minutes, 5 lines of Python, meaningful audio warmth.

### What to Skip (and Why)

| Tool | Verdict | Reason |
|------|---------|--------|
| ffmpeg-slide-gen (haridsv) | SKIP | 6 stars, dead since Feb 2023. No Ken Burns, no crossfade. Does less than our current assembler. |
| ffmpeg-parallel (HaiziIzzudin) | SKIP | Splits ONE large file into 2 halves. Inverse of our pattern (many short clips → one output). Not applicable. |
| AutoVio | SKIP | No findable open-source project under this name on GitHub or any indexed source. |
| MoviePy 2.0 | SKIP as primary | 20+ second overhead per clip vs milliseconds raw FFmpeg (confirmed MoviePy issue #2165). Breaking API change in v2.0. Architecture is fundamentally slower for our use case. |
| n8n for batch | SKIP (for now) | Setup cost exceeds value for 13-item sequential run. A Python progress-file loop accomplishes the same with zero infrastructure. Re-evaluate if you need event-driven FLUX→FFmpeg triggers. |

### Estimated Integration Effort

| Item | Effort |
|------|--------|
| Enable film grain + vignette (already coded) | 30 min — config flip only |
| Breathing pulse | 1–2 hours |
| Enable xfade dissolve (refactor concat→filter_complex) | 2–4 hours |
| Pedalboard reverb on narration | 30 min |
| ffmpeg-python incremental refactor | 1–2 days (non-urgent) |
| pycaps word captions | 1–2 days (needs Whisper word timestamps) |
| DepthFlow parallax (P1 backlog) | 1–2 weeks (AGPL license review + depth map pipeline) |

---

## Tool-by-Tool Evaluation

### ffmpeg-slide-gen

**URL:** https://github.com/haridsv/ffmpeg-slide-gen
**Stars:** 6 | **License:** Apache-2.0 | **Last Commit:** February 2023 — DEAD (3+ years, no activity)

**What it does:** Generates an FFmpeg concat demux file from a list of images + timestamps (manual, VLC bookmarks, or YouTube transcript). Runs one FFmpeg command to merge with audio. No video effects whatsoever.

**How it maps to our pipeline:** Nominally targets the same step as `assemble_teacher_youtube_slideshow.py` — image list + audio → video. But it stops there.

**What we'd gain:** Nothing. Zero.

**What we'd lose:** Ken Burns zoompan (not supported), per-image zoom parameter variation (not supported), xfade transitions (not supported), therapeutic arc pacing control, any FFmpeg filter chain.

**Integration effort:** Significant (rebuild around a tool that does strictly less)

**Verdict:** SKIP

**Priority:** N/A

---

### ffmpeg-parallel (HaiziIzzudin)

**URL:** https://github.com/HaiziIzzudin/ffmpeg-parallel
**Stars:** Not widely tracked | **License:** Open source | **Last Commit:** Recent enough to be indexed, niche

**What it does:** Splits a single input video into 2 halves, encodes them in parallel using CPU affinity masks, then rejoins. Designed to speed up encoding of one large file.

**How it maps to our pipeline:** It does not. Our bottleneck is encoding many short per-image segments, which we already parallelize with `multiprocessing.Pool(4)`. This tool addresses single-file encoding — the inverse of our pattern.

**Does it handle different filter chains per segment?** No — it encodes both halves of one video with the same settings. We need different `zoompan` parameters per image (for Ken Burns variety).

**macOS + Ubuntu?** Not clearly tested on macOS.

**What we'd gain:** Nothing applicable.

**Integration effort:** N/A — not replacing anything

**Verdict:** SKIP

**Priority:** N/A

---

### MoviePy 2.0

**URL:** https://github.com/Zulko/moviepy | https://pypi.org/project/moviepy/
**Stars:** ~12,000 | **License:** MIT | **Last Commit:** Active (v2.0 released with breaking API changes from v1)

**What it does:** Python library for programmatic video editing — cut, concatenate, apply effects, add audio — by decoding frames into NumPy arrays and re-encoding via FFmpeg.

**Ken Burns support:** Yes, via custom `resize`/crop functions applied per-frame through `fl_image()`. More readable than FFmpeg expressions, but not faster.

**Crossfade support:** Yes — `CompositeVideoClip` with `crossfadein`/`crossfadeout`. Confirmed working but reported as very slow (open issue #1557).

**Audio sync:** Supported through `set_start()` and duration-based clip assembly.

**Performance vs FFmpeg subprocess:** Severely slower. Confirmed benchmark: MoviePy takes 20+ seconds for operations FFmpeg subprocess handles in milliseconds (MoviePy issue #2165). Root cause: MoviePy decodes every frame to NumPy, then hands it back to FFmpeg for re-encoding — a double I/O penalty baked into its architecture.

**Memory usage:** Loads decoded frames into RAM. For 20 images at 1920×1080, each generating a 5-minute video, this is a meaningful concern.

**LUT / color grading support:** Not natively. Requires a custom geq-equivalent or external filter.

**What we'd gain:** More Pythonic API, readable per-frame transforms.

**What we'd lose:** Speed (confirmed 20×+ slower), single-pass encode efficiency, compatibility with our existing FFmpeg filter chains.

**Integration effort:** Significant (rewrite entire assembler, accept major performance regression)

**Verdict:** SKIP as primary assembler. Keep FFmpeg.

**Priority:** N/A

---

### n8n (Workflow Automation)

**URL:** https://n8n.io | https://github.com/n8n-io/n8n
**Stars:** ~50,000+ | **License:** Sustainable Use License (source-available, not OSI open source) | **Last Commit:** Active, weekly releases

**What it does:** Visual node-based workflow automation. Self-hosted via Docker. Can run shell commands, watch directories, respond to webhooks.

**FFmpeg nodes:** No native FFmpeg node. Use the Execute Command node. A community Docker image (`yigitkonur/n8n-docker-ffmpeg`) bundles FFmpeg into the n8n container.

**ComfyUI integration:** Yes — community node `n8n-nodes-comfyui` (mason276752, GitHub). Supports triggering ComfyUI workflows, polling for completion, retrieving generated images. Actively used for FLUX image gen automation in 2025–2026.

**Directory monitoring:** Yes — File Trigger or Watch Folder nodes can trigger workflows when ComfyUI outputs images to a directory.

**Worth it for 13-teacher overnight batch?** No. Docker + custom image + FFmpeg bundle + ComfyUI node installation + workflow design exceeds the value for a sequential 13-item run. A Python script with a JSON progress file accomplishes the same. **Re-evaluate** if you want event-driven orchestration: "when FLUX finishes teacher N's images, immediately start FFmpeg assembly for teacher N" — n8n with the ComfyUI node becomes genuinely useful for that decoupled pattern.

**What we'd gain:** Visual workflow editor, webhook triggers, ComfyUI event integration, retry UI.

**What we'd lose:** Simplicity. A nohup Python loop is zero-infrastructure.

**Integration effort:** Significant for initial setup; trivial per workflow after setup.

**Verdict:** EVALUATE (P2 — only if event-driven pipeline decoupling is needed)

**Priority:** P2

---

### AutoVio

**URL:** Not found
**Stars:** N/A | **License:** N/A | **Last Commit:** N/A

**What it does:** No project named "AutoVio" is discoverable on GitHub or any indexed source as of April 2026. Closest matches found: `auto-vid` (ossamaweb — serverless TTS/music enrichment pipeline) and AI-Auto-Video-Generator (DALL-E + ElevenLabs based, not self-hostable with external image banks). Neither matches the described use case.

**Verdict:** SKIP — cannot evaluate a non-findable project

**Priority:** N/A

---

### ffmpeg-python (Python bindings)

**URL:** https://github.com/kkroening/ffmpeg-python
**Stars:** ~11,000 | **License:** Apache-2.0 | **Last Commit:** Active (458 commits, CI workflows present; noted in issue #760 as overdue for a new PyPI release — use from source or pin to latest tagged commit)

**What it does:** Python bindings that build FFmpeg filter graphs as composable Python objects, then compile and execute them. The `.filter()` method accepts any FFmpeg filter name and arbitrary keyword/expression arguments, passing expressions through as strings.

**Can it do everything raw subprocess FFmpeg does?** Yes. Any filter expressible as a command-line string is expressible via `.filter('filtername', param='expression_string')`. Variables like `time`, `ot`, `iw`, `ih`, `zoom` in expressions are passed through verbatim.

**zoompan support:** Supported via `.filter('zoompan', z='1+0.03*sin(2*3.14159*ot/10)', ...)`. There is a known niche bug (issue #876, July 2025) affecting users who rely on a named `zoom` shorthand — not our pattern (we pass the full expression string).

**colorbalance support:** Yes — `.filter('colorbalance', rs=0.1, gs=0.0, bs=-0.1)`.

**lut3d support:** Yes — `.filter('lut3d', file='assets/luts/warm_therapeutic.cube')`.

**Maintainability improvement:** Significant. Current pattern:

```python
f"-vf zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={d}:fps={fps}:s={w}x{h},lut3d=file={cube}"
```

Becomes composable Python objects with named parameters, no escaping bugs, and testable intermediate nodes. Critical for complex chained filters (zoompan → colorbalance → lut3d → noise → vignette).

**Performance vs subprocess:** Identical — both compile to the same FFmpeg command. Zero runtime cost difference.

**What we'd gain:** Maintainable filter chains, fewer escaping bugs, testable filter graph construction.

**What we'd lose:** Nothing. This is a strict improvement over string formatting.

**Integration effort:** Moderate (refactor existing filter chains; no change to logic or output)

**Verdict:** USE — adopt incrementally. Start with new filter chains (breathing pulse, xfade refactor), then touch existing chains as they're modified.

**Priority:** P1

---

### DepthFlow (P1 Backlog Item)

**URL:** https://github.com/BrokenSource/DepthFlow
**Stars:** ~1,400 | **License:** AGPL-3.0 | **Last Commit:** Active (396 commits, issues active August 2025)

**What it does:** Converts a still image (+ optional depth map) into a looping 3D parallax video using a GPU-accelerated GLSL shader. Produces seamless loops, 2.5D motion depth effect. Includes built-in post-effects: lens distortion, depth of field, vignette. Available as `pip install depthflow`.

**Works with FLUX-generated images?** Yes — any PNG/JPG is valid input. For best results, provide a depth map, which ComfyUI can generate with Depth-Anything or MiDaS nodes. Without an explicit depth map, DepthFlow uses AI depth estimation internally.

**ComfyUI integration:** Yes — `ComfyUI-Depthflow-Nodes` (akatz-ai, available on CivitAI and GitHub). Adds a DepthFlow node directly into your FLUX workflow on Pearl Star. This means depth + parallax can be generated in one ComfyUI pass alongside the FLUX image.

**Self-hostable on Pearl Star (Ubuntu GPU)?** Yes — PyPI install, GLSL runs on GPU via OpenGL. RTX 3060 confirmed at 8K/50fps. Ubuntu Linux is supported.

**AGPL-3.0 license implications:** Any code that links/calls DepthFlow in a network service must be open-sourced under AGPL. Offline batch use (no network service exposure) is generally acceptable. Review before wiring into a deployed service endpoint.

**Therapeutic appropriateness:** The slow parallax motion (0.5–2s cycle, subtle depth shift) is calmer and more cinematic than Ken Burns. Use selectively: 3–5 key atmospheric shots per 5-minute video, not all 20 images.

**What we'd gain:** Cinematic 3D depth effect on still FLUX images, optional per the shot plan.

**What we'd lose:** Complexity (depth map pipeline, AGPL review, GPU dependency for a new effect stage).

**Integration effort:** Significant (AGPL review + depth map generation in ComfyUI + new pipeline stage)

**Verdict:** EVALUATE

**Priority:** P1 (as already listed in `docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md` P1 backlog)

---

## Breathing Pulse Implementation

The breathing pulse is **spec'd in `config/video/therapeutic_video_rules.yaml`** (`breathing_pulse.target_bpm=6`, `cycle_s=10`, `inhale_s=4`, `hold_s=2`, `exhale_s=4`, `amplitude_pct_therapeutic_min=2`, `amplitude_pct_therapeutic_max=4`) but **not implemented** in `run_render.py` or the VCE filter builders.

### Sinusoidal Approximation (Simplest)

For a smooth sine wave (no distinct hold phase):

```
z='1+0.03*sin(2*3.14159*ot/10)'
```

- `ot` = output timestamp in seconds (confirmed FFmpeg zoompan variable)
- `0.03` = 3% amplitude (center of 2–4% therapeutic range)
- `/10` = 10-second cycle (6 BPM)
- Center-locked pan: `x='iw/2-(iw/zoom/2)'`, `y='ih/2-(ih/zoom/2)'`

### Asymmetric Expression (Spec-Compliant: 4s inhale / 2s hold / 4s exhale)

```
z='1+0.03*if(lt(mod(ot,10),4), mod(ot,10)/4, if(lt(mod(ot,10),6), 1, (10-mod(ot,10))/4))'
```

Phase behavior:
- `mod(ot,10)` in `[0, 4)`: linear ramp 1.00 → 1.03 (inhale)
- `mod(ot,10)` in `[4, 6)`: hold at 1.03 (hold)
- `mod(ot,10)` in `[6, 10)`: linear ramp 1.03 → 1.00 (exhale)

Full filter string for a 10-second static shot at 24fps, 1920×1080:

```
zoompan=z='1+0.03*if(lt(mod(ot\,10)\,4)\,mod(ot\,10)/4\,if(lt(mod(ot\,10)\,6)\,1\,(10-mod(ot\,10))/4))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:fps=24:s=1920x1080
```

Note: commas inside `if()` / `lt()` expressions must be escaped as `\,` in shell strings, or passed as raw string inside Python subprocess list args (where no shell escaping is needed).

### Relationship to Ken Burns — Mutual Exclusion

These are competing zoompan filters — you cannot stack two `zoompan` on the same stream. Choose per shot:

| Shot Type | Motion | Source |
|-----------|--------|--------|
| Static atmospheric (70–80% of shots) | Breathing pulse | `therapeutic_video_rules.yaml` → `motion_budget_pct: 0` in RESOLVE |
| Dynamic transitional (20–30% of shots) | Ken Burns (directional pan + linear zoom) | `motion_policy.yaml` |

**Implementation:** Add a `motion_type: breath | kenbur` field to the shot plan metadata. The VCE filter builder in `scripts/video/vce_ffmpeg_builders.py` selects the zoompan expression string accordingly. This is approximately 15 lines of code in the builder.

### Where it goes in the codebase

- **`scripts/video/vce_ffmpeg_builders.py`** — add `build_breathing_pulse_filter(amplitude_pct, cycle_s)` function alongside existing `build_vignette_filter`, `build_noise_filter`, etc.
- **`config/video/render_params.yaml`** — add `breathing_pulse: enabled: false / amplitude_pct: 3 / cycle_s: 10` (mirrors the pattern of existing P0 upgrades)
- **`scripts/video/run_render.py`** — gate on `breathing_pulse.enabled` and per-clip `motion_type` from shot plan

---

## Effects Catalog

### xfade Dissolve (Already Coded — Enable It)

**FFmpeg filter:** `-filter_complex "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=<cumulative_s>"`

**Therapeutic appropriateness:** High — dissolve is the softest visual transition, avoids shock cuts between atmospheric images.

**Performance cost:** Low — GPU-accelerated in FFmpeg; adds ~1s encode time per transition.

**Key constraint and implementation note:** xfade requires identical fps, pixel format, and resolution between segments (already enforced by our pipeline at 24fps yuv420p 1920×1080). The architectural change is that xfade requires `filter_complex` chaining, not the concat demuxer. For 20 segments, chain them as: `[seg0][seg1]xfade=...[v01]; [v01][seg2]xfade=...[v012]; ...` Pre-calculate each `offset` as cumulative segment duration minus accumulated overlap: `offset_n = sum(durations[0:n]) - n * transition_duration`.

**Easing extension:** `xfade-easing` (scriptituk — https://github.com/scriptituk/xfade-easing) provides CSS-style easing curves (e.g., `easeinoutcubic`) as custom xfade expressions. Useful for PEAK→RELEASE transition which benefits from a slower ease-out.

---

### Film Grain / Noise (Already Coded — Enable It)

**FFmpeg filter:** `noise=c0s=6:c0f=t+u`

**Parameters for therapeutic content:**
- `c0s=6`: subtle grain (range 0=off, 15=subtle, 30=visible). The existing config default of 15 is too visible for calming content — 6–8 is more appropriate.
- `c0f=t+u`: temporal (`t`) flag ensures grain changes frame-to-frame (authentic film behavior); uniform (`u`) flag produces fine grain.

**Therapeutic appropriateness:** High — adds analog warmth, counteracts clinical smoothness of AI-generated FLUX images.

**Performance cost:** Low-medium — adds ~10–15% encode time, CPU-bound.

---

### Vignette (Already Coded — Enable It)

**FFmpeg filter:** `vignette=angle=PI/5`

**Parameters for therapeutic content:** `angle` from 0 (no effect) to PI/2 (extreme). `PI/5` (≈0.63 rad) produces subtle darkening at corners, drawing focus inward toward the teacher or nature element in the center of frame.

**Therapeutic appropriateness:** High — grounds the frame, reduces visual noise at edges, creates intimacy.

**Performance cost:** Very low — nearly free computationally.

---

### Pedalboard Reverb on Narration Audio

**Library:** https://github.com/spotify/pedalboard
**Stars:** ~5,000 | **License:** Apache-2.0 | **Maintenance:** Active (Spotify, PyCon 2025 talk)

**Python pattern:**
```python
from pedalboard import Pedalboard, Reverb
from pedalboard.io import AudioFile

board = Pedalboard([Reverb(room_size=0.15, damping=0.7, wet_level=0.08, dry_level=0.92)])
with AudioFile('narration.mp3') as f:
    audio = f.read(f.frames)
    sample_rate = f.samplerate
effected = board(audio, sample_rate)
with AudioFile('narration_reverb.mp3', 'w', sample_rate, effected.shape[0]) as f:
    f.write(effected)
```

**Parameters for therapeutic narration:**
- `room_size=0.1–0.2`: small-medium room (not a concert hall)
- `wet_level=0.05–0.12`: barely perceptible — spatial warmth, not echo
- `dry_level=0.90–0.95`: narration remains clear and foreground

**Therapeutic appropriateness:** High — naturalizes CosyVoice2's dry TTS output, adds human presence and spatial depth.

**Performance cost:** Negligible — real-time or faster.

**Where it goes in the pipeline:** Between CosyVoice2 output and FFmpeg audio input in `run_render.py` (or a pre-processing step in the audio assembly stage). Process the narration WAV/MP3 once before FFmpeg mux.

---

### pycaps Word-Level Captions

**URL:** https://github.com/francozanardi/pycaps
**Stars:** Not widely tracked | **License:** MIT | **Last Commit:** Active (Python 3.10–3.12 confirmed)

**What it does:** Word-level caption animation using Whisper word timestamps. CSS `.word-being-narrated` state highlights the current word in gold/white as speech progresses. Multiple built-in animations: fade, pop, typewriting.

**Integration with CosyVoice2:** If CosyVoice2 alignment data provides word-level timestamps (word → start_s, end_s), those feed directly to pycaps without re-running Whisper. If not, run Whisper once on the finished narration audio.

**Therapeutic appropriateness:** Medium — accessibility benefit, keeps viewer engaged. Use gentle fade-highlight, not aggressive pop animations.

**Performance cost:** Medium — Whisper inference once per video if alignment timestamps aren't already available.

**Where it goes in the pipeline:** Post-render pass, or integrated into the caption stage (`run_caption_adapter.py`). Replaces static SRT-style drawtext.

---

### DepthFlow Parallax (P1 Backlog)

See Tool Evaluations above. Therapeutically appropriate for slow, contemplative atmospheric shots. Not glitch, flash, or particle. Use selectively — 3–5 shots per 5-minute video.

---

### Effects NOT Recommended (Therapeutic Filter)

| Effect | Reason to Skip |
|--------|----------------|
| Fast cuts / glitch | Anxiety-inducing, opposite of therapeutic pacing |
| Bright flashes | Contraindicated for calming content, potential photosensitivity concern |
| Heavy particle overlays | Distracting, competes with the teacher/nature image |
| Speed ramp / echo effects | Disorienting for therapeutic arc |
| Chromatic aberration | Clinical association, breaks calming frame |

---

## Batch Orchestration Recommendation

### Recommended Approach: Python Progress-File Loop with nohup

For 13 teachers overnight, a purpose-built Python orchestrator with a JSON progress file is the right balance of simplicity, reliability, and observability. No Redis, no Celery, no n8n.

**Architecture pattern:**

```python
# scripts/video/batch_render_teachers.py
import json, subprocess, time
from pathlib import Path

PROGRESS_FILE = Path("artifacts/video/batch_progress.json")
TEACHERS = [f"teacher_{i:02d}" for i in range(1, 14)]  # or load from config

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {t: "pending" for t in TEACHERS}

def save_progress(state):
    PROGRESS_FILE.write_text(json.dumps(state, indent=2))

state = load_progress()
for teacher in TEACHERS:
    if state[teacher] in ("done", "failed_permanent"):
        continue
    for attempt in range(3):
        result = subprocess.run(
            ["python3", "scripts/video/run_render.py", "--teacher", teacher, ...],
            timeout=3600  # 1hr hard limit per teacher
        )
        if result.returncode == 0:
            state[teacher] = "done"
            save_progress(state)
            break
        state[teacher] = f"failed_attempt_{attempt + 1}"
        save_progress(state)
        time.sleep(60)  # backoff between retries
    else:
        state[teacher] = "failed_permanent"
        save_progress(state)
```

**Launch overnight:**
```bash
nohup python3 scripts/video/batch_render_teachers.py > artifacts/video/batch.log 2>&1 &
echo $! > artifacts/video/batch.pid
```

**Morning check:**
```bash
tail -50 artifacts/video/batch.log
cat artifacts/video/batch_progress.json
```

### Error Handling Strategy

| Failure Type | Strategy |
|--------------|----------|
| FFmpeg encode error | Retry up to 3 times with 60s backoff |
| FLUX / ComfyUI VRAM OOM | 0 retries — requires manual intervention; mark `failed_permanent`, continue to next teacher |
| FLUX API network timeout | Retry up to 3 times with 30s backoff within the image gen script |
| Hard timeout (1hr) | `subprocess.TimeoutExpired` → mark failed, continue |
| Orchestrator crash | Progress file preserves state; restart picks up from last known position |

### Why Not RQ, Celery, or n8n

| Tool | Assessment |
|------|-----------|
| **RQ (Redis Queue)** | Requires Redis. Task durability is worse than a plain JSON file without Redis persistence configured. A separate `rq-scheduler` package is needed for scheduling. Pure overhead for 13 sequential items. Revisit if you scale to hundreds of teachers. |
| **Celery** | Better durability and scheduling than RQ, but significant configuration surface (broker, backend, worker config, retry decorators). Development time exceeds benefit for a 13-item sequential run. |
| **n8n** | Docker setup + custom image + ComfyUI node install + workflow design. Worth it only if you need event-driven triggers (FLUX completion → FFmpeg start), not for sequential teacher runs. |

### ComfyUI Batch Queue Notes

ComfyUI's GUI Auto Queue re-queues the same workflow continuously. For varied per-teacher prompts, the ComfyUI Python API is cleaner:

```python
import requests, time

# Submit a workflow
resp = requests.post("http://localhost:8188/prompt", json={"prompt": workflow_dict})
prompt_id = resp.json()["prompt_id"]

# Poll for completion
while True:
    history = requests.get(f"http://localhost:8188/history/{prompt_id}").json()
    if prompt_id in history:
        break
    time.sleep(5)
```

This pattern integrates directly into the Python batch loop above — no separate queue manager needed.

---

## Architecture Recommendation

### Keep FFmpeg as Primary Assembler

Raw FFmpeg subprocess (or ffmpeg-python bindings) remains the right foundation. MoviePy's frame-decode architecture is fundamentally incompatible with a performance-sensitive pipeline. No library beats FFmpeg's filter graph for per-pixel operations (zoompan, lut3d, noise, vignette, xfade) applied in a single encode pass with no intermediate files.

### Effects via FFmpeg Filters, Not Libraries

All P0 effects (breathing pulse, lut3d, noise, vignette, xfade) belong as FFmpeg filter chains — single encode pass, maximum quality, no intermediate files. The exception is **Pedalboard for audio**: process narration before FFmpeg mux; Pedalboard's C++ DSP is meaningfully better quality than FFmpeg's audio filters for reverb.

### Recommended Filter Chain Order (per segment)

```
[image input]
  → zoompan (breathing pulse OR ken burns, driven by shot plan motion_type)
  → lut3d (color grade — section-based .cube file from color_grade_presets.yaml)
  → noise (film grain — c0s=6, always on once enabled)
  → vignette (angle=PI/5, always on once enabled)
  [output segment MP4]

[assembled segments + pedalboard-processed narration audio]
  → xfade chained filter_complex (dissolve, 0.5s, between all segments)
  → final output MP4
```

### Migrate to ffmpeg-python Incrementally

Start by implementing breathing pulse and the xfade refactor using ffmpeg-python's filter API. This gives type-checked filter parameters and eliminates escaping bugs in complex expressions. Existing Ken Burns chains don't need refactoring until they're next modified.

### Minimal Additions for Maximum Improvement (Ordered)

1. **Enable film grain (`c0s=6`) + vignette (`PI/5`)** — already coded in `vce_ffmpeg_builders.py`, flip config in `render_params.yaml`. 30 minutes. Zero risk.
2. **Breathing pulse** — add `build_breathing_pulse_filter()` to `vce_ffmpeg_builders.py`, gate in `run_render.py` on per-clip `motion_type`. 1–2 hours.
3. **Enable xfade dissolve** — refactor final assembly from concat demuxer to filter_complex chain. 2–4 hours.
4. **Pedalboard reverb on CosyVoice2 narration** — pre-process audio before FFmpeg mux. 30 minutes.
5. **pycaps word captions** — needs Whisper word timestamps from CosyVoice2 alignment data. 1–2 days.
6. **DepthFlow parallax** — AGPL license review first, then depth map pipeline in ComfyUI, then new render stage. 1–2 weeks.

---

## Source References

- ffmpeg-slide-gen: https://github.com/haridsv/ffmpeg-slide-gen
- ffmpeg-parallel: https://github.com/HaiziIzzudin/ffmpeg-parallel
- MoviePy efficiency issue #2165: https://github.com/Zulko/moviepy/issues/2165
- n8n-docker-ffmpeg: https://github.com/yigitkonur/n8n-docker-ffmpeg
- n8n-nodes-comfyui: https://github.com/mason276752/n8n-nodes-comfyui
- ffmpeg-python: https://github.com/kkroening/ffmpeg-python
- ffmpeg-python zoompan issue #876: https://github.com/kkroening/ffmpeg-python/issues/876
- DepthFlow: https://github.com/BrokenSource/DepthFlow
- ComfyUI-Depthflow-Nodes: https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes
- FFmpeg zoompan filter docs (8.0.1): https://ayosec.github.io/ffmpeg-filters-docs/8.0/Filters/Video/zoompan.html
- xfade crossfade — OTTVerse: https://ottverse.com/crossfade-between-videos-ffmpeg-xfade-filter/
- xfade-easing extensions: https://github.com/scriptituk/xfade-easing
- pycaps: https://github.com/francozanardi/pycaps
- Pedalboard (Spotify): https://github.com/spotify/pedalboard
- Celery vs RQ comparison 2025: https://generalistprogrammer.com/comparisons/celery-vs-rq
- ComfyUI batch processing 2026: https://apatero.com/blog/comfyui-batch-processing-1000-images-automation-2026
- n8n ComfyUI integration: https://dev.to/worldlinetech/automating-image-generation-with-n8n-and-comfyui-521p
- geq as zoompan alternative (sinusoidal examples): https://hhsprings.bitbucket.io/docs/programming/examples/ffmpeg/manipulating_video_colors/use_of_geq_as_zoompan_alternative.html
