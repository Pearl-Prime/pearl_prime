#!/usr/bin/env python3
"""
Standalone per-atom validator for browser translation results.

Called by the queue server on each POST /submit. Returns JSON:
    {"passed": true, "gates_failed": [], "reprompt": null}
    {"passed": false, "gates_failed": ["G1"], "reprompt": "Your translation is too short..."}

Can also be run from the command line for manual testing.

Usage:
    python3 scripts/translation/browser_validate.py \
        --source <file> --translation <file> --locale zh-TW
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ── format marker patterns ────────────────────────────────────────────────

_VARIANT_MARKER_RE = re.compile(r"^---\s+variant:\s+v\d+", re.MULTILINE)
_SEPARATOR_RE = re.compile(r"^---$", re.MULTILINE)
_HEADER_RE = re.compile(r"^##\s+[A-Z_]+\s+v\d+", re.MULTILINE)
_ENGLISH_SENTENCE_RE = re.compile(r"\b[A-Za-z]{4,}(?:\s+[A-Za-z]{2,}){3,}\b")

# Second-person markers
_ZH_SECOND_PERSON = "你"
_JA_SECOND_PERSON = re.compile(r"あなた")

# Commentary patterns (LLM meta-narration)
_COMMENTARY_RE = re.compile(
    r"(Here is the translation|注意：|翻訳：|翻譯：|以下是翻|以下为翻|Translation:)",
    re.IGNORECASE,
)

# Prose atoms that need second-person voice (exclude COMPRESSION, metadata-heavy types)
_PROSE_TYPES = {"HOOK", "PIVOT", "THREAD", "STORY", "TAKEAWAY", "PERMISSION", "SCENE"}


def _count_format_markers(text: str) -> dict[str, int]:
    return {
        "variant_markers": len(_VARIANT_MARKER_RE.findall(text)),
        "headers": len(_HEADER_RE.findall(text)),
        "separators": len(_SEPARATOR_RE.findall(text)),
    }


def _strip_markers(text: str) -> str:
    """Remove format marker lines, leaving only prose."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r"^---(\s+variant:\s+v\d+)?$", stripped):
            continue
        if re.match(r"^##\s+[A-Z_]+\s+v\d+", stripped):
            continue
        if re.match(r"^[a-z_]+:\s+", stripped):  # YAML metadata
            continue
        lines.append(line)
    return "\n".join(lines)


# ── gate functions ────────────────────────────────────────────────────────


def gate_g1_length(source: str, translated: str) -> tuple[bool, str]:
    """G1: Response length 25–200% of source."""
    src_len = len(source.strip())
    tgt_len = len(translated.strip())
    if src_len == 0:
        return True, ""
    ratio = tgt_len / src_len
    if ratio < 0.25:
        min_chars = int(src_len * 0.25)
        max_chars = int(src_len * 2.0)
        return False, (
            f"Your translation is too short. The original is {src_len} characters; "
            f"your translation should be {min_chars}–{max_chars} characters. "
            f"Please retranslate the full text — do not summarize or skip any section.\n\n"
            f"[ORIGINAL TEXT]\n{source}"
        )
    if ratio > 2.0:
        return False, (
            f"Your translation is too long ({tgt_len} chars vs {src_len} source chars). "
            f"Please retranslate without adding extra content.\n\n"
            f"[ORIGINAL TEXT]\n{source}"
        )
    return True, ""


def gate_g2_format(source: str, translated: str) -> tuple[bool, str]:
    """G2: All format markers present and unchanged."""
    src_counts = _count_format_markers(source)
    tgt_counts = _count_format_markers(translated)

    issues = []
    if src_counts["variant_markers"] > 0 and tgt_counts["variant_markers"] < src_counts["variant_markers"]:
        issues.append(f"variant markers (expected {src_counts['variant_markers']}, got {tgt_counts['variant_markers']})")
    if src_counts["headers"] > 0 and tgt_counts["headers"] < src_counts["headers"]:
        issues.append(f"## headers (expected {src_counts['headers']}, got {tgt_counts['headers']})")

    if issues:
        return False, (
            "Your translation broke the format markers. Copy these markers EXACTLY, character "
            "for character — do not translate them:\n"
            '  - Lines like "---" must remain "---"\n'
            '  - Lines like "## HOOK v01" must remain "## HOOK v01"\n'
            f"  - Missing: {', '.join(issues)}\n\n"
            f"Please retranslate:\n[ORIGINAL TEXT]\n{source}"
        )
    return True, ""


