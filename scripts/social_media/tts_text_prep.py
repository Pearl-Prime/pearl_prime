"""Apply config/tts/social_media_tts_text_prep.yaml to synth input (no SSOT mutation)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO = Path(__file__).resolve().parents[2]
DEFAULT_PREP = REPO / "config" / "tts" / "social_media_tts_text_prep.yaml"


def load_prep(path: Path | None = None) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML required")
    p = path or DEFAULT_PREP
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if (data.get("policy") or {}).get("ssml") == "forbidden":
        pass
    return data


def _apply_rule_list(text: str, rules: list[dict[str, Any]]) -> str:
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        pat = rule.get("pattern")
        if not pat:
            continue
        text = re.sub(pat, rule.get("replace", ""), text)
    return text


# Default (English) sentence-boundary behavior — unchanged from the original
# implementation so English output stays byte-identical after the CJK6
# locale-awareness extension below (2026-07-24, Lane 2 SOCIALTTS-L2).
DEFAULT_SENTENCE_END_CHARS = (".", "!", "?")
DEFAULT_TERMINAL_PUNCT = "."


def apply_text_prep(text: str, prep: dict[str, Any] | None = None) -> str:
    """Return speakable plain text. Never writes back to atom SSOT."""
    cfg = prep if prep is not None else load_prep()
    out = text
    order = cfg.get("apply_order") or [
        "speakable_expansions",
        "homograph_and_trap_rewrites",
        "punctuation_pacing",
    ]
    for key in order:
        block = cfg.get(key) or {}
        if key == "punctuation_pacing":
            rules = block.get("rules") or []
        else:
            rules = block if isinstance(block, list) else []
        out = _apply_rule_list(out, rules)
    out = re.sub(r"\s{2,}", " ", out).strip()

    # Locale-aware sentence boundary chars. Default is English ".!?" and
    # REQUIRES trailing whitespace to split (matches the original hardcoded
    # r"([.!?]\s+)" exactly, so English behavior is byte-identical). CJK
    # rulesets set policy.sentence_end_chars (e.g. ["。", "！", "？"]) and
    # policy.sentence_boundary_requires_space: false, because CJK full-stop
    # punctuation is not followed by a space in running text.
    policy = cfg.get("policy") or {}
    end_chars = policy.get("sentence_end_chars") or list(DEFAULT_SENTENCE_END_CHARS)
    requires_space = policy.get("sentence_boundary_requires_space", True)
    terminal_punct = policy.get("default_terminal_punct") or DEFAULT_TERMINAL_PUNCT
    end_class = "".join(re.escape(c) for c in end_chars)
    space_quantifier = r"\s+" if requires_space else r"\s*"

    # Capitalize start of each sentence (aggressive splits often leave
    # lowercase). No-op for scripts without case (CJK) since str.upper() on
    # a CJK character returns the same character.
    parts = re.split(f"([{end_class}]{space_quantifier})", out)
    rebuilt: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 0 and part:
            part = part[0].upper() + part[1:]
        rebuilt.append(part)
    out = "".join(rebuilt).strip()
    if out and out[-1] not in end_chars:
        out += terminal_punct
    return out
