# Pearl Prime — Video Pipeline (complete operator guide)

**Authority:** `docs/VIDEO_PIPELINE_SPEC.md`, `config/pipeline_registry.yaml`, `scripts/video/run_pipeline.py`.  
**Job enforcement:** Every stage script calls `require_stage(...)` unless `--no-job-check` (CI only).

---

## Before you start

1. Create a job: `python3 scripts/pipeline/create_job.py --pipeline video ... --workspace <DIR>`
2. Acknowledge the guide: `python3 scripts/pipeline/acknowledge_guide.py --workspace <DIR>`
3. Run stages **in registry order** (see `config/pipeline_registry.yaml` → `pipelines.video.stages`)
4. Never hand-roll a one-off FFmpeg/TTS path for production assets — use the scripts under `scripts/video/`.

---

## Stages (single source of truth)

Order is defined only in **`config/pipeline_registry.yaml`**. Typical flow:

| Stage | Script | Output artifact |
|-------|--------|-----------------|
| script_prep | `prepare_script_segments.py` | `script_segments.json` |
| shot_plan | `run_shot_planner.py` | `shot_plan.json` |
| asset_resolve | `run_asset_resolver.py` | `resolved_assets.json` |
| timeline | `run_timeline_builder.py` | `timeline.json` |
| caption | `run_caption_adapter.py` | `captions.json` |
| layer_comp | `run_layer_compositor.py` | `composited_layers.json` |
| animation | `run_animation_engine.py` | `animation_plan.json` |
| soundtrack | `run_soundtrack_engine.py` | `soundtrack_plan.json` |
| qc_plan | `run_qc.py --qc-mode plan` | `qc_summary.json` |
| render | `run_render.py` | video under `--out-dir` |
| qc_publish | `run_qc.py --qc-mode publish` | `qc_summary_publish.json` |
| platform_adapt | `run_platform_adapter.py` | `platform_variants.json` |
| multilang | `run_multilang_renderer.py` | `multilang_plan.json` |
| upload | `run_upload.py` | `upload_results.json` (optional) |

Voice, music, and image bank behavior are configured under **`config/video/`** and **`config/tts/brand_narrator_voice_map.yaml`**.

---

## Config map (high value)

| Path | Role |
|------|------|
| `config/video/pacing_by_content_type.yaml` | Segment duration / content type |
| `config/video/therapeutic_video_rules.yaml` | Color temp arc, therapeutic pacing |
| `config/video/motion_policy.yaml` | Motion budget (mostly static for therapeutic) |
| `config/video/visual_intent_defaults.yaml` | Default framing / motion per intent |
| `config/video/asset_selection_priority.yaml` | Resolver fallback order |
| `config/video/format_specs.yaml` | Aspect ratios per VCE format |
| `config/video/caption_policies.yaml` | Caption limits per platform |

---

## Common mistakes (agents keep repeating)

- Skipping `script_segments.json` / shot plan and jumping straight to **render**.
- Using **one background image** for an entire video — resolver + timeline must map **per-shot** assets.
- Ignoring **QC plan** before render — `run_qc.py --qc-mode plan` must pass.
- Wrong **voice** — resolve from `brand_narrator_voice_map.yaml` for the brand + locale.
- **Mono** or dropped audio after concat — use the repo render path; do not `concat` incompatible audio.

---

## If validation fails

1. `python3 scripts/pipeline/job_status.py <workspace>`
2. Open the stage’s output JSON and the QC summary.
3. Re-read **`docs/VIDEO_PIPELINE_SPEC.md`** § Shot Planner, Asset Resolver, Timeline.

---

## Example: full orchestrator

```bash
PYTHONPATH=. python3 scripts/video/run_pipeline.py \
  --plan-id my-plan \
  --render-manifest fixtures/video_pipeline/render_manifest.json \
  --out-dir artifacts/video/my-plan \
  --no-skip-render
```

For **enforced** runs, prefer creating `job.json` in `--out-dir` first and running individual stage scripts with `--workspace` pointing at that directory.

---

## P0 Visual Polish Upgrades (opt-in via config)

All P0 upgrades are **default-off** — set `enabled: true` in the relevant config to activate.

### 1. xfade transitions between clips

Replaces hard cuts with dissolve (or any xfade transition) between rendered clips.

Config: `config/video/render_params.yaml` → `xfade:`

```yaml
xfade:
  enabled: true       # false = hard cuts (default)
  transition: dissolve  # any FFmpeg xfade transition name
  duration_s: 0.5     # crossfade overlap in seconds
```

Note: enabling xfade triggers a re-encode pass during concat (no stream-copy). Duration must be shorter than the shortest clip.

### 2. lut3d color grading

Applies a 3D LUT (.cube file) to the final video for consistent color grading.

Config: `config/video/color_grade_presets.yaml` → `lut3d:`

```yaml
lut3d:
  enabled: true
  lut_path: "assets/luts/warm_therapeutic.cube"
```

A minimal warm-therapeutic LUT is included at `assets/luts/warm_therapeutic.cube`. Replace with a professional .cube file for production. The yuv420p→rgb→yuv chain is handled automatically.

### 3. Film grain (noise)

Adds organic texture via FFmpeg `noise` filter.

Config: `config/video/render_params.yaml` → `noise:`

```yaml
noise:
  enabled: true
  intensity: 15   # c0s value: 0=off, 15=subtle, 30=visible
```

### 4. Vignette

Darkens frame edges via FFmpeg `vignette` filter.

Config: `config/video/render_params.yaml` → `vignette:`

```yaml
vignette:
  enabled: true
  angle: "PI/5"   # cone half-angle; 0=off
```

### 5. Loudness normalisation (pyloudnorm)

Normalises CosyVoice2 narration WAV files to a target integrated LUFS before mixing into the video. Requires `pyloudnorm` and `soundfile`.

Install: `pip install pyloudnorm soundfile`

Config: `config/video/render_params.yaml` → `loudness:`

```yaml
loudness:
  normalize_loudness: true
  target_lufs: -16.0   # YouTube standard; -14 is also common
```

Only applied to `.wav`/`.pcm`/`.aif` narration files. MP3 narration is mixed without normalisation (convert to WAV first if needed).

### 6. Richer QC (post-render)

`run_qc.py` now supports post-render video-level checks in addition to the VCE gate checks:

- Frame count (from ffprobe stream metadata)
- Corruption detection (`ffprobe -v error`)
- Keyframe interval check (warns if avg interval > 10 s)
- SSIM measurement vs. a reference video (optional; requires `ffmpeg-quality-metrics`)

New flags:

```bash
python3 scripts/video/run_qc.py ... \
  --video-path artifacts/video/my-plan/my-plan.mp4 \
  --reference-video artifacts/video/reference/reference.mp4  # optional
```

Results are included in `qc_summary.json` under the `video_qc` key.

Install for SSIM: `pip install ffmpeg-quality-metrics`

---

## New dependencies (P0)

```
pyloudnorm>=0.1.0
soundfile>=0.12.0
ffmpeg-quality-metrics>=3.0.0
```

These are listed in `requirements.txt`. All three are optional at runtime — features
gracefully degrade with a warning if the package is missing.

---

## P1 backlog (not in this PR)

- RQ / Redis job queuing for overnight batch runs
- DepthFlow parallax 3D effect on FLUX stills
- pycaps word-level animated captions
- pedalboard audio post-processing (reverb, EQ, compression)
