# Onboarding TTS config (`config/onboarding/tts/`)

- **`ahjan_elevenlabs.yaml`** — ElevenLabs model id, voice id resolution (env or inline), `VoiceProfile` base/clamps, slider → delta formulas, per-category baselines.
- **`briefing_narration_fixture.json`** — Ordered narration steps (wizard-aligned copy) plus optional `delta` / `sliders`.

**Run generator:** from repo root,

```bash
# Load all keys from Keychain first (see CLAUDE.md or docs/INTEGRATION_CREDENTIALS_REGISTRY.md)
for key in QWEN_API_KEY DASHSCOPE_API_KEY RUNCOMFY_API_KEY ELEVENLABS_API_KEY ANTHROPIC_API_KEY DEEPSEEK_API_KEY CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN CLOUDFLARE_AI_API_TOKEN WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD YT_CLIENT_ID_SP YT_CLIENT_SECRET_SP YT_CLIENT_ID_CC YT_CLIENT_SECRET_CC TIKTOK_CLIENT_KEY_SP TIKTOK_CLIENT_SECRET_SP TIKTOK_CLIENT_KEY_CC TIKTOK_CLIENT_SECRET_CC QWEN_BASE_URL QWEN_MODEL RUNCOMFY_DEPLOYMENT_ID META_APP_ID META_APP_SECRET SLACK_BOT_TOKEN SLACK_SIGNING_SECRET TELEGRAM_BOT_TOKEN DISCORD_BOT_TOKEN GITHUB_PAT; do
  val=$(security find-generic-password -s "phoenix-omega" -a "$key" -w 2>/dev/null)
  [ -n "$val" ] && export $key="$val"
done

# TTS-specific (voice IDs not in Keychain yet)
export ELEVENLABS_VOICE_ID_MALE=...   # first male voice in your ElevenLabs catalog
export ELEVENLABS_VOICE_ID_FEMALE=...
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py
```

Dry-run (no API key; writes SSML + profile only):

```bash
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --dry-run
```

See [specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md](../../specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md).
