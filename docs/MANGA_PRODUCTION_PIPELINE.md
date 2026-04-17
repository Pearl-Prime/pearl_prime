# Manga production pipeline

## Entry points

| Step | Command / module |
|------|------------------|
| Single book (QA / operator) | `PYTHONPATH=. python3 scripts/run_manga_pipeline.py --brand stillness_press --topic burnout --persona gen_z_professionals --genre shonen --render-book --output-dir artifacts/manga_smoke/` |
| Chapter-only (advanced) | `PYTHONPATH=. python3 scripts/manga/run_manga_chapter.py --workspace … --backend replay\|runcomfy\|noop` |
| Weekly lane | `PYTHONPATH=. python3 scripts/weekly_manga_rollout.py` (`--dry-run`, `--single-book --brand … --topic … --genre …`) |

## Stages (high level)

1. **Series setup** — `phoenix_v4.manga.series.emit.emit_series_setup` writes `series/` JSON (includes manga EI character-author when `brand_id` is set).
2. **Chapter DAG** — `phoenix_v4.manga.runner.chapter_runner.run_chapter_dag` (transmission → writer → visual → images → lettering → layout → ITE → QC → series memory).
3. **Image backends**
   - **`replay` (default smoke):** Maps each `panel_id` to PNGs under `image_bank/<brand>/<topic>/` (cycles if panel count > bank size).
   - **`comfyui`:** `phoenix_v4.manga.image_backend.ComfyUIBackend` — requires `COMFYUI_URL` or `PEARL_STAR_IP` and reachable `/system_stats`.
   - **`runcomfy`:** Cloud RunComfy (`RUNCOMFY_API_KEY`, deployment id).
4. **Exports** — `artifacts/.../exports/` receives `*.pdf`, `*.cbz`, minimal `*.epub` when `--render-book` is set (Pillow required for PDF).

## Image bank gate

Stillness Press canonical slots are **56 PNGs per topic** (see `scripts/manga/stillness_press_image_bank.py`). `run_manga_pipeline` defaults `--min-panel-images 56`. Weekly config uses `require_image_bank_coverage` under `WEEKLY_ROLLOUT_CONFIG.manga_lane`.

## Speech bubbles

Until the bubble sprint lands in the layout composite path, books may ship as **silent strips** with lettering metadata only — acceptable v1; QA template calls this out in `QA_REPORT.md`.

## Cloudflare R2 layout

```
<brand_id>/
  manga/
    YYYY-MM-DD/
      <topic>_<genre>_smoke.pdf
      <topic>_<genre>_smoke.cbz
      <topic>_<genre>_smoke.epub
```

Signed URLs: `boto3` `generate_presigned_url` (default expiry 604800s), same client setup as `scripts/podcast/upload_podcast_to_r2.py`.

## GitHub Actions

- `.github/workflows/manga-smoke-test.yml` — `workflow_dispatch`, default `ubuntu-latest` + `replay` for portable QA.
- `.github/workflows/weekly-manga-rollout.yml` — cron + manual; set secrets to match podcast R2.
- `.github/workflows/manga-rollout-notify.yml` — failure hook placeholder.
- `.github/workflows/pearl-star-health.yml` — optional runner label check (`workflow_dispatch`).

## Credentials

See `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` (Cloudflare) and env names mirrored in `scripts/podcast/upload_podcast_to_r2.py` / `scripts/manga/r2_manga_release.py`. Never commit tokens.
