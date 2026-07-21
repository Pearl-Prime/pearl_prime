# Handoff — Social TTS plan pivot (gender-only + text prep)

**From:** Pearl_Research · **Date:** 2026-07-19 · **OPD:** OPD-SMV-02

## What changed

Operator listen rejected param-modulated CosyVoice personas. New plan:

- Stock `english_male` / `english_female` only (gender map in matrix v2)
- **No SSML**, no engine param modulation
- Quality via `config/tts/social_media_tts_text_prep.yaml` (punctuation + trap-word rewrites)

## Artifacts

| Path | Role |
|------|------|
| `artifacts/research/social_media_tts_text_prep_2026-07-19/REPORT.md` | Research + plan |
| `config/tts/social_media_tts_text_prep.yaml` | Machine text-prep rules |
| `config/tts/social_media_voice_matrix.yaml` | Gender-only map (v2) |
| `docs/VOICE_PERSONA_TOPIC_RESEARCH.md` §7.0 | Doctrine pivot note |

## VOID

~152 modulated bank rows from scale run under `social_media/voice_bank/20260719/` — do not ship.
Scale worker killed on pearlstar.

## Operator ratify (unblocks re-synth)

- **Q-SMV-G01:** corp=male, gen_z=female, RN=female? (or flip corp to female)
- **Q-SMV-G02:** punctuation aggressiveness medium OK?
- **Q-SMV-G03:** synth-input-only prep (SSOT untouched) OK?

Then restart Lane 2 with text_prep applied, R2 run id `20260719b`.
