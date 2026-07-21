#!/usr/bin/env python3
"""Title/subtitle LANGUAGE-conformance checker — books, illustrated, manga.

Distinct from scripts/catalog/validate_worldwide_plan_completeness.py, which
checks PLAN *existence* (a title is present / non-TBD) but explicitly does
NOT check whether a present title is actually written in the target
locale's language. This script closes that gap.

Scope (per docs/specs/WORLDWIDE_PLAN_COMPLETENESS_V1_SPEC.md):
  - book:        config/source_of_truth/book_plans_<locale>/*.yaml (title, subtitle)
  - illustrated: config/source_of_truth/manga_series_plans/<locale>/*.yaml filtered to
                 master_format/format == direct_self_help_illustrated (title only;
                 required for en_US, es_US, es_ES, de_DE, it_IT, hu_HU, zh_SG, pt_BR)
  - manga:       same tree, non-illustrated. title: TBD is EXPLICITLY ALLOWED
                 (spec S4.5) and is not a conformance failure -- only non-TBD
                 titles are checked here.

Detection strategy (evidence-based, not a guess):
  1. english_copy_through -- the locale's title/subtitle string is BYTE-IDENTICAL
     to a string observed in the en-US reference set for the same surface. For
     multi-word template phrases ("A guide for Corporate Managers") an exact
     byte match against the English source is a very strong, low-false-positive
     signal of un-translated copy-through.
  2. ascii_only_in_cjk_locale -- for CJK-script locales (ja-JP, ko-KR, zh-*),
     a title/subtitle with no CJK/Kana/Hangul codepoints at all is de facto
     English/Latin, independent of the reference-set match.
  3. wrong_script (zh-TW, zh-HK: must be Traditional; zh-CN, zh-SG: must be
     Simplified) -- uses opencc (already vendored in this environment) for
     the s2t/t2s round trip PLUS a codec-encodability check (big5 for
     Traditional-required locales, gb2312 for Simplified-required locales) so
     a single character that already looks identical in both scripts (opencc
     "changed" it via variant-selection heuristics alone) is not flagged
     unless it is also outside the target script's classical charset. This
     avoids the documented false-positive class (see
     docs -- reference_zhtw_simplified_detection_big5 memory) on characters
     that are common to both scripts.
  4. script_mismatch_ja / script_mismatch_ko -- ja-JP titles with zero
     Hiragana/Katakana codepoints, or ko-KR titles with zero Hangul
     codepoints, are flagged for manual review (weaker signal than #1/#2;
     reported separately, not folded into the hard-fail count without a
     human/agent read since short kanji-only or loan-word titles exist).

This tool aggregates by DISTINCT VALUE, not by file, because the catalog is
fanned out from a small closed template vocabulary (confirmed live: ~40-73
distinct titles / ~9 distinct subtitles cover ~30,000+ book_plan files per
locale). Reporting a handful of distinct non-conformant strings plus the file
count they cover is the actionable, auditable unit -- not a 30,000-row dump.

Usage:
  PYTHONPATH=. python3 scripts/localization/check_title_language_conformance.py \\
      --out artifacts/qa/title_language_conformance_<YYYYMMDD_HHMMSS>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

try:
    from yaml import CSafeLoader as YamlLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader as YamlLoader

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.catalog.locale_paths import plan_dirs  # noqa: E402

LOCALE_REGISTRY = REPO / "config" / "localization" / "locale_registry.yaml"
MANGA_SERIES_DIR = REPO / "config" / "source_of_truth" / "manga_series_plans"

TITLE_RE = re.compile(r"^title:\s*(.*)$", re.MULTILINE)
SUBTITLE_RE = re.compile(r"^subtitle:\s*(.*)$", re.MULTILINE)
HEAD_BYTES = 1024

TBD_RE = re.compile(r"^(?:TBD|TODO|FIXME|NULL|NONE|\.\.\.|—|-)?$", re.IGNORECASE)

ILLUSTRATED_REQUIRED_LOCALES = {
    "en_US", "es_US", "es_ES", "de_DE", "it_IT", "hu_HU", "zh_SG", "pt_BR",
}

TRADITIONAL_LOCALES = {"zh_TW", "zh_HK"}
SIMPLIFIED_LOCALES = {"zh_CN", "zh_SG"}
CJK_LOCALES = {"ja_JP", "ko_KR", "zh_CN", "zh_TW", "zh_HK", "zh_SG"}
NON_CJK_LOCALES = {"es_US", "es_ES", "fr_FR", "de_DE", "it_IT", "hu_HU", "pt_BR"}
ALL_TARGET_LOCALES = CJK_LOCALES | NON_CJK_LOCALES  # excludes en_US baseline

_OPENCC_S2T = None
_OPENCC_T2S = None


def _opencc():
    global _OPENCC_S2T, _OPENCC_T2S
    if _OPENCC_S2T is None:
        import opencc

        _OPENCC_S2T = opencc.OpenCC("s2t")
        _OPENCC_T2S = opencc.OpenCC("t2s")
    return _OPENCC_S2T, _OPENCC_T2S


def _yaml_load(path: Path) -> Any:
    return yaml.load(path.read_text(encoding="utf-8"), Loader=YamlLoader)


def _strip_quotes(raw: str) -> str:
    val = raw.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
        val = val[1:-1]
    return val


def _is_tbd(raw: str) -> bool:
    return bool(TBD_RE.match(raw.strip().strip("\"'")))


def _norm_locale(raw: str) -> str:
    return raw.replace("-", "_")


def _has_codepoint_in_ranges(text: str, ranges: list[tuple[int, int]]) -> bool:
    for ch in text:
        cp = ord(ch)
        for lo, hi in ranges:
            if lo <= cp <= hi:
                return True
    return False


# Unicode block ranges (numeric, no literal glyphs).
HIRAGANA_KATAKANA = [(0x3040, 0x30FF), (0x31F0, 0x31FF)]
HANGUL = [(0xAC00, 0xD7A3), (0x1100, 0x11FF), (0x3130, 0x318F)]
CJK_IDEOGRAPH = [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF)]
CJK_OR_KANA_OR_HANGUL = HIRAGANA_KATAKANA + HANGUL + CJK_IDEOGRAPH


def _is_ascii_only(text: str) -> bool:
    return all(ord(ch) < 128 for ch in text)


def _has_non_encodable_char(text: str, codec: str) -> bool:
    """True if any alphabetic char in text cannot round-trip through codec."""
    for ch in text:
        if not ch.isalpha():
            continue
        try:
            ch.encode(codec)
        except UnicodeEncodeError:
            return True
    return False


def _wrong_script_traditional_required(text: str) -> bool:
    """zh-TW/zh-HK: flag if opencc thinks it's simplified AND a char falls
    outside Big5 (classical Traditional charset) -- the AND avoids
    single-glyph false positives from opencc's variant heuristics alone."""
    if not text.strip():
        return False
    s2t, _ = _opencc()
    changed = s2t.convert(text) != text
    if not changed:
        return False
    return _has_non_encodable_char(text, "big5")


