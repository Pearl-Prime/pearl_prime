"""Locale-fallback honesty gate for the spine renderer.

Problem this closes
-------------------
When a book is rendered with ``--locale zh-TW`` (or any non-English locale) the
spine selector localizes *some* atom classes (persona HOOK/SCENE/PIVOT/…, which
thread ``locale`` through ``_load_persona_atoms``) but *silently falls back to the
English source* for atom classes whose resolver path does not thread ``locale``
(story_plan STORY, composite_doctrine REFLECTION, practice_library EXERCISE,
angle_atom ANGLE_*). The result is a book that is labelled zh-TW but renders the
majority of its body prose in English — with no signal anywhere in the render
artifacts. See ``artifacts/qa/zhtw_targetbook_fallback_manifest.json`` for the
empirical map that motivated this module.

What this module does
---------------------
1. Classifies every body-prose slot in an enriched book as ``localized`` /
   ``english_fallback`` / ``allowed_english`` / ``not_body_prose`` / ``empty`` /
   ``undetectable_by_script``.
2. Emits a ``locale_fallback_report.json`` artifact into the render dir listing
   every English fallback (draft renders still complete, but the fallback is now
   explicit and labelled).
3. Provides ``production_blockers()`` so a production render can FAIL loudly with a
   specific per-atom / per-slot / per-chapter message instead of shipping an
   English book under a localized SKU.

Narrowest safe classification rule (documented on purpose)
----------------------------------------------------------
There is no pre-existing allowed-English classifier in the repo, so this module
uses the narrowest rule that is safe:

* Detection is **script-based** and only *decisive* for target locales written in
  a **non-Latin script** (CJK: ``zh-*``, ``ja-*``, ``ko-*``). For those, a
  body-prose slot whose rendered content has a target-script character ratio below
  ``MIN_TARGET_SCRIPT_RATIO`` **and** at least ``MIN_LATIN_LETTERS`` Latin letters
  is an English fallback.
* **Citations / proper nouns / source titles are never flagged**: a slot whose
  Latin letters live entirely inside citation/parenthetical/quoted-title tokens
  (so the residue is below ``MIN_LATIN_LETTERS``) is classified ``allowed_english``.
  Short proper-noun-only content likewise falls below the Latin floor. A citation
  embedded inside otherwise-localized prose keeps the target-script ratio high, so
  it is classified ``localized``.
* For **Latin-script** target locales (``de-DE``, ``fr-FR``, ``pt-BR`` …) script
  analysis cannot distinguish English from the target language; such slots are
  classified ``undetectable_by_script`` and are **never** used to fail a build
  here. (A source-equality check would be needed and is out of scope for this
  gate.)

The module deliberately adds a gate; it does not weaken any existing threshold and
does not touch any English source content.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1

# Body-prose slot types (the reader-facing prose of the twelve-shape spine). Only
# these are subject to the localization requirement. Anything not listed is treated
# as non-body / structural and never flagged.
BODY_PROSE_SLOT_TYPES = frozenset({
    "HOOK", "SCENE", "STORY", "PIVOT", "REFLECTION", "TAKEAWAY",
    "INTEGRATION", "THREAD", "EXERCISE", "PERMISSION", "PERMISSION_GRANT",
    "ANGLE_DEFINITION", "ANGLE_CALLBACK",
})

# Detection thresholds (see module docstring).
MIN_TARGET_SCRIPT_RATIO = 0.15
MIN_LATIN_LETTERS = 20

# Unicode ranges per non-Latin script family we can decisively detect.
_SCRIPT_RANGES = {
    # CJK ideographs + Japanese kana + Korean hangul (shared "cjk" family — any of
    # these counts as "target script" for zh/ja/ko locales).
    "cjk": (
        r"぀-ヿ"   # hiragana + katakana
        r"㐀-䶿"   # CJK ext A
        r"一-鿿"   # CJK unified
        r"豈-﫿"   # CJK compat
        r"가-힯"   # hangul syllables
    ),
}

_LATIN_RE = re.compile(r"[A-Za-z]")


def _locale_script_family(locale: str | None) -> str | None:
    """Return the non-Latin script family for a locale, or None if Latin-script /
    unset / en-US (i.e. not decisively detectable by this gate)."""
    if not locale:
        return None
    loc = locale.strip().lower().replace("_", "-")
    if loc in ("", "en-us") or loc.startswith("en-"):
        return None
    if loc.startswith(("zh", "ja", "ko")):
        return "cjk"
    # Latin-script (de, fr, es, it, pt, hu, ...) — undetectable by script here.
    return None


# Citation / parenthetical / quoted-title tokens whose Latin letters are "allowed
# English" (proper nouns, source titles, author-year cites). Removing these before
# the Latin-floor check means a slot that is *only* such tokens is not flagged.
_ALLOWED_ENGLISH_TOKEN_RES = (
    re.compile(r"\[[^\]]*\]"),            # [Barrett, 2017], [sic], [12]
    re.compile(r"\([^)]*\d{4}[^)]*\)"),   # (Barrett, 2017)
    re.compile(r"[“\"'‘][^”\"'’]{0,80}[”\"'’]"),  # "A Quoted Title"
)


def _strip_allowed_english_tokens(text: str) -> str:
    out = text
    for rx in _ALLOWED_ENGLISH_TOKEN_RES:
        out = rx.sub(" ", out)
    return out


def _counts(text: str, family: str) -> tuple[int, int]:
    """Return (target_script_chars, latin_letters) for text under a script family."""
    rng = _SCRIPT_RANGES[family]
    target = len(re.findall(f"[{rng}]", text))
    latin = len(_LATIN_RE.findall(text))
    return target, latin


def classify_slot(slot_type: str, content: str, locale: str | None) -> dict[str, Any]:
    """Classify one slot. Returns a dict with 'classification' and diagnostics."""
    st = (slot_type or "").strip().upper()
    family = _locale_script_family(locale)
    text = content or ""
    base = {
        "slot_type": st,
        "target_script_chars": 0,
        "latin_letters": 0,
        "target_script_ratio": 0.0,
    }
    if st not in BODY_PROSE_SLOT_TYPES:
        base["classification"] = "not_body_prose"
        return base
    if not text.strip():
        base["classification"] = "empty"
        return base
    if family is None:
        base["classification"] = "undetectable_by_script"
        return base

    target, latin = _counts(text, family)
    denom = target + latin
    ratio = (target / denom) if denom else 1.0
    base.update({
        "target_script_chars": target,
        "latin_letters": latin,
        "target_script_ratio": round(ratio, 4),
    })

    if ratio >= MIN_TARGET_SCRIPT_RATIO:
        # Predominantly (or partly) target script — localized. Embedded English
        # citations do not pull the ratio below the floor.
        base["classification"] = "localized"
        return base

    # Low target-script ratio. Decide fallback vs allowed-English by measuring the
    # Latin residue AFTER removing citation/proper-noun/title tokens.
    residue_latin = len(_LATIN_RE.findall(_strip_allowed_english_tokens(text)))
    base["residue_latin_letters"] = residue_latin
    if residue_latin >= MIN_LATIN_LETTERS:
        base["classification"] = "english_fallback"
    else:
        # Only citations / proper nouns / short tokens carry the Latin letters.
        base["classification"] = "allowed_english"
    return base


def _iter_slots(book: Any) -> Iterable[tuple[int, Any]]:
    """Yield (chapter_number, slot) from an EnrichedBook-like object."""
    for ch in getattr(book, "chapters", []) or []:
        num = getattr(ch, "number", None)
        if num is None and isinstance(ch, dict):
            num = ch.get("number")
        slots = getattr(ch, "slots", None)
        if slots is None and isinstance(ch, dict):
            slots = ch.get("slots")
        for slot in slots or []:
            yield int(num or 0), slot


def _slot_field(slot: Any, name: str, default: str = "") -> str:
    if isinstance(slot, dict):
        return str(slot.get(name, default) or default)
    return str(getattr(slot, name, default) or default)


def build_locale_fallback_report(
    book: Any,
    locale: str | None,
    quality_profile: str,
) -> dict[str, Any]:
    """Build the locale-fallback report for an enriched (spine) book."""
    family = _locale_script_family(locale)
    entries: list[dict[str, Any]] = []
    counts = {
        "localized": 0,
        "english_fallback": 0,
        "allowed_english": 0,
        "not_body_prose": 0,
        "empty": 0,
        "undetectable_by_script": 0,
    }
    for ch_num, slot in _iter_slots(book):
        st = _slot_field(slot, "slot_type")
        content = _slot_field(slot, "content")
        cls = classify_slot(st, content, locale)
        counts[cls["classification"]] = counts.get(cls["classification"], 0) + 1
        if cls["classification"] in ("english_fallback", "allowed_english"):
            entries.append({
                "chapter": ch_num,
                "slot_type": st,
                "classification": cls["classification"],
                "source": _slot_field(slot, "source"),
                "source_id": _slot_field(slot, "source_id"),
                "atom_id": _slot_field(slot, "atom_id"),
                "target_script_ratio": cls.get("target_script_ratio"),
                "latin_letters": cls.get("latin_letters"),
                "residue_latin_letters": cls.get("residue_latin_letters"),
                "excerpt": re.sub(r"\s+", " ", content.strip())[:200],
            })

    fallbacks = [e for e in entries if e["classification"] == "english_fallback"]
    applicable = family is not None and bool(locale) and _locale_script_family(locale) is not None
    production = str(quality_profile or "").strip().lower() == "production"
    report = {
        "schema_version": SCHEMA_VERSION,
        "stage": "locale_fallback_report",
        "locale": locale or "en-US",
        "quality_profile": quality_profile,
        "script_family": family or "",
        "applicable": bool(applicable),
        "detection_rule": (
            "script-based; decisive only for non-Latin (CJK) target locales. "
            f"MIN_TARGET_SCRIPT_RATIO={MIN_TARGET_SCRIPT_RATIO}, "
            f"MIN_LATIN_LETTERS={MIN_LATIN_LETTERS}. Citations/proper-nouns/titles "
            "are stripped before the Latin floor and never flagged."
        ),
        "summary": {
            "total_slots": sum(counts.values()),
            **counts,
        },
        "english_fallbacks": fallbacks,
        "allowed_english": [e for e in entries if e["classification"] == "allowed_english"],
        "production_would_fail": bool(applicable and production and fallbacks),
    }
    return report


def production_blockers(report: dict[str, Any]) -> list[str]:
    """Human-readable blocker lines for a production render (one per fallback)."""
    lines: list[str] = []
    for e in report.get("english_fallbacks", []):
        lines.append(
            f"ch{e['chapter']} {e['slot_type']} [{e['source']}:{e['source_id']}] "
            f"rendered ENGLISH under locale {report.get('locale')} "
            f"(target-script ratio {e.get('target_script_ratio')})"
        )
    return lines


def write_locale_fallback_report(
    book: Any,
    locale: str | None,
    quality_profile: str,
    render_dir: Path,
    filename: str = "locale_fallback_report.json",
) -> tuple[dict[str, Any], Path]:
    """Build + write the report into render_dir. Returns (report, path)."""
    report = build_locale_fallback_report(book, locale, quality_profile)
    render_dir = Path(render_dir)
    render_dir.mkdir(parents=True, exist_ok=True)
    path = render_dir / filename
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report, path


class LocaleFallbackError(RuntimeError):
    """Raised in production when a required localized body-prose atom fell back to English."""
