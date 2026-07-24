#!/usr/bin/env python3
"""Deterministic zh-CN / zh-TW script-contamination detector.

Detects the wrong Chinese script (Simplified leaking into a zh-TW target,
Traditional leaking into a zh-CN target) plus known Taiwan/Hong-Kong or
Mainland vocabulary leaking into the other locale's output.

This module is a DETECTOR, not a rubric. It reuses:
  - the calibrated s2t/t2s + Big5/GB2312 charset-intersection method
    already implemented in
    scripts/localization/check_title_language_conformance.py
    (`_wrong_script_traditional_required` /
    `_wrong_script_simplified_required`) -- re-derived here at body-text
    granularity (that module only checks short title/subtitle strings).
  - the corpus-calibrated watchlist data in
    `analysis/<locale_dir>/regional_usage_watchlist.yaml` (built by Lane 02
    of docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/)
    when present, falling back to this package's bundled starter watchlist
    in `script_watchlists/` otherwise.

It does NOT reimplement the native-reader QA rubric in
docs/agent_prompt_packs/20260720_cjk_translation_native_audit/03_translate_zh_cn_audit.md
or the persona rules in .claude/agents/translate-zh-cn.md /
.claude/agents/translate-zh-tw.md -- those remain human/agent judgment
calls. This module only flags mechanical, re-derivable evidence for that
judgment to consume.

Usage:
    python3 scripts/localization/translation_quality/script_contamination.py \\
        --locale zh-CN path/to/CANONICAL.txt [more paths...]

    from scripts.localization.translation_quality.script_contamination import (
        check_text,
    )
    findings = check_text(text, locale="zh-CN")
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
WATCHLIST_DIR = Path(__file__).resolve().parent / "script_watchlists"

_OPENCC_S2T = None
_OPENCC_T2S = None


def _opencc():
    global _OPENCC_S2T, _OPENCC_T2S
    if _OPENCC_S2T is None:
        import opencc

        _OPENCC_S2T = opencc.OpenCC("s2t")
        _OPENCC_T2S = opencc.OpenCC("t2s")
    return _OPENCC_S2T, _OPENCC_T2S


def _has_non_encodable_char(text: str, codec: str) -> bool:
    """True if any alphabetic char in text cannot round-trip through codec.

    Mirrors check_title_language_conformance._has_non_encodable_char.
    """
    for ch in text:
        if not ch.isalpha():
            continue
        try:
            ch.encode(codec)
        except UnicodeEncodeError:
            return True
    return False


LOCALE_DIRS = {"zh-CN": "zh_cn", "zh-TW": "zh_tw"}
LOCALE_CODECS = {"zh-CN": "gb2312", "zh-TW": "big5"}


def _watchlist_path(locale: str) -> Path:
    """Prefer the live, corpus-derived analysis/ file; fall back to the
    bundled starter watchlist shipped with this package."""
    locale_dir = LOCALE_DIRS.get(locale)
    if locale_dir:
        live = REPO_ROOT / "analysis" / locale_dir / "regional_usage_watchlist.yaml"
        if live.is_file():
            return live
    return WATCHLIST_DIR / f"{locale_dir or locale.lower().replace('-', '_')}_default.yaml"


def load_watchlist(locale: str, path: Path | None = None) -> dict[str, Any]:
    p = path or _watchlist_path(locale)
    if not p.is_file():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


@dataclass
class ScriptFinding:
    kind: str  # "wrong_script_char" | "forbidden_vocabulary"
    detail: str
    offending_span: str


@dataclass
class ScriptCheckResult:
    locale: str
    watchlist_source: str
    wrong_script_flagged: bool
    findings: list[ScriptFinding] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.findings


def _wrong_script_present(text: str, locale: str) -> bool:
    """zh-CN body must be Simplified; zh-TW body must be Traditional.

    Returns True only when opencc's round-trip conversion changes the text
    (suggesting the "other" script is present) AND at least one changed
    character falls outside the target locale's classical charset -- the
    AND avoids single-glyph false positives from opencc's variant-selection
    heuristics alone (documented false-positive class: 台/吃/游/群/床).
    """
    if not text.strip():
        return False
    s2t, t2s = _opencc()
    codec = LOCALE_CODECS[locale]
    if locale == "zh-TW":
        changed = s2t.convert(text) != text
    else:
        changed = t2s.convert(text) != text
    if not changed:
        return False
    return _has_non_encodable_char(text, codec)


def _iter_forbidden_terms(watchlist: dict[str, Any], locale: str) -> list[tuple[str, str]]:
    """Return [(forbidden_term, replacement_note), ...] for this locale."""
    out: list[tuple[str, str]] = []
    if locale == "zh-CN":
        for row in watchlist.get("forbidden_taiwan_vocabulary") or []:
            term = row.get("taiwan")
            if term:
                out.append((term, str(row.get("mainland", ""))))
        for row in watchlist.get("forbidden_hongkong_vocabulary") or []:
            term = row.get("hongkong")
            if term:
                out.append((term, str(row.get("mainland", ""))))
    elif locale == "zh-TW":
        for row in watchlist.get("forbidden_mainland_vocabulary") or []:
            term = row.get("mainland")
            if term:
                out.append((term, str(row.get("taiwan", ""))))
        for row in watchlist.get("forbidden_hongkong_vocabulary") or []:
            term = row.get("hongkong")
            if term:
                out.append((term, str(row.get("taiwan", ""))))
    return out


def check_text(text: str, locale: str, watchlist_path: Path | None = None) -> ScriptCheckResult:
    """Run the script-contamination detector against one blob of target text.

    locale: "zh-CN" or "zh-TW" (the target locale of `text`).
    """
    if locale not in LOCALE_CODECS:
        raise ValueError(f"script_contamination only supports zh-CN/zh-TW, got {locale!r}")

    watchlist = load_watchlist(locale, watchlist_path)
    wl_path = watchlist_path or _watchlist_path(locale)
    findings: list[ScriptFinding] = []

    wrong_script = _wrong_script_present(text, locale)
    if wrong_script:
        findings.append(
            ScriptFinding(
                kind="wrong_script_char",
                detail=(
                    "Traditional-script leakage in zh-CN target"
                    if locale == "zh-CN"
                    else "Simplified-script leakage in zh-TW target"
                ),
                offending_span="",
            )
        )

    for term, replacement in _iter_forbidden_terms(watchlist, locale):
        if term and term in text:
            findings.append(
                ScriptFinding(
                    kind="forbidden_vocabulary",
                    detail=f"forbidden term {term!r} (prefer {replacement!r})",
                    offending_span=term,
                )
            )

    return ScriptCheckResult(
        locale=locale,
        watchlist_source=str(wl_path.relative_to(REPO_ROOT)) if wl_path.is_file() else "none",
        wrong_script_flagged=wrong_script,
        findings=findings,
    )


def check_file(path: Path, locale: str, watchlist_path: Path | None = None) -> ScriptCheckResult:
    text = path.read_text(encoding="utf-8")
    return check_text(text, locale=locale, watchlist_path=watchlist_path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="Target-locale CANONICAL.txt (or any text) files to check")
    ap.add_argument("--locale", required=True, choices=sorted(LOCALE_CODECS), help="Target locale of the files")
    ap.add_argument("--watchlist", type=Path, default=None, help="Override watchlist YAML path")
    args = ap.parse_args(argv)

    failed = 0
    for raw in args.paths:
        p = Path(raw)
        result = check_file(p, locale=args.locale, watchlist_path=args.watchlist)
        if result.clean:
            print(f"OK  {p} (watchlist={result.watchlist_source})")
        else:
            failed += 1
            print(f"FAIL {p} (watchlist={result.watchlist_source})")
            for f in result.findings:
                print(f"     - {f.kind}: {f.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