def _wrong_script_simplified_required(text: str) -> bool:
    """zh-CN/zh-SG: flag if opencc thinks it's traditional AND a char falls
    outside GB2312 (classical Simplified charset)."""
    if not text.strip():
        return False
    _, t2s = _opencc()
    changed = t2s.convert(text) != text
    if not changed:
        return False
    return _has_non_encodable_char(text, "gb2312")


@dataclass
class ValueFinding:
    value: str
    file_count: int
    reasons: list[str] = field(default_factory=list)


@dataclass
class SurfaceReport:
    locale: str
    surface: str
    field_name: str  # "title" or "subtitle"
    files_checked: int = 0
    distinct_values: int = 0
    conformant_files: int = 0
    non_conformant_files: int = 0
    findings: list[ValueFinding] = field(default_factory=list)
    reason_totals: dict[str, int] = field(default_factory=lambda: defaultdict(int))


def _classify_value(value: str, locale: str, en_reference: set[str]) -> list[str]:
    """Return list of non-conformance reasons; empty list == conformant."""
    if not value.strip():
        return []  # blank handled as TBD/absent upstream, not a language failure here
    reasons = []
    if value in en_reference:
        reasons.append("english_copy_through")
    if locale in CJK_LOCALES:
        if _is_ascii_only(value):
            if "english_copy_through" not in reasons:
                reasons.append("ascii_only_in_cjk_locale")
        else:
            if locale in TRADITIONAL_LOCALES and _wrong_script_traditional_required(value):
                reasons.append("wrong_script_simplified_in_traditional_locale")
            if locale in SIMPLIFIED_LOCALES and _wrong_script_simplified_required(value):
                reasons.append("wrong_script_traditional_in_simplified_locale")
            if locale == "ja_JP" and not _has_codepoint_in_ranges(value, HIRAGANA_KATAKANA + CJK_IDEOGRAPH):
                reasons.append("script_mismatch_ja_review")
            if locale == "ko_KR" and not _has_codepoint_in_ranges(value, HANGUL):
                reasons.append("script_mismatch_ko_review")
    else:
        # Non-CJK Latin-script locale: only the exact-match signal is hard evidence
        # (heuristic word lists are not used -- avoids false positives on proper
        # nouns / cognates). Flag pure placeholder-shape ("Word: Word") ONLY when
        # it also exact-matched english_copy_through above.
        pass
    return reasons


