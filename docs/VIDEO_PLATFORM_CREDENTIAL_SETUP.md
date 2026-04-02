# Video Platform Credential Setup Guide

**Authority:** `specs/VIDEO_CONTENT_ENGINE_DEV_SPEC.md` §Stage-18
**Config:** `config/video/upload_config.yaml`
**Scripts:** `scripts/video/credential_setup/`

## Quick Start (2-brand setup)

```bash
# 1. Copy and fill the manifest
cp scripts/video/credential_setup/credentials_manifest.yaml.example credentials_manifest.yaml
# Edit credentials_manifest.yaml with your platform credentials

# 2. Run OAuth flows for each platform (opens browser per brand)
python scripts/video/credential_setup/youtube_oauth.py \
  --manifest credentials_manifest.yaml --output .credentials.env

python scripts/video/credential_setup/tiktok_oauth.py \
  --manifest credentials_manifest.yaml --output .credentials.env

python scripts/video/credential_setup/instagram_oauth.py \
  --manifest credentials_manifest.yaml --output .credentials.env

# 3. Wire all credentials to GitHub Secrets
python scripts/video/credential_setup/wire_secrets.py --env-file .credentials.env

# 4. Verify
python scripts/video/credential_setup/wire_secrets.py --verify

# 5. Clean up (CRITICAL — never leave credential files on disk)
rm .credentials.env credentials_manifest.yaml
```

## Scaling to N Brands

The system is designed to scale to any number of brands. Each brand gets a credential suffix (e.g., `_SP`, `_CC`, `_ND`) appended to all secret names. To add a new brand:

1. Add the brand entry to `credentials_manifest.yaml`
2. Add the brand to `config/video/upload_config.yaml` → `brand_platform_map`
3. Re-run the OAuth scripts with `--manifest` (they process new brands only)
4. Re-run `wire_secrets.py` (it skips already-set secrets unless `--overwrite`)

---

## Per-Platform Setup Details

### YouTube (Google Cloud Console)

**One-time project setup** (done once for all brands):

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable **YouTube Data API v3** (API Library → search → Enable)
4. Configure OAuth consent screen:
   - App name: `Phoenix Video Publisher`
   - User type: External
   - Add all brand Google accounts as test users (Audience → Test users)
5. Create OAuth 2.0 Client:
   - Type: Web application
   - Authorized redirect URIs: `http://localhost:8095` (for the automation script)
   - Copy Client ID and Client Secret

**Per-brand token generation** (repeat for each brand):

```bash
# Single brand:
python scripts/video/credential_setup/youtube_oauth.py \
  --client-id <CLIENT_ID> --client-secret <CLIENT_SECRET> \
  --brand-suffix _SP --output .credentials.env

# Or batch via manifest:
python scripts/video/credential_setup/youtube_oauth.py \
  --manifest credentials_manifest.yaml --output .credentials.env
```

The script opens a browser. Sign in with the Google account that owns the brand's YouTube channel. The refresh token is captured automatically.

**Secrets per brand:** `YT_CLIENT_ID_{suffix}`, `YT_CLIENT_SECRET_{suffix}`, `YT_REFRESH_TOKEN_{suffix}`

**Token lifecycle:** Refresh tokens don't expire unless revoked. The uploader uses the refresh token to get short-lived access tokens at runtime.

**Adding test users for new brands:** Before a new Google account can authorize, add it as a test user in Google Cloud Console → Google Auth Platform → Audience → Test users. Alternatively, publish the app for production (requires Google verification).

---

### TikTok (TikTok Developer Portal)

**One-time app setup** (done once for all brands):

