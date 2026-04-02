# Onboarding briefing audio (generated)

Regenerate with:

```bash
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --dry-run
```

With ElevenLabs credentials and `ffmpeg` on PATH (for a single merged MP3 per gender):

```bash
export ELEVENLABS_API_KEY=...
export ELEVENLABS_VOICE_ID_MALE=...
export ELEVENLABS_VOICE_ID_FEMALE=...
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py
```

Outputs (see [specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md](../../specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md)):

- `briefing_ssml.xml` — full cumulative SSML
- `briefing_voice_profile.json` — final VoiceProfile
- `briefing_segment_profiles.json` — per-step profile audit
- `briefing_ahjan_male.mp3` / `briefing_ahjan_female.mp3` — merged when ffmpeg succeeds
- `segments/` — per-step MP3s (always written when API runs)

`.mp3` and `segments/` are gitignored.