def _extract_title_subtitle(path: Path) -> tuple[str | None, str | None]:
    try:
        chunk = path.read_bytes()[:HEAD_BYTES].decode("utf-8", errors="ignore")
    except OSError:
        return None, None
    tm = TITLE_RE.search(chunk)
    sm = SUBTITLE_RE.search(chunk)
    title = _strip_quotes(tm.group(1)) if tm else None
    subtitle = _strip_quotes(sm.group(1)) if sm else None
    return title, subtitle


def build_en_reference(book_dir: Path, illust_paths: list[Path], manga_paths: list[Path]) -> tuple[set[str], set[str]]:
    titles: set[str] = set()
    subtitles: set[str] = set()
    if book_dir.is_dir():
        with os.scandir(book_dir) as it:
            for ent in it:
                if not ent.name.endswith(".yaml"):
                    continue
                t, s = _extract_title_subtitle(Path(ent.path))
                if t and not _is_tbd(t):
                    titles.add(t)
                if s and not _is_tbd(s):
                    subtitles.add(s)
    for p in illust_paths + manga_paths:
        t, _ = _extract_title_subtitle(p)
        if t and not _is_tbd(t):
            titles.add(t)
    return titles, subtitles


def scan_book_surface(locale: str, en_titles: set[str], en_subtitles: set[str]) -> tuple[SurfaceReport, SurfaceReport]:
    book_dir, _series_dir = plan_dirs(REPO, locale)
    title_counts: dict[str, int] = defaultdict(int)
    subtitle_counts: dict[str, int] = defaultdict(int)
    files_checked = 0
    if book_dir.is_dir():
        with os.scandir(book_dir) as it:
            for ent in it:
                if not ent.name.endswith(".yaml") or not ent.is_file():
                    continue
                files_checked += 1
                t, s = _extract_title_subtitle(Path(ent.path))
                if t and not _is_tbd(t):
                    title_counts[t] += 1
                if s and not _is_tbd(s):
                    subtitle_counts[s] += 1
    title_rep = _build_surface_report(locale, "book", "title", files_checked, title_counts, en_titles)
    sub_rep = _build_surface_report(locale, "book", "subtitle", files_checked, subtitle_counts, en_subtitles)
    return title_rep, sub_rep


def _manga_plan_paths(locale: str) -> list[Path]:
    d = MANGA_SERIES_DIR / locale
    if not d.is_dir():
        return []
    return [Path(p) for p in d.glob("*.yaml") if "_samples" not in str(p)]


def _is_illustrated(path: Path) -> bool:
    name = path.name.lower()
    if "illustrated" in name:
        return True
    try:
        head = path.read_bytes()[:2048].decode("utf-8", errors="ignore")
    except OSError:
        return False
    return "direct_self_help_illustrated" in head


def scan_manga_and_illustrated(locale: str, en_titles: set[str]) -> tuple[SurfaceReport, SurfaceReport]:
    paths = _manga_plan_paths(locale)
    illust_counts: dict[str, int] = defaultdict(int)
    manga_counts: dict[str, int] = defaultdict(int)
    illust_files = 0
    manga_files = 0
    for p in paths:
        t, _ = _extract_title_subtitle(p)
        if t is None or _is_tbd(t):
            continue  # TBD manga titles are explicitly allowed -- not scanned
        if _is_illustrated(p):
            illust_files += 1
            illust_counts[t] += 1
        else:
            manga_files += 1
            manga_counts[t] += 1
    illust_rep = _build_surface_report(locale, "illustrated", "title", illust_files, illust_counts, en_titles)
    manga_rep = _build_surface_report(locale, "manga", "title", manga_files, manga_counts, en_titles)
    return illust_rep, manga_rep


def _build_surface_report(
    locale: str,
    surface: str,
    field_name: str,
    files_checked: int,
    value_counts: dict[str, int],
    en_reference: set[str],
) -> SurfaceReport:
    rep = SurfaceReport(locale=locale, surface=surface, field_name=field_name, files_checked=files_checked)
    rep.distinct_values = len(value_counts)
    for value, count in value_counts.items():
        reasons = _classify_value(value, locale, en_reference)
        hard_reasons = [r for r in reasons if not r.endswith("_review")]
        if hard_reasons:
            rep.non_conformant_files += count
            rep.findings.append(ValueFinding(value=value, file_count=count, reasons=reasons))
            for r in reasons:
                rep.reason_totals[r] += count
        else:
            rep.conformant_files += count
            if reasons:  # review-only flags
                rep.findings.append(ValueFinding(value=value, file_count=count, reasons=reasons))
                for r in reasons:
                    rep.reason_totals[r] += count
    rep.findings.sort(key=lambda f: -f.file_count)
    return rep