1. Go to [TikTok Developer Portal](https://developers.tiktok.com/)
2. Sign up / log in with a developer account
3. Create an app:
   - App name: `Phoenix Video Publisher`
   - Category: Content & Publishing
4. Add products: **Content Posting API** (Login Kit is included automatically)
5. Configure redirect URI: `http://localhost:8096`
6. Note the **Client Key** and **Client Secret** from app settings
7. Submit for review (TikTok requires app review for Content Posting API)

**Per-brand token generation:**

```bash
python scripts/video/credential_setup/tiktok_oauth.py \
  --client-key <CLIENT_KEY> --client-secret <CLIENT_SECRET> \
  --brand-suffix _SP --output .credentials.env
```

The script opens a browser. Log in with the TikTok account for this brand and approve access.

**Secrets per brand:** `TIKTOK_CLIENT_KEY_{suffix}`, `TIKTOK_CLIENT_SECRET_{suffix}`, `TIKTOK_ACCESS_TOKEN_{suffix}`

**Token lifecycle:** TikTok access tokens expire after ~24 hours. The app must use the refresh token flow to get new access tokens. For production, implement a token refresh cron job or refresh at upload time.

**Rate limits:** 20 video uploads per day per app. For 24 brands, consider separate TikTok developer apps or request elevated limits.

---

### Instagram Reels (Meta Developer Portal)

**One-time app setup** (done once for all brands):

1. Go to [Meta Developer Portal](https://developers.facebook.com/)
2. Create a new app (Type: Business)
3. Add product: **Instagram Graph API**
4. Configure OAuth redirect URI: `http://localhost:8097`
5. Note the **App ID** and **App Secret** from Settings → Basic
6. Each brand's Instagram account must be a Business or Creator account linked to a Facebook Page

**Per-brand token generation:**

```bash
python scripts/video/credential_setup/instagram_oauth.py \
  --app-id <APP_ID> --app-secret <APP_SECRET> \
  --brand-suffix _SP --output .credentials.env
```

The script opens a browser. Log in with the Facebook account that manages the brand's Instagram Business account.

**Secrets per brand:** `IG_ACCESS_TOKEN_{suffix}`, `IG_USER_ID_{suffix}`

**Token lifecycle:** Long-lived tokens last 60 days. Must be refreshed before expiry. The uploader can call the token refresh endpoint automatically. Set up a monthly cron job to refresh tokens.

**Requirements:** Each Instagram account must be a Business or Creator account, linked to a Facebook Page.

---

## Secret Naming Convention

All secrets follow the pattern: `{PLATFORM_KEY}{BRAND_SUFFIX}`

| Platform | Secret Keys | Per Brand |
|----------|------------|-----------|
| YouTube | `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | Yes (shared client, unique refresh token) |
| YouTube Shorts | Same as YouTube | Same |
| TikTok | `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN` | Yes |
| Instagram Reels | `IG_ACCESS_TOKEN`, `IG_USER_ID` | Yes |
| Bilibili | `BILI_SESSDATA`, `BILI_CSRF` | Yes |
| Douyin | `DOUYIN_CLIENT_KEY`, `DOUYIN_CLIENT_SECRET`, `DOUYIN_ACCESS_TOKEN` | Yes |

**Brand suffixes used in this repo:**
- `_SP` — Stillness Press
- `_CC` — Cognitive Clarity
- (Add `_ND`, `_B01`–`_B24`, etc. as needed)

## Verification

```bash
# Check which secrets are set:
python scripts/video/credential_setup/wire_secrets.py --verify

# Or directly:
gh secret list | grep -E "YT_|TIKTOK_|IG_|BILI_|DOUYIN_"
```

## Master Orchestration (Recommended)

Instead of running each platform script individually, use the master script:

```bash
# Full setup — all platforms, all brands from manifest:
bash scripts/video/credential_setup/setup_all_platforms.sh --manifest credentials_manifest.yaml

# Specific platforms only:
bash scripts/video/credential_setup/setup_all_platforms.sh --manifest credentials_manifest.yaml --platforms youtube,tiktok

# Dry run (see what would be wired without actually setting secrets):
bash scripts/video/credential_setup/setup_all_platforms.sh --manifest credentials_manifest.yaml --dry-run
```

The master script:
1. Reads the manifest for brand list and platform credentials
2. Runs each platform's OAuth script in sequence (opens browser per brand)
3. Collects all tokens into `.credentials.env`
4. Wires everything to GitHub Secrets via `gh secret set`
5. Runs verification to confirm all secrets are set

---

### Bilibili (Cookie-Based Auth)

Bilibili does not use OAuth. Auth is via browser cookies (SESSDATA + bili_jct CSRF token).

**Per-brand setup:**

```bash
python scripts/video/credential_setup/bilibili_setup.py --brand-suffix _SP --output .credentials.env
```

The script opens Bilibili's login page. After you log in:
1. Open DevTools (F12) → Application → Cookies → bilibili.com
2. Copy the `SESSDATA` value
3. Copy the `bili_jct` value
4. Paste each when the script prompts

**Secrets per brand:** `BILI_SESSDATA_{suffix}`, `BILI_CSRF_{suffix}`

**Token lifecycle:** Cookies expire periodically. Re-extract from browser when uploads fail with auth errors.

---

### Douyin (Douyin Open Platform)

Douyin is separate from TikTok — different API, accounts, and content review process.

**One-time app setup:**

1. Go to [Douyin Open Platform](https://open.douyin.com/)
2. Create an app and apply for `video.create` permission
3. Note the Client Key and Client Secret
4. ICP filing is required for production use

**Per-brand setup:**

```bash
python scripts/video/credential_setup/douyin_oauth.py \
  --client-key <KEY> --client-secret <SECRET> \
  --brand-suffix _SP --output .credentials.env
```

**Secrets per brand:** `DOUYIN_CLIENT_KEY_{suffix}`, `DOUYIN_CLIENT_SECRET_{suffix}`, `DOUYIN_ACCESS_TOKEN_{suffix}`

**Token lifecycle:** Access tokens expire. Content review takes 24-72 hours after upload.

---

## Security Rules

1. **Never commit credentials** — `.credentials.env`, `credentials_manifest.yaml` are gitignored
2. **Delete credential files** after wiring to GitHub Secrets
3. **Agent never types credentials** — human pastes, `gh secret set` reads from stdin
4. **Rotate tokens periodically** — re-run OAuth scripts and `wire_secrets.py --overwrite`
5. **Separate apps per platform** if rate limits are reached at scale