def gate_g3_english_leakage(source: str, translated: str) -> tuple[bool, str]:
    """G3: No English prose sentences in output."""
    prose = _strip_markers(translated)
    matches = _ENGLISH_SENTENCE_RE.findall(prose)
    if matches:
        return False, (
            "Your translation still contains English text. Translate ALL prose — including "
            "body sensations, dialogue, and instructions. Do not leave any English words.\n\n"
            f"Please retranslate:\n[ORIGINAL TEXT]\n{source}"
        )
    return True, ""


def gate_g4_commentary(source: str, translated: str) -> tuple[bool, str]:
    """G4: No LLM meta-commentary."""
    match = _COMMENTARY_RE.search(translated)
    if match:
        return False, (
            f"Your response contains commentary ('{match.group()}') — remove it. "
            "Reply ONLY with the translated text. No preamble. No explanation.\n\n"
            f"Please retranslate:\n[ORIGINAL TEXT]\n{source}"
        )
    return True, ""


def gate_g5_second_person(source: str, translated: str, locale: str, atom_type: str) -> tuple[bool, str]:
    """G5: Second-person markers present for prose atoms."""
    if atom_type.upper() not in _PROSE_TYPES:
        return True, ""
    has_you = bool(re.search(r"\byou\b", source, re.IGNORECASE))
    if not has_you:
        return True, ""

    if locale in ("zh-TW", "zh-CN") and _ZH_SECOND_PERSON not in translated:
        return False, (
            "Your translation is missing 「你」. Address the reader directly as 「你」 — "
            "not 「人們」 or third person.\n\n"
            f"Please retranslate:\n[ORIGINAL TEXT]\n{source}"
        )
    if locale == "ja-JP" and not _JA_SECOND_PERSON.search(translated):
        # Japanese often omits explicit pronoun — treat as soft pass
        return True, ""
    return True, ""


def gate_g6_compression(source: str, translated: str, atom_type: str) -> tuple[bool, str]:
    """G6: COMPRESSION atoms must be identical to source."""
    if atom_type.upper() != "COMPRESSION":
        return True, ""
    if translated.strip() != source.strip():
        return False, "COMPRESSION atom must be written as-is (no LLM translation)."
    return True, ""


# ── main validate function ────────────────────────────────────────────────


def validate(
    source: str,
    translated: str,
    locale: str,
    atom_type: str = "HOOK",
) -> dict:
    """
    Run all gates. Returns:
        {"passed": bool, "gates_failed": [...], "reprompt": str|None}
    """
    gates = [
        ("G1", gate_g1_length(source, translated)),
        ("G2", gate_g2_format(source, translated)),
        ("G3", gate_g3_english_leakage(source, translated)),
        ("G4", gate_g4_commentary(source, translated)),
        ("G5", gate_g5_second_person(source, translated, locale, atom_type)),
        ("G6", gate_g6_compression(source, translated, atom_type)),
    ]

    failed = [(name, msg) for name, (passed, msg) in gates if not passed]
    if not failed:
        return {"passed": True, "gates_failed": [], "reprompt": None}

    first_gate, reprompt = failed[0]
    return {
        "passed": False,
        "gates_failed": [name for name, _ in failed],
        "reprompt": reprompt,
    }


# ── CLI ───────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a single atom translation.")
    parser.add_argument("--source", type=Path, required=True, help="Source atom file")
    parser.add_argument("--translation", type=Path, required=True, help="Translated atom file")
    parser.add_argument("--locale", required=True, choices=["zh-TW", "zh-CN", "ja-JP"])
    parser.add_argument("--atom-type", default="HOOK", help="Atom type (HOOK, PIVOT, COMPRESSION, ...)")
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    translated = args.translation.read_text(encoding="utf-8")

    result = validate(source, translated, args.locale, args.atom_type)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
