"""Script-aware word counting for book gates and reports.

English (and other whitespace-delimited scripts) keep whitespace tokenization.
CJK ideographs / kana / hangul each count as one word unit so a full Han
paragraph is never treated as a single whitespace-"word".

This does **not** relax gate thresholds — it only makes the unit of measure
honest for mixed and CJK prose. Production gates (F2.D, F14, book word-floor,
book-pass / book-quality reporting) must use ``count_words`` instead of
``len(text.split())``.
"""
from __future__ import annotations

import re

# Han (unified + ext A + compatibility) + hiragana + katakana + hangul syllables.
_CJK_CHAR_RE = re.compile(
    r"["
    r"\u3400-\u4dbf"
    r"\u4e00-\u9fff"
    r"\uf900-\ufaff"
    r"\u3040-\u309f"
    r"\u30a0-\u30ff"
    r"\uac00-\ud7af"
    r"]"
)

# Sentence-terminal marks recognized by fragment detectors (ASCII + CJK).
CJK_SENTENCE_TERMINALS = (".", "?", "!", "。", "？", "！", "…", "‥")


def has_cjk_script(text: str) -> bool:
    """True when *text* contains at least one CJK ideograph/kana/hangul char."""
    return bool(text and _CJK_CHAR_RE.search(text))


def count_words(text: str) -> int:
    """Count words with CJK-honest units.

    - Each CJK ideograph / hiragana / katakana / hangul syllable = 1 word.
    - Remaining non-CJK text is whitespace-split (same as ``str.split()``).
    - Empty / whitespace-only input → 0.
    """
    if not text:
        return 0
    s = text.strip()
    if not s:
        return 0
    cjk_units = len(_CJK_CHAR_RE.findall(s))
    remainder = _CJK_CHAR_RE.sub(" ", s)
    spaced_units = len(remainder.split())
    return cjk_units + spaced_units
