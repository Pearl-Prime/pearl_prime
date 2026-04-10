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
