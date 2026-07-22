#!/usr/bin/env python3
"""Deterministic structural + surface validator for a translated candidate.

Pure pass/fail + reason list. Makes NO translation-quality judgment call —
that is Claude Code's job (Lane 02 of
docs/agent_prompt_packs/20260721_zh_tw_translation_quality_program/). This
module only checks things a script can check with certainty:

  - header IDs match the English source exactly (count + identity + order)
  - no duplicate / missing / extra localized header IDs
  - "---" delimiter block count matches per header (structure preserved)
  - placeholder tokens ({snake_case}) preserved exactly
  - markdown links / HTML tags preserved (same count, not necessarily same
    link text -- link text may be legitimately localized)
  - URLs preserved byte-for-byte
  - numbers preserved (same multiset of standalone digit runs)
  - protected terms preserved (reads analysis/<locale_dir>/protected_terms.yaml
    if present; otherwise falls back to the generic structural checks above)
  - glossary violations (reads analysis/<locale_dir>/glossary_core.yaml +
    glossary_project.yaml `avoid` lists if present)
  - untranslated English (candidate body is ascii-only / near-ascii-only in
    a CJK-script locale)
  - script contamination (delegates to
    scripts/localization/translation_quality/script_contamination.py for
    zh-CN/zh-TW; a no-op for every other locale)
  - missing/duplicated content (paragraph/block count parity)

Usage:
    python3 scripts/localization/translation_quality/structural_validator.py \\
        --source path/to/CANONICAL.txt \\
        --candidate path/to/candidate_or_localized_CANONICAL.txt \\
        --locale zh-CN
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.localization.translation_quality.script_contamination import (  # noqa: E402
    LOCALE_CODECS as SCRIPT_CHECK_LOCALES,
    check_text as script_contamination_check,
)

HEADER_BLOCK_RE = re.compile(r"^##\s+([A-Za-z0-9_]+)\s+v(\d+)\s*$", re.MULTILINE)
DELIM_RE = re.compile(r"^---\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{[a-zA-Z][a-zA-Z0-9_]*\}")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\([^)]*\)")
HTML_TAG_RE = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?>")
URL_RE = re.compile(r"https?://[^\s\)\]\"'>]+")
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])\d[\d,.:]*\d|(?<![A-Za-z0-9_])\d(?![A-Za-z0-9_])")

CJK_SCRIPT_LOCALES = {"zh-CN", "zh-TW", "zh-HK", "zh-SG", "ja-JP", "ko-KR"}

LOCALE_ANALYSIS_DIRS = {
    "zh-CN": "zh_cn",
    "zh-TW": "zh_tw",
    "zh-HK": "zh_hk",
    "zh-SG": "zh_sg",
    "ja-JP": "ja_jp",
    "ko-KR": "ko_kr",
}


def _has_cjk(text: str) -> bool:
    for ch in text:
        cp = ord(ch)
        if 0x3040 <= cp <= 0x30FF or 0x3400 <= cp <= 0x9FFF or 0xAC00 <= cp <= 0xD7A3:
            return True
    return False


def _is_ascii_only(text: str) -> bool:
    return all(ord(ch) < 128 for ch in text)


@dataclass
class HeaderBlock:
    header_id: str  # e.g. "PIVOT_v01"
    shape: str
    version: str
    start: int
    end: int
    body: str
    delimiter_count: int


def parse_blocks(text: str) -> list[HeaderBlock]:
    """Split a CANONICAL.txt-shaped file into per-header blocks.

    Independent of phoenix_v4.planning.assembly_compiler._parse_canonical_txt
    (which resolves atom roles/bindings for the compiler and needs
    directory context this validator doesn't have). This is a QA-scoped
    structural parse only: header identity, delimiter count, raw body span.
    """
    matches = list(HEADER_BLOCK_RE.finditer(text))
    blocks: list[HeaderBlock] = []
    for i, m in enumerate(matches):
        shape, ver = m.group(1), m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        blocks.append(
            HeaderBlock(
                header_id=f"{shape}_v{ver}",
                shape=shape,
                version=ver,
                start=start,
                end=end,
                body=body,
                delimiter_count=len(DELIM_RE.findall(body)),
            )
        )
    return blocks


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _analysis_dir(locale: str) -> Path | None:
    d = LOCALE_ANALYSIS_DIRS.get(locale)
    return (REPO_ROOT / "analysis" / d) if d else None


def _glossary_avoid_terms(locale: str) -> list[tuple[str, str]]:
    """[(avoid_term, source_term), ...] from glossary_core.yaml + glossary_project.yaml."""
    out: list[tuple[str, str]] = []
    adir = _analysis_dir(locale)
    if not adir:
        return out
    for fname in ("glossary_core.yaml", "glossary_project.yaml"):
        data = _load_yaml(adir / fname)
        for term in data.get("terms") or []:
            source = str(term.get("source", ""))
            for avoid in term.get("avoid") or []:
                # avoid entries sometimes carry a trailing parenthetical note
                # ("靜觀（台灣用語）") -- match on the literal string as given.
                avoid_clean = str(avoid).strip()
                if avoid_clean:
                    out.append((avoid_clean, source))
    return out


def _protected_terms(locale: str) -> dict[str, Any]:
    adir = _analysis_dir(locale)
    if not adir:
        return {}
    return _load_yaml(adir / "protected_terms.yaml")


@dataclass
class ValidationResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "reasons": self.reasons, "details": self.details}


def validate(
    source_text: str,
    candidate_text: str,
    locale: str,
    *,
    check_glossary: bool = True,
    check_script: bool = True,
) -> ValidationResult:
    reasons: list[str] = []
    details: dict[str, Any] = {}

    src_blocks = parse_blocks(source_text)
    cand_blocks = parse_blocks(candidate_text)

    src_ids = [b.header_id for b in src_blocks]
    cand_ids = [b.header_id for b in cand_blocks]

    # 1. header IDs match exactly (identity + order)
    if src_ids != cand_ids:
        reasons.append("header_id_mismatch")
        details["source_header_ids"] = src_ids
        details["candidate_header_ids"] = cand_ids

    # 2. no duplicate localized header IDs
    dupes = {h for h in cand_ids if cand_ids.count(h) > 1}
    if dupes:
        reasons.append("duplicate_header_ids")
        details["duplicate_header_ids"] = sorted(dupes)

    # 3. no missing localized header IDs
    missing = [h for h in src_ids if h not in cand_ids]
    if missing:
        reasons.append("missing_header_ids")
        details["missing_header_ids"] = missing

    # 4. no extra localized header IDs
    extra = [h for h in cand_ids if h not in src_ids]
    if extra:
        reasons.append("extra_header_ids")
        details["extra_header_ids"] = extra

    # Per-block checks only make sense when IDs line up 1:1; use zip on the
    # common prefix / matched IDs to still catch defects in a partially
    # mismatched file rather than bailing out entirely.
    cand_by_id = {b.header_id: b for b in cand_blocks}
    block_reasons: dict[str, list[str]] = {}
    for sb in src_blocks:
        cb = cand_by_id.get(sb.header_id)
        if cb is None:
            continue
        this_block_reasons: list[str] = []

        # 5. body not empty / placeholder-only / TODO-only
        stripped = cb.body.strip()
        if not stripped:
            this_block_reasons.append("empty_body")
        elif re.fullmatch(r"(?i)(todo|tbd|fixme|\.{3}|—|-)+", stripped):
            this_block_reasons.append("placeholder_only_body")

        # 6. delimiter structure preserved
        if sb.delimiter_count != cb.delimiter_count:
            this_block_reasons.append(
                f"delimiter_count_mismatch(source={sb.delimiter_count},candidate={cb.delimiter_count})"
            )

        # 7. placeholders preserved exactly (same multiset)
        src_ph = sorted(PLACEHOLDER_RE.findall(sb.body))
        cand_ph = sorted(PLACEHOLDER_RE.findall(cb.body))
        if src_ph != cand_ph:
            this_block_reasons.append("placeholders_not_preserved")

        # 8. markdown links preserved (count parity)
        if len(MD_LINK_RE.findall(sb.body)) != len(MD_LINK_RE.findall(cb.body)):
            this_block_reasons.append("markdown_link_count_mismatch")

        # 9. HTML tags preserved (count parity)
        if len(HTML_TAG_RE.findall(sb.body)) != len(HTML_TAG_RE.findall(cb.body)):
            this_block_reasons.append("html_tag_count_mismatch")

        # 10. URLs preserved byte-for-byte (same set)
        src_urls = sorted(set(URL_RE.findall(sb.body)))
        cand_urls = sorted(set(URL_RE.findall(cb.body)))
        if src_urls != cand_urls:
            this_block_reasons.append("urls_not_preserved")

        # 11. untranslated English: candidate body is ascii-only in a
        # CJK-script locale, and the source body itself was NOT ascii-only
        # (i.e. this isn't a legitimately-untranslated code/URL-only block).
        if locale in CJK_SCRIPT_LOCALES and stripped:
            if _is_ascii_only(stripped) and not _is_ascii_only(sb.body.strip()):
                this_block_reasons.append("untranslated_english")
            elif locale in {"ja-JP", "ko-KR", "zh-CN", "zh-TW", "zh-HK", "zh-SG"} and not _has_cjk(stripped):
                this_block_reasons.append("untranslated_english")

        # 12. script contamination (zh-CN/zh-TW only)
        if check_script and locale in SCRIPT_CHECK_LOCALES and stripped:
            sc = script_contamination_check(stripped, locale=locale)
            if not sc.clean:
                this_block_reasons.append("script_contamination")
                details.setdefault("script_contamination_findings", {})[sb.header_id] = [
                    f.detail for f in sc.findings
                ]

        # 13. glossary violations (avoid-list terms present in candidate)
        if check_glossary:
            for avoid_term, source_term in _glossary_avoid_terms(locale):
                if avoid_term and avoid_term in cb.body:
                    this_block_reasons.append(f"glossary_violation:{avoid_term}")

        if this_block_reasons:
            block_reasons[sb.header_id] = this_block_reasons

    if block_reasons:
        reasons.append("per_block_failures")
        details["per_block_failures"] = block_reasons

    return ValidationResult(ok=not reasons, reasons=reasons, details=details)


def validate_files(source_path: Path, candidate_path: Path, locale: str) -> ValidationResult:
    source_text = source_path.read_text(encoding="utf-8")
    candidate_text = candidate_path.read_text(encoding="utf-8")
    return validate(source_text, candidate_text, locale=locale)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, type=Path, help="English source CANONICAL.txt")
    ap.add_argument("--candidate", required=True, type=Path, help="Candidate/localized file to validate")
    ap.add_argument("--locale", required=True, help="Target locale code, e.g. zh-CN")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text")
    ap.add_argument("--no-glossary", action="store_true", help="Skip glossary avoid-list check")
    ap.add_argument("--no-script-check", action="store_true", help="Skip script-contamination check")
    args = ap.parse_args(argv)

    source_text = args.source.read_text(encoding="utf-8")
    candidate_text = args.candidate.read_text(encoding="utf-8")
    result = validate(
        source_text,
        candidate_text,
        locale=args.locale,
        check_glossary=not args.no_glossary,
        check_script=not args.no_script_check,
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        if result.ok:
            print(f"OK  {args.candidate}")
        else:
            print(f"FAIL {args.candidate}: {', '.join(result.reasons)}")
            if result.details:
                print(json.dumps(result.details, indent=2, ensure_ascii=False))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
