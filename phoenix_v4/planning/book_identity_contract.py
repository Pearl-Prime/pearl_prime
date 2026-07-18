"""Book identity contracts — selection enforcement (Part E, de-injection 2026-07-05).

Config: ``config/planning/book_identity_contracts/{topic_id}.yaml``
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_CONTRACTS_DIR = REPO_ROOT / "config" / "planning" / "book_identity_contracts"
_CACHE: dict[str, dict[str, Any] | None] = {}


def load_book_identity_contract(topic_id: str) -> dict[str, Any] | None:
    tid = (topic_id or "").strip().lower()
    if not tid:
        return None
    if tid in _CACHE:
        return _CACHE[tid]
    path = _CONTRACTS_DIR / f"{tid}.yaml"
    if not path.exists() or yaml is None:
        _CACHE[tid] = None
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        data = {}
    if not isinstance(data, dict) or data.get("status") != "wired":
        _CACHE[tid] = None
        return None
    _CACHE[tid] = data
    return data


def banned_phrase_penalty(text: str, contract: dict[str, Any]) -> float:
    """Soft penalty per banned phrase hit (not a hard reject)."""
    low = (text or "").lower()
    banned = contract.get("banned_phrases") or []
    hits = sum(1 for p in banned if p and str(p).lower() in low)
    return float(hits) * 3.0


def engine_metaphor_bonus(text: str, contract: dict[str, Any], engine: str) -> float:
    """Tie-breaker bonus when atom imagery aligns with engine metaphor."""
    engine_key = (engine or "").strip().lower()
    metaphors = contract.get("engine_metaphors") or {}
    if not engine_key or not isinstance(metaphors, dict):
        return 0.0
    phrase = str(metaphors.get(engine_key) or "").strip().lower()
    if not phrase:
        return 0.0
    low = (text or "").lower()
    # First content word of metaphor phrase as a cheap anchor.
    anchor = phrase.split()[0] if phrase.split() else ""
    if len(anchor) > 3 and anchor in low:
        return 2.0
    if phrase[:24] in low:
        return 1.5
    return 0.0


def identity_line_for_chapter(
    contract: dict[str, Any],
    chapter_index0: int,
    total_chapters: int,
) -> str:
    """Return identity line when this chapter index should carry it."""
    line = str(contract.get("identity_line") or "").strip()
    if not line:
        return ""
    placement = contract.get("identity_line_placement") or [1, "last"]
    ch_num = chapter_index0 + 1
    for p in placement:
        if str(p).strip().lower() == "last" and chapter_index0 >= total_chapters - 1:
            return line
        try:
            if int(p) == ch_num:
                return line
        except (TypeError, ValueError):
            continue
    return ""


def ensure_identity_line_in_text(
    text: str,
    identity_line: str,
) -> str:
    """Append identity line when absent from chapter prose."""
    body = (text or "").strip()
    line = (identity_line or "").strip()
    if not body or not line:
        return body
    if line.lower() in body.lower():
        return body
    return f"{body}\n\n{line}"
