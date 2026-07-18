# Manga production pipeline

> **Routing (2026-05-29):** Use this doc for **`scripts/run_manga_pipeline.py`** smoke/weekly paths and `run_manga_chapter.py` backends. For **registry jobs + ITE**, use [MANGA_PIPELINE_COMPLETE_GUIDE.md](./MANGA_PIPELINE_COMPLETE_GUIDE.md). For **series setup + canonical DAG**, use [MANGA_PIPELINE_ONBOARDING.md](./MANGA_PIPELINE_ONBOARDING.md). **Render authority:** V5.1 — [docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md](./specs/MANGA_V5_LAYERED_ARCHITECTURE.md) (V4 paths below are legacy).

## Entry points

| Step | Command / module |
|------|------------------|
| Single book (QA / operator) | `PYTHONPATH=. python3 scripts/run_manga_pipeline.py --brand stillness_press --topic burnout --persona gen_z_professionals --genre shonen --render-book --output-dir artifacts/manga_smoke/` |
| **Distribution exports** (post-compose pages) | `PYTHONPATH=. python3 scripts/manga/run_manga_pipeline.py --title-id stillness_press_anxiety_vol1 --page-dir /path/to/page_###.png --formats epub3,cbz,webtoon` |
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

## Distribution pipeline (profile-driven)

After compose, **`scripts/manga/run_manga_pipeline.py`** builds platform exports from `page_###.png` + `load_series_profile()` + `config/manga/format_adaptation_grammars.yaml` (no hardcoded dimensions):

| Format | Script | Notes |
|--------|--------|-------|
| EPUB3 (fixed-layout) | `build_epub3.py` | Apple Books; reading direction from print grammar |
| Print PDF | `build_print_pdf.py` | Bleed canvas from print grammar + brand color palette sidecar |
| CBZ + ComicInfo | `build_cbz.py` | GlobalComix; comp titles in sidecar JSON |
| Webtoon strips | `reformat_webtoon.py` | 800px width from webtoon grammar; requires `webtoon` in `adaptation_targets` |

Dry-run: `--dry-run` loads profile and scans pages without writing. Upload checklist: `generate_upload_checklist.py` (invoked by orchestrator).

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

- `.github/workflows/manga-smoke-test.yml` — `workflow_dispatch`, **replay** on `ubuntu-latest`; **comfyui/runcomfy** waits for `pearl-star-gpu` then runs on self-hosted. Optional `upload_to_r2` / `send_digest` (requires secrets + `WEEKLY_ROLLOUT_OPERATOR_EMAIL` var). See `docs/GITHUB_ACTIONS_BACKGROUND_AGENTS.md`.
- `.github/workflows/weekly-manga-rollout.yml` — cron + manual; set secrets to match podcast R2.
- `.github/workflows/manga-rollout-notify.yml` — failure hook placeholder.
- `.github/workflows/manga-operator-setup-verify.yml` — runner + secrets + operator email var (scheduled + manual).
- `.github/workflows/manga-image-bank-build.yml` — long GPU job to fill Stillness `image_bank/` (opens PR when done).
- `.github/workflows/manga-backend-flip.yml` — opens PR flipping weekly lane to `comfyui` + self-hosted (after operator confirmation).
- `scripts/ci/wait_for_self_hosted_runner.py` — queue wait (smoke GPU path). `scripts/ci/check_pearl_star_runner_online.py` — instant check (operator verify).

## Credentials

See `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` (Cloudflare) and env names mirrored in `scripts/podcast/upload_podcast_to_r2.py` / `scripts/manga/r2_manga_release.py`. Never commit tokens.
