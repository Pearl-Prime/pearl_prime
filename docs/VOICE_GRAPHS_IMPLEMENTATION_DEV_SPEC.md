# Voice Graphs Implementation Dev Spec

**Owner:** Pearl_Architect
**Date:** 2026-04-02
**Audience:** External developer NOT on this branch
**Status:** Implementation-ready handoff

---

## 1. Objective + Audience

This spec hands off four workstreams to a developer who has never touched this repo. Each workstream has exact file paths, exact commands, and pass/fail criteria.

**Success criteria:** All four workstreams completed; all verification checks in Section 8 pass.

**Out of scope:**

- Actual ElevenLabs API billing decisions
- ComfyUI workflow authoring
- Pearl Prime V4 format changes
- Any changes to the brand wizard React app (`BrandWizard.jsx`)

---

## 2. Current-State Baseline

### 2.1 DOCS_INDEX copies

| Copy | Path |
|------|------|
| Main worktree | `docs/DOCS_INDEX.md` |
| Eloquent-wozniak worktree | `.claude/worktrees/eloquent-wozniak/docs/DOCS_INDEX.md` |
| Tender-nightingale worktree | `.claude/worktrees/tender-nightingale/docs/DOCS_INDEX.md` |

**Current diff status (2026-04-02):** All three copies are byte-identical. No reconciliation is needed at this moment, but drift can recur on any worktree commit.

### 2.2 Key rows present in all copies

| Row label | Present | Notes |
|-----------|---------|-------|
| `START HERE -- Integration credentials (canonical)` | Yes | Includes `--json` object-shape note (`summary`, `items`, `env_vars_tracked`, `registry_doc`) |
| `Find all integration credentials (canonical registry)` | Yes | Points to same registry; same `--json` shape note |
| `Brand briefing narration (TTS / SSML / ElevenLabs)` | Yes | Points to spec, script, config README, and Pages audio URL |

### 2.3 Session context

