"""Canonical list of integration environment variables for Phoenix Omega.

Single source of truth for:
- ``scripts/ci/check_integration_env.py`` (set vs missing in current shell)
- ``scripts/ci/load_integration_env_from_keychain.py`` (macOS Keychain → export lines)

Keep in sync with ``docs/INTEGRATION_CREDENTIALS_REGISTRY.md`` (human-facing docs).

Each entry: (service_name, env_var, required_bool, notes).
"""

from __future__ import annotations

# Canonical env var registry.
REGISTRY: list[tuple[str, str, bool, str]] = [
    # --- LLM Providers ---
    # --- Tier 2 LLM (Pearl Star Ollama — unattended scheduled work only) ---
    ("Pearl Star / Gemma", "GEMMA_BASE_URL", True, "Gemma Ollama endpoint (English Tier 2). Default: http://192.168.1.101:11434/v1"),
    ("Pearl Star / Gemma", "GEMMA_MODEL", False, "Gemma model override (default: gemma2:9b)"),
    ("Qwen / DashScope", "QWEN_BASE_URL", True, "Qwen Ollama endpoint (CJK6 Tier 2). Default: http://192.168.1.101:11434/v1"),
    ("Qwen / DashScope", "QWEN_MODEL", False, "Qwen model override (default: qwen2.5:7b)"),
    ("Qwen / DashScope", "QWEN_API_KEY", False, "DashScope API key (not needed for local Ollama)"),
    ("Qwen / DashScope", "DASHSCOPE_API_KEY", False, "Alt env var for DashScope key"),
    ("Qwen / DashScope", "DASHSCOPE_BASE_URL", False, "Alt env var for DashScope URL"),
    ("Qwen / DashScope", "DASHSCOPE_MODEL", False, "Alt env var for DashScope model"),
    # ANTHROPIC_API_KEY is BANNED from production code. Tier 1 = Claude Code session (subscription).
    # This entry is kept so load_integration_env_from_keychain.py doesn't emit an error if present.
    ("Anthropic", "ANTHROPIC_API_KEY", False, "NOT required for production — Tier 1 = Claude Code subscription"),
    ("Anthropic", "CLAUDE_MODEL", False, "Claude model selection (local dev reference only)"),
    ("OpenAI", "OPENAI_API_KEY", False, "OpenAI API key (TTS + fallback LLM)"),
    ("Ollama", "OLLAMA_HOST", False, "Local Ollama endpoint"),
    ("Ollama", "OLLAMA_MODEL", False, "Local Ollama model"),
    # --- CJK translation providers ---
    ("DeepSeek", "DEEPSEEK_API_KEY", False, "zh-CN/zh-TW translation — deepseek-chat (V3). Get: platform.deepseek.com/api_keys"),
    ("DeepSeek", "DEEPSEEK_MODEL", False, "DeepSeek model override (default: deepseek-chat)"),
    ("Google AI Studio", "GOOGLE_AI_API_KEY", False, "ja-JP translation — Gemini 2.0 Flash, 1M tokens/day free. Get: aistudio.google.com/apikey"),
    ("Google AI Studio", "GEMINI_MODEL", False, "Gemini model override (default: gemini-2.0-flash)"),
    # --- Free-tier LLM providers (EN / non-CJK article expansion) ---
    ("Groq", "GROQ_API_KEY", False, "Free EN default: llama-3.3-70b-versatile. Get: console.groq.com/keys"),
    ("xAI / Grok", "XAI_API_KEY", False, "Free EN fallback 1: grok-3-mini. $25/mo free credits. Get: console.x.ai"),
    ("Together AI", "TOGETHER_API_KEY", False, "Free EN fallback 2: Llama-3.3-70B-Instruct-Turbo-Free. 1M tokens/mo. Get: api.together.ai"),
    # --- Media / TTS ---
    ("ElevenLabs", "ELEVENLABS_API_KEY", False, "TTS (guided audio, journal prompts)"),
    # --- Infrastructure ---
    ("Cloudflare", "CLOUDFLARE_ACCOUNT_ID", False, "Workers AI + Pages"),
    ("Cloudflare", "CLOUDFLARE_API_TOKEN", False, "Cloudflare API token. cfut_ prefix = Workers Builds (IP-locked to Cloudflare CI; CANNOT do Pages from a developer laptop)"),
    ("Cloudflare", "CLOUDFLARE_API_TOKEN_PAGES", False, "Pages-scoped Custom token for local branch-preview deploys (must NOT have cfut_ prefix; create via dash.cloudflare.com/profile/api-tokens > Custom Token > Account:Cloudflare Pages:Edit, no IP filter)"),
    ("Cloudflare", "CLOUDFLARE_AI_API_TOKEN", False, "Workers AI inference token"),
    ("Cloudflare", "CLOUDFLARE_AI_BASE_URL", False, "Workers AI OpenAI-compat base URL (accounts/<ID>/ai/v1)"),
    ("Cloudflare", "CLOUDFLARE_AI_MODEL", False, "Workers AI model name (e.g. @cf/google/gemma-3-12b-it)"),
    ("Cloudflare R2", "R2_ACCESS_KEY_ID", False, "R2 S3-compatible access key (bucket-scoped to phoenix-omega-artifacts). Get: dash.cloudflare.com → R2 → Manage R2 API Tokens"),
    ("Cloudflare R2", "R2_SECRET_ACCESS_KEY", False, "R2 S3-compatible secret (shown once when access key created)"),
    ("Cloudflare R2", "R2_ACCOUNT_ID", False, "R2 account ID for S3 endpoint URL (same value as CLOUDFLARE_ACCOUNT_ID; scoped separately for r2_sync.py + setup_r2.sh consumers)"),
    ("Cloudflare R2", "R2_BUCKET", False, "R2 bucket name (default: phoenix-omega-artifacts)"),
    ("Cloudflare R2", "R2_ENDPOINT", False, "S3 endpoint URL override. Set this for EU-jurisdiction or non-default-jurisdiction buckets where the host is NOT https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com. Cloudflare shows the correct URL on the R2 → Manage R2 API Tokens result page."),
    # --- Pearl Prime Storefront (Cloudflare Pages + D1 + R2 + KV + Snipcart-wraps-Stripe) ---
    # Spec: docs/specs/PEARL_PRIME_STOREFRONT_V1_SPEC.md §5 + AMENDMENT-2026-06-04 (PR #1446)
    # Operator runbook + resource IDs: skills/pearl-int/references/storefront_resource_ids.md
    # Deploy: .github/workflows/pearl-prime-storefront-deploy.yml
    ("Pearl Prime Storefront", "CLOUDFLARE_API_TOKEN_PAGES_STOREFRONT", False, "Optional storefront-scoped Pages token. Default: REUSE existing CLOUDFLARE_API_TOKEN repo secret (already b80152c3-scoped). Only create this variant if you want the storefront workflow to fail-loud when writing to non-storefront Pages projects. See storefront_resource_ids.md §5."),
    ("Pearl Prime Storefront", "STOREFRONT_D1_ID", False, "Cloudflare D1 database ID for `pearl_prime_storefront`. Populated by operator after dashboard provisioning per storefront_resource_ids.md §2. Required before Pearl_Dev application code lands."),
    ("Pearl Prime Storefront", "STOREFRONT_R2_BUCKET", False, "Cloudflare R2 bucket name for storefront assets — default `pearl-prime-storefront-assets`. Bucket name IS the identifier (no separate UUID). en-US/ + ja-JP/ prefixes pre-allocated per spec §2.2 Phase A."),
    ("Pearl Prime Content", "PEARL_PRIME_CONTENT_R2_BUCKET", False, "R2 bucket for weekly marketing_feed.json (GHL). Default `pearl-prime-content`. Path: pearl-prime-content/{brand_id}/{locale}/{week}/marketing_feed.json"),
    ("Pearl Prime Content", "PEARL_PRIME_CONTENT_CDN_URL", False, "Public CDN base for GHL feed URLs, e.g. https://content.pearlprime.shop"),
    ("Pearl Prime Storefront", "STOREFRONT_KV_NAMESPACE_ID", False, "Cloudflare KV namespace ID for `pearl_prime_storefront_session_cart`. 60-minute TTL for anonymous browsing carts. Populated by operator per storefront_resource_ids.md §4."),
    ("Snipcart", "SNIPCART_API_KEY", False, "Snipcart secret API key — server-side only (Pages Functions / Worker). Free tier per AMENDMENT Q-PRP-PAY-01. Get: app.snipcart.com → API keys. Store in Keychain ONLY; never commit. See storefront_resource_ids.md §6."),
    ("Snipcart", "SNIPCART_PUBLIC_API_KEY", False, "Snipcart public API key — embedded in storefront HTML for the drop-in JS. Get: app.snipcart.com → API keys. Public-safe (rate-limited)."),
    ("Snipcart", "SNIPCART_WEBHOOK_SECRET", False, "Snipcart webhook signing secret — verifies inbound webhook payloads to `/api/webhook/snipcart`. Stored in Cloudflare Pages env var (encrypted) AND macOS Keychain. Quarterly rotation per docs/INTEGRATION_CREDENTIALS_REGISTRY.md."),
    ("GitHub", "GITHUB_TOKEN", False, "GitHub API (auto in Actions)"),
    ("GitHub", "GITHUB_REPOSITORY", False, "owner/repo for API calls; auto in Actions"),
    # --- Publishing ---
    ("WordPress", "WORDPRESS_SITE_URL", False, "Pearl News publishing"),
    ("WordPress", "WORDPRESS_USERNAME", False, "WordPress user"),
    ("WordPress", "WORDPRESS_APP_PASSWORD", False, "WordPress app password"),
    # --- Funnel ---
    ("GoHighLevel", "GHL_API_KEY", False, "Funnel CRM"),
    ("GoHighLevel", "GHL_LOCATION_ID", False, "GHL location"),
    ("GoHighLevel", "GHL_CONTACTS_URL", False, "GHL Contacts API URL (server-side funnel app)"),
    ("GoHighLevel", "PHOENIX_GHL_FUNNEL_WEBHOOK", False, "GHL inbound webhook URL for phoenix_lead.js static capture (Stillness / legacy /free/{slug}/)"),
    ("GoHighLevel", "PHOENIX_GHL_FUNNEL_WEBHOOK_STILLNESS", False, "Stillness Press funnel capture webhook"),
    ("GoHighLevel", "PHOENIX_GHL_FUNNEL_WEBHOOK_DEVOTION", False, "Devotion Path (Open Vessel Press) funnel capture webhook"),
    ("GoHighLevel", "PHOENIX_GHL_FUNNEL_WEBHOOK_WAYSTREAM", False, "Waystream Sanctuary funnel capture webhook"),
    # --- GHL V2 sub-account sync (YAML desired-state). NOT the legacy V1 funnel vars above. ---
    ("GoHighLevel", "GHL_PRIVATE_INTEGRATION_TOKEN", False, "GHL V2 Private Integration Token (Bearer). Read-only scopes ONLY: locations.readonly, locations/customValues.readonly, locations/customFields.readonly. Distinct from legacy GHL_API_KEY (V1, end-of-support 2025-12-31 — not accepted for sub-account sync). Static token: no auto-refresh, rotate every 90 days per HighLevel. Get: app.gohighlevel.com > Settings > Private Integrations > Create new Integration. See artifacts/coordination/handoffs/ghl_credential_sandbox_probe_2026-07-15.md §4."),
    ("GoHighLevel", "GHL_SANDBOX_LOCATION_ID", False, "Operator-selected sandbox/test GHL location id for read-only probes. NEVER a production location. Get: sandbox sub-account > Settings > Business Profile."),
    ("GoHighLevel", "GHL_API_VERSION", False, "GHL API `Version` request header value, e.g. 2021-07-28 per the Private Integration Token docs. Explicit desired-state metadata — docs are versioned, so never leave this implicit."),
    ("SMTP", "SMTP_HOST", False, "Funnel email host"),
    ("SMTP", "SMTP_PORT", False, "Funnel email port"),
    ("SMTP", "SMTP_USER", False, "Funnel email user"),
    ("SMTP", "SMTP_PASSWORD", False, "Funnel email password"),
    ("Funnel", "FROM_EMAIL", False, "Funnel sender email"),
    ("Funnel", "FROM_NAME", False, "Funnel sender name"),
    ("Funnel", "SECRET_KEY", False, "Flask session key"),
    ("Funnel", "BASE_URL", False, "Funnel base URL"),
    ("Google Analytics", "GA4_MEASUREMENT_ID", False, "Funnel analytics"),
    # --- Video Platforms ---
    ("YouTube (SP)", "YT_CLIENT_ID_SP", False, "YouTube OAuth client ID — SoulPath"),
    ("YouTube (SP)", "YT_CLIENT_SECRET_SP", False, "YouTube OAuth client secret — SoulPath"),
    ("YouTube (SP)", "YT_REFRESH_TOKEN_SP", False, "YouTube OAuth refresh token — SoulPath"),
    ("YouTube (CC)", "YT_CLIENT_ID_CC", False, "YouTube OAuth client ID — ConsciousCreator"),
    ("YouTube (CC)", "YT_CLIENT_SECRET_CC", False, "YouTube OAuth client secret — ConsciousCreator"),
    ("YouTube (CC)", "YT_REFRESH_TOKEN_CC", False, "YouTube OAuth refresh token — ConsciousCreator"),
    ("YouTube (ND)", "YT_CLIENT_ID_ND", False, "YouTube OAuth client ID — NeuroDharma"),
    ("YouTube (ND)", "YT_CLIENT_SECRET_ND", False, "YouTube OAuth client secret — NeuroDharma"),
    ("YouTube (ND)", "YT_REFRESH_TOKEN_ND", False, "YouTube OAuth refresh token — NeuroDharma"),
    ("TikTok (SP)", "TIKTOK_CLIENT_KEY_SP", False, "TikTok client key — SoulPath"),
    ("TikTok (SP)", "TIKTOK_CLIENT_SECRET_SP", False, "TikTok client secret — SoulPath"),
    ("TikTok (SP)", "TIKTOK_ACCESS_TOKEN_SP", False, "TikTok access token — SoulPath"),
    ("TikTok (CC)", "TIKTOK_CLIENT_KEY_CC", False, "TikTok client key — ConsciousCreator"),
    ("TikTok (CC)", "TIKTOK_CLIENT_SECRET_CC", False, "TikTok client secret — ConsciousCreator"),
    ("TikTok (CC)", "TIKTOK_ACCESS_TOKEN_CC", False, "TikTok access token — ConsciousCreator"),
    ("TikTok (ND)", "TIKTOK_CLIENT_KEY_ND", False, "TikTok client key — NeuroDharma"),
    ("TikTok (ND)", "TIKTOK_CLIENT_SECRET_ND", False, "TikTok client secret — NeuroDharma"),
    ("TikTok (ND)", "TIKTOK_ACCESS_TOKEN_ND", False, "TikTok access token — NeuroDharma"),
    ("Instagram (SP)", "IG_ACCESS_TOKEN_SP", False, "Instagram access token — SoulPath"),
    ("Instagram (SP)", "IG_USER_ID_SP", False, "Instagram user ID — SoulPath"),
    ("Instagram (CC)", "IG_ACCESS_TOKEN_CC", False, "Instagram access token — ConsciousCreator"),
    ("Instagram (CC)", "IG_USER_ID_CC", False, "Instagram user ID — ConsciousCreator"),
    ("Instagram (ND)", "IG_ACCESS_TOKEN_ND", False, "Instagram access token — NeuroDharma"),
    ("Instagram (ND)", "IG_USER_ID_ND", False, "Instagram user ID — NeuroDharma"),
    ("Bilibili", "BILIBILI_SESSDATA", False, "Bilibili session cookie (disabled platform)"),
    ("Bilibili", "BILIBILI_CSRF", False, "Bilibili CSRF token (disabled platform)"),
    ("Douyin", "DOUYIN_CLIENT_KEY", False, "Douyin client key (disabled, needs ICP)"),
    ("Douyin", "DOUYIN_CLIENT_SECRET", False, "Douyin client secret (disabled, needs ICP)"),
    ("Douyin", "DOUYIN_ACCESS_TOKEN", False, "Douyin access token (disabled, needs ICP)"),
    ("SerpApi", "SERPAPI_KEY", False, "Trend checking (245 calls/month budget)"),
    # --- Pearl Star (local inference server) ---
    ("Pearl Star", "PEARL_STAR_IP", True, "Pearl Star server LAN IP (ComfyUI, Ollama, CosyVoice2)"),
    ("Pearl Star / ComfyUI", "COMFYUI_URL", True, "ComfyUI endpoint (e.g. http://${PEARL_STAR_IP}:8188)"),
    ("Pearl Star / CosyVoice2", "COSYVOICE_URL", False, "CosyVoice2 TTS endpoint (e.g. http://${PEARL_STAR_IP}:9880)"),
    (
        "Pearl Star / Hugging Face",
        "HF_TOKEN",
        False,
        "Hugging Face user access token for gated model downloads on Pearl Star (huggingface-cli / ComfyUI). macOS Keychain only — never commit the value.",
    ),
    # Image generation (PRIMARY — ComfyUI on Pearl Star). RunComfy paid lane DECOMMISSIONED 2026-06-13
    # (operator cancelled — SWEEP-TAIL). RUNCOMFY_* removed from registry + Keychain; runtime code kept
    # fail-closed (backend selection falls through to Pearl Star/ComfyUI when creds absent). See cap
    # IMG-RENDER-DUAL-PATH-V1-01 (decommissioned) and docs/SESSION_HANDOFF_2026_06_11_RUNCOMFY_SUNSET.md.
    # fal.ai serverless GPU inference (Milestone H §7.1 smoke test target — Qwen-Image-Layered hosted endpoint)
    ("fal.ai", "FAL_KEY", False, "fal.ai serverless GPU inference key (canonical env var name per fal-client SDK). Used for Milestone H §7.1 Qwen-Image-Layered smoke test. Apache-2.0 model, commercial-clean ToS. Pricing: $0.06/image stage 2 + $0.02/MP stage 1. Get: https://fal.ai/dashboard/keys (see docs/runbooks/PEARL_INT_FAL_AI_SETUP_2026-05-27.md)"),
]

ENV_VARS_TRACKED_COUNT = len({row[1] for row in REGISTRY})
