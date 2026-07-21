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
    # Capitalize start of each sentence (aggressive splits often leave lowercase).
    parts = re.split(r"([.!?]\s+)", out)
    rebuilt: list[str] = []
    for i, part in enumerate(parts):
        if i % 2 == 0 and part:
            part = part[0].upper() + part[1:]
        rebuilt.append(part)
    out = "".join(rebuilt).strip()
    if out and out[-1] not in ".!?":
        out += "."
    return out
