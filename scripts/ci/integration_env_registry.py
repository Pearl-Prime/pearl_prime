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
    ("Qwen / DashScope", "QWEN_API_KEY", False, "DashScope API key (not needed for local Ollama)"),
    ("Qwen / DashScope", "QWEN_BASE_URL", True, "LLM endpoint URL (Pearl Star Ollama :11434/v1 or DashScope cloud)"),
    ("Qwen / DashScope", "QWEN_MODEL", False, "Model override (default in scripts)"),
    ("Qwen / DashScope", "DASHSCOPE_API_KEY", False, "Alt env var for DashScope key"),
    ("Qwen / DashScope", "DASHSCOPE_BASE_URL", False, "Alt env var for DashScope URL"),
    ("Qwen / DashScope", "DASHSCOPE_MODEL", False, "Alt env var for DashScope model"),
    ("Anthropic", "ANTHROPIC_API_KEY", False, "Claude API key (optional fallback LLM)"),
    ("Anthropic", "CLAUDE_MODEL", False, "Claude model selection"),
    ("OpenAI", "OPENAI_API_KEY", False, "OpenAI API key (TTS + fallback LLM)"),
    ("Ollama", "OLLAMA_HOST", False, "Local Ollama endpoint"),
    ("Ollama", "OLLAMA_MODEL", False, "Local Ollama model"),
    # --- Free-tier LLM providers (EN / non-CJK article expansion) ---
    ("Groq", "GROQ_API_KEY", False, "Free EN default: llama-3.3-70b-versatile. Get: console.groq.com/keys"),
    ("xAI / Grok", "XAI_API_KEY", False, "Free EN fallback 1: grok-3-mini. $25/mo free credits. Get: console.x.ai"),
    ("Together AI", "TOGETHER_API_KEY", False, "Free EN fallback 2: Llama-3.3-70B-Instruct-Turbo-Free. 1M tokens/mo. Get: api.together.ai"),
    # --- Media / TTS ---
    ("ElevenLabs", "ELEVENLABS_API_KEY", False, "TTS (guided audio, journal prompts)"),
    # --- Infrastructure ---
    ("Cloudflare", "CLOUDFLARE_ACCOUNT_ID", False, "Workers AI + Pages"),
    ("Cloudflare", "CLOUDFLARE_API_TOKEN", False, "Cloudflare API token"),
    ("Cloudflare", "CLOUDFLARE_AI_API_TOKEN", False, "Workers AI inference token"),
    ("Cloudflare", "CLOUDFLARE_AI_BASE_URL", False, "Workers AI OpenAI-compat base URL (accounts/<ID>/ai/v1)"),
    ("Cloudflare", "CLOUDFLARE_AI_MODEL", False, "Workers AI model name (e.g. @cf/google/gemma-3-12b-it)"),
    ("GitHub", "GITHUB_TOKEN", False, "GitHub API (auto in Actions)"),
    ("GitHub", "GITHUB_REPOSITORY", False, "owner/repo for API calls; auto in Actions"),
    # --- Publishing ---
    ("WordPress", "WORDPRESS_SITE_URL", False, "Pearl News publishing"),
    ("WordPress", "WORDPRESS_USERNAME", False, "WordPress user"),
    ("WordPress", "WORDPRESS_APP_PASSWORD", False, "WordPress app password"),
    # --- Funnel ---
    ("GoHighLevel", "GHL_API_KEY", False, "Funnel CRM"),
    ("GoHighLevel", "GHL_LOCATION_ID", False, "GHL location"),
    ("GoHighLevel", "GHL_CONTACTS_URL", False, "GHL contacts / webhook URL"),
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
    # Image generation (PRIMARY — ComfyUI on Pearl Star; RunComfy is cloud fallback)
    ("RunComfy", "RUNCOMFY_API_KEY", False, "RunComfy API key (FALLBACK image gen — cloud backup when ComfyUI unavailable)"),
    ("RunComfy", "RUNCOMFY_DEPLOYMENT_ID", False, "RunComfy deployment ID (default: 677edba8-ace0-4b2b-bad2-8e94b9959065)"),
]

ENV_VARS_TRACKED_COUNT = len({row[1] for row in REGISTRY})
