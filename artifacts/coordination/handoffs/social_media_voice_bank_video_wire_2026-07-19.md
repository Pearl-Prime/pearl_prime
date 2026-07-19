# Handoff — CosyVoice MP3 bank → social reels + TTS captions (2026-07-19)

**Acceptance layer:** `system working` (wiring + one-atom smoke). Not catalog batch-render; not production_ready / bestseller register.

## What landed

| Piece | Path |
|-------|------|
| MANIFEST + full speakable | `artifacts/social_media_voice_bank_2026-07-19/MANIFEST.tsv` (`speakable_text` col; backfill via `scripts/social_media/backfill_speakable_text.py`) |
| Onbox writer | `scripts/social_media/generate_voice_bank_onbox.py` writes `speakable_text` |
| Lookup helper | `scripts/social_media/voice_bank_lookup.py` (registry: `social_media_voice_bank_lookup`) |
| VCE | `run_pipeline.py --voice-bank` → caption adapter + voice synthesis prefer bank |
| Social | `evergreen_shortform_caption_pack.py` + `render_faceless_research_complete.py --voice-bank` |
| Smoke reel | `scripts/social_media/smoke_voice_bank_reel.py` |

## Smoke proof (operator listen)

- **Atom:** `EVG-ENUS-ANXI-CORP-SS-01`
- **MP4:** `artifacts/social_media_voice_bank_2026-07-19/smoke_reel/EVG-ENUS-ANXI-CORP-SS-01_short_9x16.mp4`
- **Craft stack (not simple drawtext):** PRIMARY `broll_montage` (multi-plate Ken Burns + cut SFX) + kinetic ASS captions (portrait mid-lower `y≈1286`, wrap 16–18 chars, MarginL/R 96) + CosyVoice bank VO
- **Speakable / caption SSOT:** `artifacts/social_media_voice_bank_2026-07-19/smoke_reel/caption_speakable.txt`
- **Receipt:** `artifacts/social_media_voice_bank_2026-07-19/smoke_reel/SMOKE_RECEIPT.json`
- **Check:** portrait phone — captions fully inset; VO matches speakable; montage cuts audible
- **Fix note:** first smoke used landscape-ish full-width drawtext; replaced with agreed LOOK_COMPARE stack.

## Bank status at wire time

- Local MANIFEST after pull+backfill: ~1346 `ok` / ~274 `fail` (speakable filled for all 1620).
- Remote (Pearl Star) was still climbing (~1366 ok). Residual fails are excluded from video (lookup fail-closed).
- R2 prefix: `social_media/voice_bank/20260719b/` (modulated `20260719/` void).

## How to use

```bash
# VCE short + bank
python3 scripts/video/run_pipeline.py --plan-id <id> --format short --platforms tiktok \
  --voice-bank --no-job-check

# Faceless research lane
python3 scripts/social/render_faceless_research_complete.py --voice-bank --only <example_id>

# One-atom smoke
python3 scripts/social_media/smoke_voice_bank_reel.py --atom-id EVG-ENUS-ANXI-CORP-SS-01
```

## Out of scope (still)

- Full 1,620 automatic reel batch
- ASR/Whisper karaoke alignment
- Re-tuning CosyVoice params / SSML
- GitHub push (account 403) — land offline on `agent/social-media-mp3-bank-20260719` or follow-on


## Bank finish status (2026-07-19 evening)

- Remote MANIFEST peak during session: **~1501 ok / ~119 fail** (target 1620).
- CosyVoice on Pearl Star became unstable under retry (process SIGKILL during/after load; restart loops). Residual fails remain **fail-closed / excluded from video**.
- Local sync for pilot: `mp3/en-US/corporate_managers/anxiety/` = **27** MP3s; MANIFEST backfilled with `speakable_text`.
- Serial retry / watchdog: leave for operator when CosyVoice stays healthy (health 200 for >60s without kill).

## Pilot batch (step 3)

- Pack: `anxiety_corporate` (5 beats, corporate_managers × anxiety)
- MP4: `artifacts/social_media_voice_bank_2026-07-19/pilot_batch/anxiety_corporate_short_9x16.mp4`
- Receipt: `artifacts/social_media_voice_bank_2026-07-19/pilot_batch/anxiety_corporate_RECEIPT.json`
- Atoms: HC-02, PA-02, ME-02, TS-01, SP-02
- Craft: PRIMARY broll_montage + kinetic ASS + per-beat bank VO
- Acceptance: `system working` (pilot), not full catalog


## Metricool dry-run (approved pilot)

- Payload: `artifacts/social_media_voice_bank_2026-07-19/pilot_batch/metricool_dry_run/anxiety_corporate__tiktok_dry_run.json`
- Safety: `draft/autoPublish=false/dryRun=true`, media `UPLOAD_REQUIRED`
- Report: `.../metricool_dry_run/publish_safety_report.md`
- Live Metricool API post: **not authorized**
- Offline commit: `94f5860986` on `agent/social-media-voice-bank-video-wire-20260719`

## CosyVoice residual (blocked)

- Bank frozen at **1501 ok / 119 fail** — CosyVoice on Pearl Star flaps (health 200 then dies; startup `NOTIMPLEMENTED` / SIGKILL under load).
- Residual fails remain **fail-closed / excluded from video**.
- Re-open bank finish only when CosyVoice holds health 200 for ≥5 minutes without restart thrash.
