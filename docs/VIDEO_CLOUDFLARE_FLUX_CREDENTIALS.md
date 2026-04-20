# Cloudflare Workers AI credentials for video image generation

**Purpose:** How to get and use Cloudflare Account ID and API token for FLUX image generation (video image bank and master prompt QA).  
**Used by:** [scripts/video/run_flux_generate.py](../scripts/video/run_flux_generate.py). Same credentials can be used for author cover art T2I when that pipeline uses Workers AI.  
**Authority:** [docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md](./VIDEO_IMAGE_MASTER_PROMPT_SPEC.md), [docs/DOCS_INDEX.md](./DOCS_INDEX.md) § Video pipeline.

---

## What you need

| Variable | What it is | Not |
|----------|------------|-----|
| **CLOUDFLARE_ACCOUNT_ID** | A 32-character hexadecimal string Cloudflare assigns to your account (e.g. `a1b2c3d4e5f6789012345678abcdef01`). | Your login email (e.g. Ahjansamvara@gmail.com). |
| **CLOUDFLARE_API_TOKEN** | A long secret string from "Create Workers AI API Token" in the dashboard. Shown once; copy and store safely. | Your account password or email. |
| **CLOUDFLARE_AI_API_TOKEN** *(optional but recommended)* | A second token scoped only to **Workers AI – Read** and **Workers AI – Edit**. If set, image scripts use it **before** `CLOUDFLARE_API_TOKEN`, so a generic Cloudflare token (Pages, DNS, etc.) does not produce **401** on `.../ai/run/@cf/...`. | Same as API token row — must be Workers AI–scoped. |

---

## 1. Get Account ID and API token

