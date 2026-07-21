# Handoff — CosyVoice MP3 bank → social reels + TTS captions (2026-07-19)

**Acceptance layer:** `system working` — bank **1620/1620** + matrix **60/60** PRIMARY packs + Metricool dry-runs.  
Not production_ready / not bestseller / not live Metricool publish.

## Bank

| Item | Value |
|------|-------|
| MANIFEST | `artifacts/social_media_voice_bank_2026-07-19/MANIFEST.tsv` |
| Status | **1620 ok / 0 fail** (Cosy residual cleared after removing `/tmp/COSYVOICE_PAUSED_FOR_MANGA` keeper) |
| Local MP3s | `artifacts/social_media_voice_bank_2026-07-19/mp3/` (1620) |
| R2 prefix | `social_media/voice_bank/20260719b/` |
| Lookup | `scripts/social_media/voice_bank_lookup.py` |
| Prefetch | `scripts/social_media/prefetch_voice_bank_manifest.py` |

## Matrix video (PRIMARY broll)

| Item | Value |
|------|-------|
| Driver | `scripts/social_media/render_voice_bank_matrix_batch.py` |
| Packs | **60/60** persona×topic (3×20) |
| Output | `artifacts/social_media_voice_bank_2026-07-19/matrix_batch/` |
| Coverage | `.../matrix_batch/COVERAGE.md` |
| Craft | lavfi color plates + kinetic ASS + bank VO (smoke keeps photo Ken Burns) |
| Plates helper | `scripts/social_media/stock_plates_for_topic.py` |
| Caption packs | `scripts/social/evergreen_shortform_caption_pack.py` — full `TOPICS`×`PERSONAS` |

## Metricool dry-run

| Item | Value |
|------|-------|
| Builder | `scripts/social_media/build_voice_bank_pilot_metricool_dry_run.py` |
| Payloads | 60 × `.../matrix_batch/metricool_dry_run/*__tiktok_dry_run.json` |
| Safety | `draft/autoPublish=false/dryRun=true`, media `UPLOAD_REQUIRED` |
| Report | `.../metricool_dry_run/publish_safety_report.md` |
| Live publish | **not authorized** |

## Smoke (operator-approved craft)

- Atom: `EVG-ENUS-ANXI-CORP-SS-01`
- MP4: `artifacts/social_media_voice_bank_2026-07-19/smoke_reel/EVG-ENUS-ANXI-CORP-SS-01_short_9x16.mp4`
- Stack: photo broll_montage Ken Burns + kinetic ASS + bank VO

## Git

- Branch: `agent/social-media-voice-bank-video-wire-20260719` (offline; GitHub 403 — do not push until unblocked)
- Do **not** commit multi‑GB MP4/mp3 trees — receipts + scripts + handoff only

## How to use

```bash
# Full matrix (resume)
VOICE_BANK_FFMPEG_PRESET=ultrafast PYTHONPATH=. python3 -u \
  scripts/social_media/render_voice_bank_matrix_batch.py --topics all --personas all --resume

# Metricool dry-runs
PYTHONPATH=. python3 scripts/social_media/build_voice_bank_pilot_metricool_dry_run.py \
  --receipt-dirs artifacts/social_media_voice_bank_2026-07-19/matrix_batch
```
