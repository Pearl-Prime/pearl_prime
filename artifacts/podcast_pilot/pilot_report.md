# Podcast pilot — `stillness_press` / es-US / 2026-W15

**Inputs:** `artifacts/pipeline_examples/ahjan` (anxiety arc), formats `podcast_episode` + `podcast_short`.  
**Outputs:** `artifacts/podcast_pilot/podcast/` (MP3, `feed.xml`, `artwork.jpg`, `pipeline_report.json`). Large binaries are **not** tracked in git; re-run the pipeline locally to reproduce.

## Commands

```bash
python3 -m pip install -r requirements.txt
python3 scripts/podcast/run_podcast_pipeline.py \
  --brand-id stillness_press \
  --locale es-US \
  --week 2026-W15 \
  --book-dir artifacts/pipeline_examples/ahjan \
  --output-dir artifacts/podcast_pilot \
  --formats podcast_episode,podcast_short \
  --skip-upload
```

## Acceptance checklist

| Criterion | Result |
|-----------|--------|
| Episode duration 15–25 min | **Pass** (~20.0 min, ~1200 s) |
| Short duration 2–5 min | **Pass** (~4.75 min, 285 s) |
| Loudness −16 LUFS ±1 LU (EBU R128 integrated, `ffmpeg` `ebur128`) | **Pass** (episode **−16.7 LUFS**, short **−16.1 LUFS**) |
| RSS validates (`xmllint --noout feed.xml`) | **Pass** |
| Narrator routing es-US | **Pass** — `edge_fallback` **es-US-AlonsoNeural**, provider `edge_tts` via `locale_voice_routing.yaml` + non-English primary path in `scripts/podcast/_lib.py` |
| Music bed present | **Pass** — bank or lavfi bed under speech in segment mix |
| ID3 / metadata | **Pass** — FFmpeg `-metadata` + optional Mutagen EasyID3 when installed |
| Pipeline report | **Pass** — `podcast/pipeline_report.json`, render reports per MP3 |
| EI stealth (no clinical positioning in scripted micro-copy) | **Pass** (intro/outro uses educational framing; atom text is existing catalog content) |

## Notes

- **Optional full narrator row lookup:** set `PHOENIX_LOAD_NARRATOR_ASSIGNMENTS=1` to read `config/tts/narrator_voice_assignments.yaml` (large file; slow cold start).
- **Loudness:** encode uses `loudnorm` two-pass with empirical gain compensation so **post-encode** EBU `I` aligns with ~−16 LUFS after `libmp3lame` 128k mono.
- **R2:** uploads are skipped here; production uses `scripts/podcast/upload_podcast_to_r2.py` (permanent objects — no lifecycle deletion).