1. **Log in:** [Cloudflare Dashboard](https://dash.cloudflare.com). Use email/password if social login fails (see [Troubleshooting](#troubleshooting) below).

2. **Open Workers AI:** Go to [Workers AI](https://dash.cloudflare.com/?to=/:account/ai/workers-ai) (or in the left sidebar: **AI** → **Workers AI**).

3. **Get Account ID:**
   - Click the **"REST API"** card (e.g. "Call Workers AI from any deployment using the REST API").
   - On the REST API page, **Account ID** is shown — copy it (32 hex characters).
   - Or: left sidebar → your account name (e.g. "YourEmail’s Account") or **Manage account**; Account ID is on that page.
   - Or: from the browser URL when on Workers AI: `dash.cloudflare.com/`**`xxxxxxxx...`**`/ai/workers-ai` — the hex segment is your Account ID.

4. **Create API token:**
   - On the same **Workers AI** / **REST API** page, click **"Create API Token"** or **"Create Workers AI API Token"**.
   - Confirm permissions (must include **Workers AI – Read** and **Workers AI – Edit**).
   - Click **Create API Token**, then **Copy** the token immediately (it is only shown once).

---

## 2. Where to put the credentials

Use **one** of the following. The script checks in this order: env vars → `.env` → key file.

### Option A: Key file at repo root (recommended for local use)

Create or edit a file at the **repo root** (same directory as this `docs/` folder’s parent):

**Filename:** `cloudflare_workers_ai.txt` or `11.txt`

**Format (one per line):**

```
CLOUDFLARE_ACCOUNT_ID=your_32_char_hex_account_id
CLOUDFLARE_API_TOKEN=your_long_api_token_string
```

- No spaces around `=`. No quotes unless the value contains spaces (then use straight quotes).
- Keep this file **out of version control** (add to `.gitignore` if needed).

### Option B: Environment variables (preferred — load all from Keychain)

All keys including Cloudflare are now in macOS Keychain. Load them all at once:

```bash
# Load all 30 keys from Keychain (see CLAUDE.md or docs/INTEGRATION_CREDENTIALS_REGISTRY.md)
for key in QWEN_API_KEY DASHSCOPE_API_KEY RUNCOMFY_API_KEY ELEVENLABS_API_KEY ANTHROPIC_API_KEY DEEPSEEK_API_KEY CLOUDFLARE_ACCOUNT_ID CLOUDFLARE_API_TOKEN CLOUDFLARE_AI_API_TOKEN WORDPRESS_SITE_URL WORDPRESS_USERNAME WORDPRESS_APP_PASSWORD YT_CLIENT_ID_SP YT_CLIENT_SECRET_SP YT_CLIENT_ID_CC YT_CLIENT_SECRET_CC TIKTOK_CLIENT_KEY_SP TIKTOK_CLIENT_SECRET_SP TIKTOK_CLIENT_KEY_CC TIKTOK_CLIENT_SECRET_CC QWEN_BASE_URL QWEN_MODEL RUNCOMFY_DEPLOYMENT_ID META_APP_ID META_APP_SECRET SLACK_BOT_TOKEN SLACK_SIGNING_SECRET TELEGRAM_BOT_TOKEN DISCORD_BOT_TOKEN GITHUB_PAT; do
  val=$(security find-generic-password -s "phoenix-omega" -a "$key" -w 2>/dev/null)
  [ -n "$val" ] && export $key="$val"
done
```

This sets `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`, and `CLOUDFLARE_AI_API_TOKEN` (Workers AI / FLUX Schnell).

### Option C: `.env` at repo root

Create a file `.env` at repo root with:

```
CLOUDFLARE_ACCOUNT_ID=your_32_char_hex_account_id
CLOUDFLARE_API_TOKEN=your_long_api_token_string
```

Requires `python-dotenv`; the script loads it automatically if present. Do not commit `.env`.

---

## 3. Run the image generator

From the repo root:

```bash
# Generate one image (anxiety palette, hands/tea scene), save to image_bank/master_prompt_test_anxiety.png
python3 scripts/video/run_flux_generate.py

# Dry-run: print prompt and negative block only (no API call)
python3 scripts/video/run_flux_generate.py --dry-run

# Custom scene, topic, output path
python3 scripts/video/run_flux_generate.py --scene "hands on a keyboard at a desk" --topic burnout --out image_bank/my_test.png
```

Output image path: `image_bank/master_prompt_test_<topic>.png` unless `--out` is set.

---

## 4. Related docs and config

| Item | Location |
|------|----------|
| Master prompt template & API summary | [docs/VIDEO_IMAGE_MASTER_PROMPT_SPEC.md](./VIDEO_IMAGE_MASTER_PROMPT_SPEC.md) |
| Palette & bands (brand_style_tokens) | [config/video/brand_style_tokens.yaml](../config/video/brand_style_tokens.yaml) |
| Negative prompts (no adoration, shared) | [config/video/prompt_constraints.yaml](../config/video/prompt_constraints.yaml) |
| Video color master system (palette reference) | [docs/video-color-master-system.html](./video-color-master-system.html) |
| FLUX/Shnell prompt research | [docs/flux_shnell_research.rtf](./flux_shnell_research.rtf) |
| Cloudflare REST API (official) | [Get started - REST API](https://developers.cloudflare.com/workers-ai/get-started/rest-api) |

---

## Troubleshooting

- **"Social login did not work" / "details do not match identity provider"**  
  Use **Sign up / Log in with email** (or another method) instead of Google/Apple. If the account already exists, use the email and password you used when you first signed up. If it still fails, use **Contact support** on the login page.

- **"Set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN"**  
  The script did not find credentials. Check: (1) key file is at repo root and named `cloudflare_workers_ai.txt` or `11.txt`; (2) lines start with `CLOUDFLARE_ACCOUNT_ID=` and `CLOUDFLARE_API_TOKEN=`; (3) no typos; (4) Account ID is the 32-char hex, not your email.

- **API returns 4xx/5xx**  
  Verify Account ID and token are correct, token has Workers AI Read+Edit, and the account has Workers AI enabled. Check [Cloudflare System status](https://www.cloudflarestatus.com/) if needed.
