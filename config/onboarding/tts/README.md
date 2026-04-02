# Onboarding TTS config (`config/onboarding/tts/`)

- **`ahjan_elevenlabs.yaml`** — ElevenLabs model id, voice id resolution (env or inline), `VoiceProfile` base/clamps, slider → delta formulas, per-category baselines.
- **`briefing_narration_fixture.json`** — Ordered narration steps (wizard-aligned copy) plus optional `delta` / `sliders`.

**Run generator:** from repo root,

```bash
export ELEVENLABS_API_KEY=...
export ELEVENLABS_VOICE_ID_MALE=...   # first male voice in your ElevenLabs catalog
export ELEVENLABS_VOICE_ID_FEMALE=...
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py
```

Dry-run (no API key; writes SSML + profile only):

```bash
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --dry-run
```

See [specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md](../../specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md).
