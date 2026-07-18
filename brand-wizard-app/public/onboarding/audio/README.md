# Briefing MP3s (generated)

Place **`briefing_ahjan_male.mp3`** and **`briefing_ahjan_female.mp3`** here for
[`briefing_audio.html`](../briefing_audio.html) to play on Cloudflare Pages.

Generate + copy in one step (from repo root):

```bash
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --publish-public
# or offline (macOS say + ffmpeg):
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --offline-demo --publish-public
```

`*.mp3` in this folder may be gitignored; keep them locally or produce in CI with secrets before `npm run build`.
