"""Translation glossary + tone notes for iyashikei manga.

PR #631 therapeutic-craft companion: iyashikei depends on negative space,
breath, and gentle sensory anchors. Translation must preserve those
qualities — a literal-tight rendering can flatten the regulating effect.

This module exports:
- TONE_NOTES_BY_LOCALE — system-prompt fragments handed to the translator
- TERMINOLOGY — terms with locked translations (consistency across episodes)
- SFX_POLICY_BY_LOCALE — Japanese onomatopoeia handling rules

Used by translators.py to build per-locale system prompts.
"""
from __future__ import annotations

from typing import Final


# ─── tone notes ────────────────────────────────────────────────────────────
# Each note is plain English, prepended to the system prompt before the
# locale-specific user instruction. Covers register, pacing, sensory weight.

TONE_NOTES_BY_LOCALE: Final[dict[str, str]] = {
    "ja_JP": (
        "Translate to Japanese for an iyashikei (癒し系) manga. "
        "Voice is gentle, slow, sensory. Prefer plain-form (ですます/だ) over "
        "stylized speech. Internal monologue uses だ-form / casual register. "
        "Preserve negative space — short translations are usually right. Avoid "
        "loanword-heavy phrasing; prefer native Japanese vocabulary where "
        "natural. Do NOT add explanation or emotion words the source lacks. "
        "Onomatopoeia stay in their original Japanese where appropriate "
        "(例: 「ドキドキ」「シーン」)."
    ),
    "zh_TW": (
        "Translate to Traditional Chinese (Taiwan) for an iyashikei healing "
        "manga (療癒系). Tone is gentle, contemplative, present-tense. Prefer "
        "concise lines — Traditional Chinese readers expect economy of "
        "characters in dialogue. Use 你/我 colloquially; avoid stiff literary "
        "register. Use Taiwan/HK vocabulary (e.g. 軟體 not 软件). Preserve "
        "the sensory weight of the original."
    ),
    "zh_CN": (
        "Translate to Simplified Chinese (Mainland) for a healing/治愈系 "
        "manga. Tone is gentle, contemplative, present-tense. Prefer concise "
        "lines. Use mainland vocabulary (软件 not 軟體). Avoid mainland "
        "internet slang or very modern colloquialisms — the audience for "
        "this work prefers a slightly more contemplative register."
    ),
    "ko_KR": (
        "Translate to Korean for a healing (힐링) webtoon. Tone is gentle, "
        "warm, unhurried. Use 해요-form for spoken dialogue (mid-formal); "
        "internal monologue uses 해 / 다 plain form depending on character "
        "register. Preserve the sensory and breath quality of the source."
    ),
}


# ─── terminology lock-ins ──────────────────────────────────────────────────
# Terms that recur across the catalog and must translate consistently.
# Format: { en_US_term: { locale: translation } }.

TERMINOLOGY: Final[dict[str, dict[str, str]]] = {
    # Core teaching frame
    "alarm system": {
        "ja_JP": "警報システム",
        "zh_TW": "警報系統",
        "zh_CN": "警报系统",
        "ko_KR": "경보 체계",
    },
    "smoke detector": {
        "ja_JP": "煙感知器",
        "zh_TW": "煙霧偵測器",
        "zh_CN": "烟雾探测器",
        "ko_KR": "연기 감지기",
    },
    # Therapeutic teaching anchors
    "still here": {
        "ja_JP": "まだ ここに",
        "zh_TW": "還在這裡",
        "zh_CN": "还在这里",
        "ko_KR": "아직 여기에",
    },
    # Recurring scene-setting
    "the tea is still warm": {
        "ja_JP": "お茶は まだ 温かい",
        "zh_TW": "茶還溫著",
        "zh_CN": "茶还温着",
        "ko_KR": "차는 아직 따뜻하다",
    },
}


# ─── SFX policy ────────────────────────────────────────────────────────────
# Per locale, how to handle the source SFX list.

SFX_POLICY_BY_LOCALE: Final[dict[str, str]] = {
    "ja_JP": (
        "Convert Latin SFX to Japanese onomatopoeia. Common mappings: "
        "BANG → ドン / ドカン. THUD → ドサッ. CRASH → ガシャン. "
        "Quiet heartbeat → ドキドキ (whisper register). Silence-marker → シーン. "
        "If source SFX is already Japanese, keep as-is."
    ),
    "zh_TW": (
        "Use Taiwan/HK comic-standard sound effects. Common mappings: "
        "BANG → 砰. THUD → 咚. CRASH → 嘩啦. Heartbeat → 撲通. "
        "Where the SFX is purely sensory (e.g. silence), preserve in 中文."
    ),
    "zh_CN": (
        "Use mainland comic-standard sound effects. Common mappings: "
        "BANG → 砰. THUD → 咚. CRASH → 哗啦. Heartbeat → 扑通. Same as TC "
        "but with simplified characters."
    ),
    "ko_KR": (
        "Use Korean onomatopoeia. Common mappings: BANG → 쾅. "
        "THUD → 쿵. CRASH → 와장창. Heartbeat → 두근두근."
    ),
}


def system_prompt_for(locale: str) -> str:
    """Compose the full system prompt for a translator targeting `locale`.

    Includes tone notes, SFX policy, and a short terminology preamble.
    """
    tone = TONE_NOTES_BY_LOCALE.get(locale, "")
    sfx = SFX_POLICY_BY_LOCALE.get(locale, "")
    glossary_lines = []
    for term, locales in TERMINOLOGY.items():
        if locale in locales:
            glossary_lines.append(f"- {term!r} → {locales[locale]!r}")
    glossary = "\n".join(glossary_lines)

    return (
        f"You are a professional translator for therapeutic manga.\n\n"
        f"{tone}\n\n"
        f"SFX policy: {sfx}\n\n"
        f"Locked terminology (use exactly when these terms appear):\n{glossary}\n\n"
        f"Output ONLY the translated text — no quotes, no explanation, no markdown."
    )
