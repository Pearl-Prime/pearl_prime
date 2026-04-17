# Weekly rollout framework

## Prose lane (existing)

- **Packages:** `scripts/build_weekly_brand_package.py` builds `artifacts/weekly_packages/<brand>/<week>/` (CSV manifest, rendered books, metadata).
- **Portal:** `server/routes/brand_admin.py` exposes weekly package listing for authenticated brand admins.
- **Observability:** `.github/workflows/weekly-pipeline.yml` runs `scripts/release/weekly_pipeline_with_marketing.py` (canary + systems test) on a Monday UTC schedule (`0 8 * * 1`).

## Manga lane (new)

- **Config:** `config/weekly_rollout/manga_rollout.yaml` — per-brand topics, `books_per_week`, `require_image_bank_coverage`, and `image_backend` (`replay` uses `image_bank/<brand>/<topic>/`; `comfyui` / `runcomfy` require Pearl Star / RunComfy).
- **Runner:** `scripts/weekly_manga_rollout.py` — selects topics with enough PNGs, calls `scripts/run_manga_pipeline.py` logic, uploads exports to Cloudflare R2 under `{brand_id}/manga/{YYYY-MM-DD}/`, mirrors podcast-style credentials (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`). Aliases `CF_R2_ACCESS_KEY` / `CF_R2_SECRET_KEY` are also accepted in `scripts/manga/r2_manga_release.py`.
- **Digest:** Markdown fragments under `artifacts/weekly_digests/` (`{brand}_weekly_digest_{date}.md`) list presigned GET URLs (7-day default) for PDF/CBZ/EPUB. Brand admins can ingest the same paths as other weekly artifacts or receive copies via SendGrid when `SENDGRID_API_KEY` and `WEEKLY_ROLLOUT_OPERATOR_EMAIL` are set.
- **GitHub Actions:** `.github/workflows/weekly-manga-rollout.yml` (Monday `0 14 * * 1` UTC, aligned with common US-morning windows). Swap `runs-on` to `[self-hosted, pearl-star-gpu]` when the Pearl Star runner is registered and switch `image_backend` to `comfyui` for live panels.

## Knobs

- Increase `books_per_week` or lower `require_image_bank_coverage` only after image banks and QA capacity catch up.
- **Cadence:** Default is **one manga per brand per week** (`books_per_week: 1`).
