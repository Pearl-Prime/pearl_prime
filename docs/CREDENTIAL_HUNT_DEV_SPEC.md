# Credential Hunt Dev Spec

**Purpose:** Get every API key and token into BOTH macOS Keychain AND GitHub Secrets.
**Owner:** Any agent or dev
**Authority:** `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`
**Date:** 2026-04-03

---

## Current State

| Status | Count | Meaning |
|--------|-------|---------|
| ✅ Both | 2 | `QWEN_API_KEY`, `RUNCOMFY_API_KEY` |
| ⚠️ GitHub only | 17 | In CI but not local — agents can't use locally |
| ⚠️ Keychain only | 2 | `DASHSCOPE_API_KEY`, `ELEVENLABS_API_KEY` — need adding to GitHub |
| ❌ Missing both | 41 | Not set anywhere |

---

## Priority 1 — Copy GitHub Secrets to Keychain (17 keys)

These are already in GitHub Secrets but not locally. **Cannot read GitHub Secrets back** — must re-copy from each provider dashboard.

### 1A. Cloudflare (2 keys)

Dashboard: https://dash.cloudflare.com/ → Account → API Tokens

```bash
# After copying from dashboard:
security add-generic-password -U -s "phoenix-omega" -a "CLOUDFLARE_ACCOUNT_ID" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "CLOUDFLARE_API_TOKEN" -w "<paste>"
```

### 1B. Qwen config values (2 keys — NOT secrets, just config)

These are not secret — they're endpoint URLs and model names:

```bash
security add-generic-password -U -s "phoenix-omega" -a "QWEN_BASE_URL" -w "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
security add-generic-password -U -s "phoenix-omega" -a "QWEN_MODEL" -w "qwen-plus"
```

### 1C. WordPress (3 keys)

Dashboard: Your WordPress admin → Application Passwords

```bash
security add-generic-password -U -s "phoenix-omega" -a "WORDPRESS_SITE_URL" -w "<your-wordpress-url>"
security add-generic-password -U -s "phoenix-omega" -a "WORDPRESS_USERNAME" -w "<your-username>"
security add-generic-password -U -s "phoenix-omega" -a "WORDPRESS_APP_PASSWORD" -w "<paste>"
```

### 1D. YouTube SP + CC (6 keys)

Dashboard: https://console.cloud.google.com/apis/credentials
Two apps: Stillness Press (SP) and Cognitive Clarity (CC)

```bash
# Stillness Press
security add-generic-password -U -s "phoenix-omega" -a "YT_CLIENT_ID_SP" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "YT_CLIENT_SECRET_SP" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "YT_REFRESH_TOKEN_SP" -w "<paste>"
# Cognitive Clarity
security add-generic-password -U -s "phoenix-omega" -a "YT_CLIENT_ID_CC" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "YT_CLIENT_SECRET_CC" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "YT_REFRESH_TOKEN_CC" -w "<paste>"
```

### 1E. TikTok SP + CC (4 keys)

Dashboard: https://developers.tiktok.com/apps → Phoenix Video Publisher → App details

```bash
security add-generic-password -U -s "phoenix-omega" -a "TIKTOK_CLIENT_KEY_SP" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "TIKTOK_CLIENT_SECRET_SP" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "TIKTOK_CLIENT_KEY_CC" -w "<paste>"
security add-generic-password -U -s "phoenix-omega" -a "TIKTOK_CLIENT_SECRET_CC" -w "<paste>"
```

---

## Priority 2 — Copy Keychain to GitHub Secrets (2 keys)

These are local but not in GitHub Secrets.

### 2A. DASHSCOPE_API_KEY

Same value as QWEN_API_KEY. Go to GitHub Settings → Secrets → Actions → New:
- Name: `DASHSCOPE_API_KEY`
- Value: `sk-3404112742fa4bbc9250df92e4f7853f`

### 2B. ELEVENLABS_API_KEY

Go to GitHub Settings → Secrets → Actions → New:
- Name: `ELEVENLABS_API_KEY`
- Value: contents of `docs/11.txt` (or from Keychain: `security find-generic-password -s "phoenix-omega" -a "ELEVENLABS_API_KEY" -w`)

---

## Priority 3 — Hunt down missing keys (actionable subset)

Of the 41 missing keys, most are either blocked (need account setup) or optional. Here are the ones that matter:

### 3A. Anthropic — REQUIRED for Claude fallback LLM

Dashboard: https://console.anthropic.com/settings/keys (or https://platform.claude.com/settings/keys)
**Blocker:** Need to log in first.

