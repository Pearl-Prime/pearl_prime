# Video narration (CJK + English), ambient bed, music bank

**Purpose:** How TTS and beds connect to `scripts/video/run_pipeline.py` → `run_render.py`.  
**Updated:** 2026-04-09

## Routing

| Locale | Engine | Config |
|--------|--------|--------|
| English | Piper (when installed) | `--voice`; must fail clearly if missing |
| CJK | CosyVoice2 `reference_id` | `config/tts/narrator_voice_assignments.yaml` |

480 author keys: `${teacher_id}__${brand_id}` from `config/authoring/pen_name_teacher_profiles_full.json`. See PR **#313** and `artifacts/tts/voice_assignment_verification_report.md`.

## Audio path

1. `run_soundtrack_engine.py` → `soundtrack_plan.json`  
2. `--music-bank` → `artifacts/video/<plan>/audio/soundtrack_plan_with_audio.json` with `music_path`  
3. `--voice` → narration WAVs + updated plan  
4. `run_render.py` → `_mix_audio_tracks()` when paths exist  

Use `assets/music_bank/` and `assets/sfx_bank/` via the soundtrack engine; avoid one-off manual FFmpeg except for debugging.

## Pacing configs

`config/video/pacing_by_content_type.yaml`, `music_policy.yaml`, `therapeutic_video_rules.yaml`, `caption_policies.yaml`.

## References

- [VIDEO_PIPELINE_SPEC.md](./VIDEO_PIPELINE_SPEC.md)  
- [SESSION_HANDOFF_2026_04_09_PRESENTATION.md](./SESSION_HANDOFF_2026_04_09_PRESENTATION.md)  
- [specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md](../specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md)  
