# Session handoff — 2026-04-09 — Therapeutic video pipeline (real plan run)

**Project:** `proj_state_convergence_20260328`  
**Subsystem:** `video_pipeline`

## Reproducible command

```bash
python3 scripts/video/run_pipeline.py \
  --plan-id plan-ahjan-anxiety-001 \
  --fixtures-dir artifacts/pipeline_examples/ahjan \
  --assets-dir brand-wizard-app/public/assets/image_bank \
  --format mid \
  --channel-id ch_001 \
  --no-skip-render \
  --quality draft \
  --force
```

Optional music bed: add `--music-bank`. Narration: `--voice` (requires Piper/CosyVoice2 per doc below).

## Evidence paths

| Artifact | Path |
|----------|------|
| Master (typ.) | `artifacts/video/plan-ahjan-anxiety-001/plan-ahjan-anxiety-001.mp4` |
| Timeline duration | `artifacts/video/plan-ahjan-anxiety-001/timeline.json` → `duration_s` |
| Render meta | `artifacts/video/plan-ahjan-anxiety-001/timeline_ref.json` |
| Plan QC | `artifacts/video/plan-ahjan-anxiety-001/qc_summary.json` |
| Image bank | `brand-wizard-app/public/assets/image_bank/` |

## Voice lane (merged)

**PR #313** — 480 narrator assignments, ECAPA artifact, verification report. Cross-links: `config/tts/narrator_voice_assignments.yaml`, `artifacts/tts/voice_assignment_verification_report.md`. Libri stand-ins in `assets/tts/reference_clips/` (gitignored locally) until locale-native clips replace them.

## Doc pointer

See [VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md](./VIDEO_NARRATION_CJK_AND_AMBIENT_WIRING.md) for CJK vs English routing and soundtrack mix.