def _report_to_dict(rep: SurfaceReport) -> dict[str, Any]:
    return {
        "locale": rep.locale,
        "surface": rep.surface,
        "field": rep.field_name,
        "files_checked": rep.files_checked,
        "distinct_values": rep.distinct_values,
        "conformant_files": rep.conformant_files,
        "non_conformant_files": rep.non_conformant_files,
        "reason_totals": dict(rep.reason_totals),
        "findings": [
            {"value": f.value, "file_count": f.file_count, "reasons": f.reasons}
            for f in rep.findings
        ],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="Output artifact directory (no extension)")
    ap.add_argument(
        "--locales",
        nargs="*",
        default=None,
        help="Subset of locale codes (underscore or hyphen form) to check; default = all 13 non-English",
    )
    args = ap.parse_args(argv)

    if args.locales:
        target_locales = [_norm_locale(x) for x in args.locales]
    else:
        target_locales = sorted(ALL_TARGET_LOCALES)

    en_book_dir, _ = plan_dirs(REPO, "en_US")
    en_illust_paths = [p for p in _manga_plan_paths("en_US") if _is_illustrated(p)]
    en_manga_paths = [p for p in _manga_plan_paths("en_US") if not _is_illustrated(p)]
    en_titles, en_subtitles = build_en_reference(en_book_dir, en_illust_paths, en_manga_paths)
    print(f"[ref] en_US distinct titles={len(en_titles)} subtitles={len(en_subtitles)}", flush=True)

    out_dir = REPO / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    all_reports: list[SurfaceReport] = []
    summary_rows = []
    for locale in target_locales:
        book_title_rep, book_sub_rep = scan_book_surface(locale, en_titles, en_subtitles)
        illust_rep, manga_rep = scan_manga_and_illustrated(locale, en_titles)
        all_reports.extend([book_title_rep, book_sub_rep, illust_rep, manga_rep])
        print(
            f"[{locale}] book.title files={book_title_rep.files_checked} "
            f"non_conformant={book_title_rep.non_conformant_files} "
            f"({book_title_rep.distinct_values} distinct) | "
            f"book.subtitle non_conformant={book_sub_rep.non_conformant_files} | "
            f"illustrated files={illust_rep.files_checked} non_conformant={illust_rep.non_conformant_files} | "
            f"manga(non-TBD) files={manga_rep.files_checked} non_conformant={manga_rep.non_conformant_files}",
            flush=True,
        )
        summary_rows.append(
            {
                "locale": locale,
                "illustrated_required": locale in ILLUSTRATED_REQUIRED_LOCALES,
                "book_title": _report_to_dict(book_title_rep),
                "book_subtitle": _report_to_dict(book_sub_rep),
                "illustrated_title": _report_to_dict(illust_rep),
                "manga_title_non_tbd": _report_to_dict(manga_rep),
            }
        )

    (out_dir / "title_language_conformance.json").write_text(
        json.dumps({"generated_at": datetime.now().isoformat(), "locales": summary_rows}, indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Title/Subtitle Language-Conformance -- live gap (not PLAN-existence)",
        "",
        f"- Date: {datetime.now().isoformat()}",
        "- Authority: this checker closes the gap named in "
        "docs/specs/WORLDWIDE_PLAN_COMPLETENESS_V1_SPEC.md (PLAN-existence != language-conformance).",
        "",
        "| locale | book title non-conf/checked | book subtitle non-conf/checked | illustrated non-conf/checked | manga(non-TBD) non-conf/checked |",
        "|---|---|---|---|---|",
    ]
    for row in summary_rows:
        bt, bs, il, mg = row["book_title"], row["book_subtitle"], row["illustrated_title"], row["manga_title_non_tbd"]
        lines.append(
            f"| {row['locale']} | {bt['non_conformant_files']}/{bt['files_checked']} | "
            f"{bs['non_conformant_files']}/{bs['files_checked']} | "
            f"{il['non_conformant_files']}/{il['files_checked']} | "
            f"{mg['non_conformant_files']}/{mg['files_checked']} |"
        )
    (out_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nWrote {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
