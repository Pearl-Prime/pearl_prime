# Pearl Prime — Podcast Pipeline (complete operator guide)

**Orchestrator:** `scripts/podcast/run_podcast_pipeline.py`  
**Stages:** `assemble_podcast_episode.py`, `render_podcast_audio.py`, `generate_podcast_feed.py`, `upload_podcast_to_r2.py`  
**Registry:** `config/pipeline_registry.yaml` → `pipelines.podcast`  
**Spec:** `docs/PODCAST_PIPELINE_INTEGRATION_SPEC.md`

---

## Before you start

1. `python3 scripts/pipeline/create_job.py --pipeline podcast --brand-id … --locale … --week … --book-dir … --workspace <OUT_ROOT>`
2. `python3 scripts/pipeline/acknowledge_guide.py --workspace <OUT_ROOT>`
3. Run orchestrator or individual stage scripts with **`--workspace`** (same directory as `job.json`).

---

## Stage outputs

| Stage | Artifact |
|-------|----------|
| assemble | `assembly_*.json` |
| render_audio | `*.mp3` + `*.render_report.json` |
| feed | `feed.xml` |
| upload | `upload_manifest.json` (R2) |

TTS routing: auto selects providers per locale (see `render_podcast_audio.py` and `scripts/podcast/_lib.py`).

---

## Config map

| Path | Role |
|------|------|
| `config/podcast/podcast_format.yaml` | Segment structure, duration targets |
| `config/catalog_planning/brand_identity_system.yaml` | Artwork colors |
| Env: `R2_*`, `PODCAST_PUBLIC_BASE_URL` | Upload + enclosure URLs |

---

## Loudness / mastery

Target **−16 LUFS**, **−1.0 dBTP** true peak in render path (see render implementation and integration spec).

---

## Common mistakes

- Missing **`--workspace`** so stage scripts cannot find `job.json`.
- Running **feed** before **render** produces episode meta.
- Upload without **R2** env vars — gate fails; use `--no-job-check` only for local dry runs.

---

## Example orchestrator

```bash
PYTHONPATH=. python3 scripts/podcast/run_podcast_pipeline.py \
  --brand-id stillness_press --locale en-US --week 2026-W15 \
  --book-dir path/to/book_artifacts --output-dir path/to/package \
  --workspace path/to/package
```
