"""Phoenix Omega manga translation pipeline.

Populates ``text_by_locale`` / ``sfx_by_locale`` / ``narrator_caption_by_locale``
dicts on v3 lettering specs and chapter scripts. Per PR #631 Decision 1:
50–99× cost reduction across 5 markets vs re-render-per-locale.

Backends (LLM Tier Policy compliant):
- ``qwen_ollama``  (Tier 2 default, free, unattended-safe — Pearl Star)
- ``deepseek``     (operator-present override — paid; ja_JP/zh quality)
- ``google_ai``    (operator-present override — Gemini 2.0 Flash free tier)
- ``mock``         (tests; deterministic output)

See: phoenix_v4/manga/translation/translators.py
"""