```bash
security add-generic-password -U -s "phoenix-omega" -a "ANTHROPIC_API_KEY" -w "<paste>"
# Also add to GitHub Secrets
```

### 3B. RunComfy deployment ID — config value, not secret

```bash
security add-generic-password -U -s "phoenix-omega" -a "RUNCOMFY_DEPLOYMENT_ID" -w "677edba8-ace0-4b2b-bad2-8e94b9959065"
```

### 3C. Instagram access tokens (SP, CC) — BLOCKED on phone reset

Dashboard: Meta Graph API Explorer (need Instagram Business Account linked to Facebook Page)
**Blocker:** Instagram password reset via phone required first.

### 3D. TikTok access tokens (SP, CC) — BLOCKED on app review

Dashboard: https://developers.tiktok.com/apps → need app approved first
**Blocker:** TikTok app is in Draft, needs icon + Terms/Privacy URLs + review.

### 3E. NorCal Dharma brand (ND) — all platforms — NOT SET UP

YouTube, TikTok, Instagram for the ND brand have no credentials anywhere.
**Blocker:** Need to create OAuth apps for the 3rd brand.

---

## Priority 4 — Optional / deferred

| Key | Why deferred |
|-----|-------------|
| `BILIBILI_*` | Platform disabled (no zh content for EN brands) |
| `DOUYIN_*` | Blocked — needs Chinese ICP entity |
| `GHL_*` | GoHighLevel CRM — not active yet |
| `SMTP_*` | Funnel email — not active yet |
| `GA4_MEASUREMENT_ID` | Funnel analytics — not active yet |
| `SERPAPI_KEY` | Trend checking — optional, budget-guarded |
| `OPENAI_API_KEY` | Optional fallback — Qwen is primary |
| `OLLAMA_*` | Local LLM — config only, no key needed |
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions — never store locally |
| `GITHUB_REPOSITORY` | Auto-provided by GitHub Actions |
| `CLAUDE_MODEL` | Config value — set when Anthropic key is obtained |
| `DASHSCOPE_BASE_URL` | Same as QWEN_BASE_URL |
| `DASHSCOPE_MODEL` | Same as QWEN_MODEL |
| `FROM_EMAIL` / `FROM_NAME` | SMTP config — set when SMTP is active |
| `CLOUDFLARE_AI_API_TOKEN` | Separate from Pages token — for Workers AI image gen (demoted to fallback) |

---

## Execution Order

1. **Immediate (no browser needed):**
   - 1B: Qwen config values (just strings, no dashboard visit)
   - 3B: RunComfy deployment ID (just a string)
   - 2A: DASHSCOPE_API_KEY to GitHub (value known)
   - 2B: ELEVENLABS_API_KEY to GitHub (value known)

2. **Browser needed (visit dashboards, copy keys):**
   - 1A: Cloudflare dashboard
   - 1C: WordPress dashboard
   - 1D: Google Cloud console (YouTube)
   - 1E: TikTok developer portal
   - 3A: Anthropic console (need to log in)

3. **Blocked (need external action first):**
   - 3C: Instagram (phone reset)
   - 3D: TikTok access tokens (app review)
   - 3E: NorCal Dharma brand setup

---

## Verification

After each key is stored, run:

```bash
# Load all keys from Keychain
for key in QWEN_API_KEY DASHSCOPE_API_KEY RUNCOMFY_API_KEY ELEVENLABS_API_KEY CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD YT_CLIENT_ID_SP YT_CLIENT_SECRET_SP YT_REFRESH_TOKEN_SP YT_CLIENT_ID_CC YT_CLIENT_SECRET_CC YT_REFRESH_TOKEN_CC TIKTOK_CLIENT_KEY_SP TIKTOK_CLIENT_SECRET_SP TIKTOK_CLIENT_KEY_CC TIKTOK_CLIENT_SECRET_CC ANTHROPIC_API_KEY QWEN_BASE_URL QWEN_MODEL RUNCOMFY_DEPLOYMENT_ID; do
  val=$(security find-generic-password -s "phoenix-omega" -a "$key" -w 2>/dev/null)
  if [ -n "$val" ]; then echo "✅ $key"; else echo "❌ $key"; fi
done

# Full check
PYTHONPATH=. python3 scripts/ci/check_integration_env.py
```

---

## Acceptance Criteria

- [ ] All Priority 1 keys (17) in Keychain
- [ ] All Priority 2 keys (2) in GitHub Secrets
- [ ] Priority 3A (Anthropic) in both
- [ ] Verification script shows 0 required keys missing
- [ ] `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` status column updated for each key