- PR #245 deleted ~20K files (accident)
- PR #252 restored them
- `image_generation/` restored separately
- Branch consolidation complete (PR #146): `main` is the only active remote branch

### 2.4 Canonical source files

| Asset | Path | Exists |
|-------|------|--------|
| TTS spec | `specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md` | Yes |
| Generator script | `scripts/onboarding/generate_briefing_narration.py` | Yes |
| ElevenLabs YAML config | `config/onboarding/tts/ahjan_elevenlabs.yaml` | Yes |
| Narration fixture | `config/onboarding/tts/briefing_narration_fixture.json` | Yes |
| TTS config README | `config/onboarding/tts/README.md` | Yes |
| Integration credentials registry | `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` | Yes |
| Env checker script | `scripts/ci/check_integration_env.py` | Yes |
| Public audio dir | `brand-wizard-app/public/onboarding/audio/` | Yes (contains briefing MP3s + voice bench clips) |
| Voice graphs manifest | `artifacts/voice_graphs/` | **Does not exist** |
| Voice graphs HTML | `brand-wizard-app/public/voice_graphs.html` | **Does not exist** |
| ElevenLabs key fallback | `11.txt` or `docs/11.txt` | **Not found** (gitignored; must be created locally) |

---

## 3. Workstream A -- DOCS_INDEX Reconciliation

### 3.1 Objective

Keep all three DOCS_INDEX copies aligned. Currently identical; this workstream prevents drift.

### 3.2 Rows to audit

After any edit to any copy, verify these rows are identical across all three:

| Row key | Expected content |
|---------|-----------------|
| `START HERE -- Integration credentials (canonical)` | Links to `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`; includes `--json` object shape note: `summary`, `items`, `env_vars_tracked`, `registry_doc` |
| `Find all integration credentials (canonical registry)` | Same link; same `--json` shape note; mentions `check_integration_env.py` |
| `Brand briefing narration (TTS / SSML / ElevenLabs)` | Links to spec, script, config README; mentions `/onboarding/briefing_audio.html` on Pages |

### 3.3 Reconciliation procedure

```bash
# From repo root:
MAIN=docs/DOCS_INDEX.md
EW=.claude/worktrees/eloquent-wozniak/docs/DOCS_INDEX.md
TN=.claude/worktrees/tender-nightingale/docs/DOCS_INDEX.md

diff "$MAIN" "$EW"
diff "$MAIN" "$TN"
```

**Pass:** Both diffs produce zero output.
**Fail:** Any diff output. Fix by copying the main copy to the divergent worktree(s):

```bash
cp "$MAIN" "$EW"
cp "$MAIN" "$TN"
```

---

## 4. Workstream B -- TTS Briefing Pipeline

### 4.1 Source-of-truth files

| File | Role |
|------|------|
| `specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md` | Contract / spec |
| `config/onboarding/tts/ahjan_elevenlabs.yaml` | Voice profile config (base, clamps, slider deltas, category deltas) |
| `config/onboarding/tts/briefing_narration_fixture.json` | 15 narration steps, wizard-aligned copy |
| `scripts/onboarding/generate_briefing_narration.py` | Generator (SSML + ElevenLabs API + offline demo) |

### 4.2 Credential lookup order

The generator script resolves `ELEVENLABS_API_KEY` in this order:

1. `ELEVENLABS_API_KEY` environment variable (shell)
2. Repo root `.env` file (KEY=value lines, does not override existing env)
3. `11.txt` (repo root) -- KEY=value lines or bare `sk_*` token
4. `docs/11.txt` -- same format
5. `11.txt.example` -- same format

Voice IDs resolve via:

1. `ELEVENLABS_VOICE_ID_MALE` / `ELEVENLABS_VOICE_ID_FEMALE` env vars
2. `voices.male_id` / `voices.female_id` in `ahjan_elevenlabs.yaml`

### 4.3 Commands

**Dry-run (no API key needed):**

```bash
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --dry-run
```

**Pass:** Exit code 0; files created:
- `artifacts/onboarding_audio/briefing_ssml.xml`
- `artifacts/onboarding_audio/briefing_segment_profiles.json`
- `artifacts/onboarding_audio/briefing_voice_profile.json`

**Live run (ElevenLabs):**

```bash
# Load all keys from Keychain first (see CLAUDE.md § "Load all keys locally")
for key in QWEN_API_KEY DASHSCOPE_API_KEY RUNCOMFY_API_KEY ELEVENLABS_API_KEY ANTHROPIC_API_KEY DEEPSEEK_API_KEY CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN CLOUDFLARE_AI_API_TOKEN WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD YT_CLIENT_ID_SP YT_CLIENT_SECRET_SP YT_CLIENT_ID_CC YT_CLIENT_SECRET_CC TIKTOK_CLIENT_KEY_SP TIKTOK_CLIENT_SECRET_SP TIKTOK_CLIENT_KEY_CC TIKTOK_CLIENT_SECRET_CC QWEN_BASE_URL QWEN_MODEL RUNCOMFY_DEPLOYMENT_ID META_APP_ID META_APP_SECRET SLACK_BOT_TOKEN SLACK_SIGNING_SECRET TELEGRAM_BOT_TOKEN DISCORD_BOT_TOKEN GITHUB_PAT; do
  val=$(security find-generic-password -s "phoenix-omega" -a "$key" -w 2>/dev/null)
  [ -n "$val" ] && export $key="$val"
done
# Voice IDs not in Keychain yet — set manually:
export ELEVENLABS_VOICE_ID_MALE="..."
export ELEVENLABS_VOICE_ID_FEMALE="..."
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --publish-public
```

**Pass:** Exit code 0; additional files:
- `artifacts/onboarding_audio/briefing_ahjan_male.mp3`
- `artifacts/onboarding_audio/briefing_ahjan_female.mp3`
- `artifacts/onboarding_audio/segments/ahjan_male_*.mp3` (15 segments)
- `artifacts/onboarding_audio/segments/ahjan_female_*.mp3` (15 segments)
- `brand-wizard-app/public/onboarding/audio/briefing_ahjan_male.mp3` (published copy)
- `brand-wizard-app/public/onboarding/audio/briefing_ahjan_female.mp3` (published copy)

**Offline demo (macOS only, no API key):**

```bash
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --offline-demo
```

Requires `say` and `ffmpeg` on PATH. Uses macOS Daniel/Samantha voices.

### 4.4 Pages verification

```bash
curl -s -o /dev/null -w "%{http_code}" https://brand-admin-onboarding.pages.dev/onboarding/briefing_audio.html
```

**Pass:** HTTP 200.
**Fail:** 404 means the Pages deploy has not run or the file is missing from `brand-wizard-app/public/onboarding/`.

---

## 5. Workstream C -- Voice Graphs Demo (20 clips)

### 5.1 Concept

Single male voice, 4 emotional categories, 5 delivery positions each = 20 clips total.

| Category | Positions (1-5) | Default |
|----------|-----------------|---------|
| comfort | 1 (whisper) to 5 (full) | 3 |
| authority | 1 (soft) to 5 (commanding) | 3 |
| cta | 1 (gentle) to 5 (urgent) | 3 |
| hope | 1 (quiet) to 5 (radiant) | 3 |

One sentence per clip. One shared audio player on the demo page. Default position is 3 for all categories.

### 5.2 Required artifacts (all must be created)

| Artifact | Path | Purpose |
|----------|------|---------|
| Canonical manifest | `config/onboarding/tts/voice_graphs_manifest.json` | Source of truth: 20 entries with category, position, sentence, voice settings |
| Public manifest copy | `brand-wizard-app/public/onboarding/voice_graphs_manifest.json` | Runtime fetch by HTML page |
| Generator script | `scripts/onboarding/generate_voice_graphs.py` | Reads manifest, calls ElevenLabs, writes MP3s |
| Static demo page | `brand-wizard-app/public/voice_graphs.html` | 4 category sections, per-category playback, one shared `<audio>` player |
| Public MP3 layout | `brand-wizard-app/public/onboarding/audio/voice_graphs/` | 20 files: `{category}_{position}.mp3` (e.g., `comfort_3.mp3`) |

### 5.3 Manifest schema

```json
{
  "version": "1.0",
  "voice_id_env": "ELEVENLABS_VOICE_ID_MALE",
  "model_id": "eleven_multilingual_v2",
  "categories": [
    {
      "id": "comfort",
      "label": "Comfort",
      "positions": [
        {
          "position": 1,
          "sentence": "You are safe here.",
          "voice_settings": {
            "stability": 0.65,
            "similarity_boost": 0.80,
            "style": 0.05,
            "use_speaker_boost": true
          }
        }
      ]
    }
  ]
}
```

### 5.4 SSML compatibility

ElevenLabs `eleven_multilingual_v2` may reject `<emphasis>` tags. If API returns 422 on SSML input:

1. Strip `<emphasis>` tags, keep inner text
2. Retry with plain text + `voice_settings` only
3. Log which segments needed fallback

The existing `generate_briefing_narration.py` already implements this pattern (tries SSML, falls back to plain text on error). Reuse that approach.

### 5.5 Runtime behavior (HTML page)

- Default: position 3 selected for all categories on page load
- Click any position button: plays that clip, highlights button
- One shared `<audio>` element (not 20 players)
- Fetch manifest from `onboarding/voice_graphs_manifest.json` on load
- MP3 paths: `onboarding/audio/voice_graphs/{category}_{position}.mp3`

### 5.6 Generation commands

```bash
# Dry-run (creates manifest, no audio)
PYTHONPATH=. python3 scripts/onboarding/generate_voice_graphs.py --dry-run

# Load all keys from Keychain (see CLAUDE.md), then:
for key in QWEN_API_KEY DASHSCOPE_API_KEY RUNCOMFY_API_KEY ELEVENLABS_API_KEY ANTHROPIC_API_KEY DEEPSEEK_API_KEY CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN CLOUDFLARE_AI_API_TOKEN WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD YT_CLIENT_ID_SP YT_CLIENT_SECRET_SP YT_CLIENT_ID_CC YT_CLIENT_SECRET_CC TIKTOK_CLIENT_KEY_SP TIKTOK_CLIENT_SECRET_SP TIKTOK_CLIENT_KEY_CC TIKTOK_CLIENT_SECRET_CC QWEN_BASE_URL QWEN_MODEL RUNCOMFY_DEPLOYMENT_ID META_APP_ID META_APP_SECRET SLACK_BOT_TOKEN SLACK_SIGNING_SECRET TELEGRAM_BOT_TOKEN DISCORD_BOT_TOKEN GITHUB_PAT; do
  val=$(security find-generic-password -s "phoenix-omega" -a "$key" -w 2>/dev/null)
  [ -n "$val" ] && export $key="$val"
done
export ELEVENLABS_VOICE_ID_MALE="..."  # not in Keychain yet
PYTHONPATH=. python3 scripts/onboarding/generate_voice_graphs.py
```

**Pass (dry-run):** Manifest written to `config/onboarding/tts/voice_graphs_manifest.json`.
**Pass (live):** 20 MP3 files in `brand-wizard-app/public/onboarding/audio/voice_graphs/`.

### 5.7 Verification

```bash
ls brand-wizard-app/public/onboarding/audio/voice_graphs/*.mp3 | wc -l
# Pass: 20

ls brand-wizard-app/public/voice_graphs.html
# Pass: file exists

python3 -c "
import json, pathlib
m = json.loads(pathlib.Path('config/onboarding/tts/voice_graphs_manifest.json').read_text())
cats = m['categories']
total = sum(len(c['positions']) for c in cats)
assert total == 20, f'Expected 20, got {total}'
print(f'Manifest OK: {len(cats)} categories, {total} clips')
"
```

---

## 6. Workstream D -- GitHub Secret Wiring (DashScope)

### 6.1 Key naming

| Priority | Secret name | Notes |
|----------|-------------|-------|
| Preferred | `DASHSCOPE_API_KEY` | All workflows read this first |
| Fallback | `QWEN_API_KEY` | Legacy; same key value |

### 6.2 Workflow files referencing DASHSCOPE_API_KEY or QWEN_API_KEY

| Workflow file | Pattern used |
|---------------|-------------|
| `catalog-book-pipeline.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |
| `marketing_continuous.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |
| `generate-and-translate-atoms.yml` | `${{ secrets.QWEN_API_KEY }}` (no fallback -- should be updated) |
| `research-pipeline-run.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |
| `max-quality-catalog.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |
| `pearl-news-fill-qwen.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |
| `marketing-briefs-and-proposals.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |
| `translate-bestseller-atoms.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |
| `translate-atoms-qwen-matrix.yml` | `${{ secrets.DASHSCOPE_API_KEY \|\| secrets.QWEN_API_KEY }}` |

### 6.3 Env mapping in workflows

Standard pattern (already in most files):

```yaml
env:
  QWEN_API_KEY: ${{ secrets.DASHSCOPE_API_KEY || secrets.QWEN_API_KEY }}
  QWEN_BASE_URL: ${{ secrets.QWEN_BASE_URL }}
  DASHSCOPE_API_KEY: ${{ secrets.DASHSCOPE_API_KEY || secrets.QWEN_API_KEY }}
```

**Exception:** `generate-and-translate-atoms.yml` uses `${{ secrets.QWEN_API_KEY }}` only. Update it to match the standard pattern.

### 6.4 Required GitHub Secrets checklist

| Secret | Required | Notes |
|--------|----------|-------|
| `DASHSCOPE_API_KEY` | Yes | Preferred name for DashScope API key |
| `QWEN_API_KEY` | Fallback | Same value as DASHSCOPE_API_KEY; kept for legacy workflows |
| `QWEN_BASE_URL` | Yes | DashScope endpoint URL |
| `QWEN_MODEL` | Optional | Model name (e.g., `qwen-max`); most scripts have defaults |
| `CLOUDFLARE_API_TOKEN` | Yes (Pages) | Used by `brand-admin-onboarding-pages.yml` |
| `CLOUDFLARE_ACCOUNT_ID` | Yes (Pages) | Used by `brand-admin-onboarding-pages.yml` |

### 6.5 Validation

```bash
PYTHONPATH=. python3 scripts/ci/check_integration_env.py --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
s = d['summary']
print(f'Set: {s[\"set\"]}/{s[\"total\"]}')
req = [i for i in d['items'] if i['required'] and not i['set']]
if req:
    print('FAIL: required vars missing:')
    for r in req:
        print(f'  {r[\"env_var\"]} ({r[\"service\"]})')
    sys.exit(1)
else:
    print('PASS: all required vars set')
"
```

**Pass:** Exit code 0, all required vars set.
**Fail:** Exit code 1, lists missing required vars.

---

## 7. Execution Order for External Dev

1. **Sync DOCS_INDEX** -- Run Workstream A diff check. If copies diverge, copy main to worktrees.
2. **Wire/validate secrets** -- Add `DASHSCOPE_API_KEY` to GitHub Secrets (Settings > Secrets and variables > Actions). Fix `generate-and-translate-atoms.yml` to use the standard fallback pattern. Run validation (Section 6.5).
3. **Generate TTS briefing assets** -- Run dry-run first (Section 4.3), then live with ElevenLabs key. Verify output files exist.
4. **Create voice graphs assets** -- Write manifest, generator script, and HTML demo page (Section 5). Generate 20 clips. Verify file count.
5. **Update public/static pages** -- Ensure `voice_graphs.html` is in `brand-wizard-app/public/`. Copy voice graphs manifest to public dir. Add nav link if applicable.
6. **Run full verification suite** -- Execute Section 8 checklist end-to-end.

---

## 8. Verification Checklist (copy-paste runnable)

```bash
#!/usr/bin/env bash
set -e
echo "=== File existence checks ==="

# This spec
ls docs/VOICE_GRAPHS_IMPLEMENTATION_DEV_SPEC.md && echo "PASS: dev spec" || echo "FAIL: dev spec"

# TTS pipeline
ls scripts/onboarding/generate_briefing_narration.py && echo "PASS: briefing generator" || echo "FAIL: briefing generator"
ls config/onboarding/tts/ahjan_elevenlabs.yaml && echo "PASS: elevenlabs yaml" || echo "FAIL: elevenlabs yaml"
ls config/onboarding/tts/briefing_narration_fixture.json && echo "PASS: fixture json" || echo "FAIL: fixture json"
ls specs/BRAND_ADMIN_ONBOARDING_TTS_SPEC.md && echo "PASS: tts spec" || echo "FAIL: tts spec"

# Voice graphs (created by this workstream)
ls config/onboarding/tts/voice_graphs_manifest.json && echo "PASS: voice graphs manifest" || echo "FAIL: voice graphs manifest (must be created)"
ls scripts/onboarding/generate_voice_graphs.py && echo "PASS: voice graphs generator" || echo "FAIL: voice graphs generator (must be created)"
ls brand-wizard-app/public/voice_graphs.html && echo "PASS: voice graphs html" || echo "FAIL: voice graphs html (must be created)"

# Integration env
ls scripts/ci/check_integration_env.py && echo "PASS: env checker" || echo "FAIL: env checker"
ls docs/INTEGRATION_CREDENTIALS_REGISTRY.md && echo "PASS: credentials registry" || echo "FAIL: credentials registry"

echo ""
echo "=== DOCS_INDEX alignment ==="
diff docs/DOCS_INDEX.md .claude/worktrees/eloquent-wozniak/docs/DOCS_INDEX.md > /dev/null 2>&1 && echo "PASS: main == eloquent-wozniak" || echo "FAIL: DOCS_INDEX drift (eloquent-wozniak)"
diff docs/DOCS_INDEX.md .claude/worktrees/tender-nightingale/docs/DOCS_INDEX.md > /dev/null 2>&1 && echo "PASS: main == tender-nightingale" || echo "FAIL: DOCS_INDEX drift (tender-nightingale)"

echo ""
echo "=== Workflow secret wiring ==="
grep -r "DASHSCOPE_API_KEY\|QWEN_API_KEY" .github/workflows/ | grep -c "secrets\." && echo "(workflow references found)"

echo ""
echo "=== Integration env check ==="
PYTHONPATH=. python3 scripts/ci/check_integration_env.py --json 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
s = d['summary']
print(f'Env vars: {s[\"set\"]}/{s[\"total\"]} set')
req = [i for i in d['items'] if i['required'] and not i['set']]
if req:
    print('FAIL: required vars missing:')
    for r in req:
        print(f'  {r[\"env_var\"]}')
else:
    print('PASS: all required vars set')
" || echo "WARN: env checker failed (expected if not in configured shell)"

echo ""
echo "=== Dry-run TTS briefing ==="
PYTHONPATH=. python3 scripts/onboarding/generate_briefing_narration.py --dry-run && echo "PASS: dry-run" || echo "FAIL: dry-run"
ls artifacts/onboarding_audio/briefing_ssml.xml > /dev/null 2>&1 && echo "PASS: ssml output" || echo "FAIL: ssml output"
ls artifacts/onboarding_audio/briefing_voice_profile.json > /dev/null 2>&1 && echo "PASS: voice profile" || echo "FAIL: voice profile"

echo ""
echo "=== Pages smoke test ==="
curl -s -o /dev/null -w "HTTP %{http_code}" https://brand-admin-onboarding.pages.dev/ && echo " PASS" || echo " FAIL"
curl -s -o /dev/null -w "HTTP %{http_code}" https://brand-admin-onboarding.pages.dev/onboarding/briefing_audio.html && echo " (briefing audio page)" || true
```

---

## 9. Handoff / Closeout

### 9.1 Expected deliverables

| # | Deliverable | Workstream |
|---|-------------|------------|
| 1 | DOCS_INDEX aligned across 3 copies (zero diff) | A |
| 2 | `generate-and-translate-atoms.yml` updated to standard DASHSCOPE fallback pattern | D |
| 3 | `DASHSCOPE_API_KEY` added to GitHub Secrets | D |
| 4 | `artifacts/onboarding_audio/briefing_ssml.xml` + profile JSONs generated (dry-run) | B |
| 5 | Briefing MP3s generated (if ElevenLabs key available) | B |
| 6 | `config/onboarding/tts/voice_graphs_manifest.json` created | C |
| 7 | `scripts/onboarding/generate_voice_graphs.py` created | C |
| 8 | `brand-wizard-app/public/voice_graphs.html` created | C |
| 9 | 20 voice graph MP3s in `brand-wizard-app/public/onboarding/audio/voice_graphs/` | C |
| 10 | All Section 8 checks passing | All |

### 9.2 PR notes template

```
## Voice Graphs Implementation

### Changes
- [ ] DOCS_INDEX: verified aligned across main + 2 worktrees
- [ ] generate-and-translate-atoms.yml: DASHSCOPE_API_KEY fallback wiring
- [ ] Voice graphs manifest: config/onboarding/tts/voice_graphs_manifest.json
- [ ] Voice graphs generator: scripts/onboarding/generate_voice_graphs.py
- [ ] Voice graphs demo page: brand-wizard-app/public/voice_graphs.html
- [ ] Voice graphs MP3s: brand-wizard-app/public/onboarding/audio/voice_graphs/ (20 files)
- [ ] TTS briefing dry-run verified

### Verification
All checks in docs/VOICE_GRAPHS_IMPLEMENTATION_DEV_SPEC.md Section 8 pass.

### Dependencies
- ElevenLabs API key required for live audio generation
- DASHSCOPE_API_KEY must be set in GitHub Secrets for CI workflows
```

### 9.3 Rollback guidance

**If audio generation fails (ElevenLabs):**

1. All non-audio artifacts (SSML, profiles, manifest, HTML) are still valid
2. Run `--dry-run` to confirm pipeline logic is correct
3. Use `--offline-demo` on macOS for demo-quality audio without API
4. Audio files are gitignored; no rollback needed for MP3s

**If voice graphs page breaks the Pages deploy:**

1. Remove `brand-wizard-app/public/voice_graphs.html`
2. Remove `brand-wizard-app/public/onboarding/audio/voice_graphs/`
3. Redeploy; existing pages are unaffected

**If DOCS_INDEX drift causes merge conflicts:**

1. The main worktree copy is canonical
2. `cp docs/DOCS_INDEX.md .claude/worktrees/<name>/docs/DOCS_INDEX.md`
3. Worktree copies are not deployed; they exist only for agent context
