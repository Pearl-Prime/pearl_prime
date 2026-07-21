#!/usr/bin/env python3
"""
G-ORIENT — Chapter-1 Orient machine approximation.

Per PEARL_PRIME_PERFECT_BOOKS_SPEC.md #3.B: "Ch1 first 120 words must contain
>=1 body/scene anchor from approved lexicon OR SCENE atom provenance" ->
WARN->escalate to authored-candidate eligibility (Layer 2), NOT a Layer-1 hard
gate. This script never returns HARD_FAIL; default exit is 0 (report-only)
unless --strict is passed (Layer-2 eligibility check context).

No approved lexicon SSOT existed prior to this gate (Wave-2 lane 04
discovery). A minimal one was authored at
config/quality/orient_body_scene_lexicon.yaml, seeded from the frozen
flagship Ch1 exemplar + the existing HOOK-SCENE-FIRST-01/F11 scene-first
vocabulary in phoenix_v4/quality/register_gate.py (cited, not re-derived).

SCENE-atom provenance path: when a book_outline.json (phoenix_v4/qa/book_outline.py
schema) is supplied via --book-outline and chapter 1's `slot_types_landed`
contains "SCENE", the anchor requirement is satisfied via provenance even if
the lexicon word-match misses (e.g. paraphrased scene language).

Authority: artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md #3.B (G-ORIENT row)

Usage:
  PYTHONPATH=. python3 scripts/ci/check_orient_ch1_scene_anchor.py  # integrity mode
  PYTHONPATH=. python3 scripts/ci/check_orient_ch1_scene_anchor.py --book path/to/book.txt
  PYTHONPATH=. python3 scripts/ci/check_orient_ch1_scene_anchor.py --book path/to/book.txt \\
      --book-outline path/to/book_outline.json
  PYTHONPATH=. python3 scripts/ci/check_orient_ch1_scene_anchor.py --book path/to/book.txt --strict

Exit: 0 pass/WARN (default); 1 WARN under --strict; 1 on missing input errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.register_gate import _split_chapters  # noqa: E402

DEFAULT_LEXICON_PATH = REPO_ROOT / "config" / "quality" / "orient_body_scene_lexicon.yaml"
ORIENT_WORD_WINDOW = 120


def load_lexicon(path: Path = DEFAULT_LEXICON_PATH) -> set[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    words: set[str] = set()
    for key in ("body_anchors", "scene_anchors"):
        for w in data.get(key) or []:
            words.add(str(w).strip().lower())
    return words


def _first_n_words(text: str, n: int) -> str:
    words = text.split()
    return " ".join(words[:n])


def ch1_first_words(book_text: str, *, n: int = ORIENT_WORD_WINDOW) -> str:
    chapters = _split_chapters(book_text)
    for ch_num, ch_body in chapters:
        if ch_num == 1:
            return _first_n_words(ch_body, n)
    # No "Chapter 1" header found (e.g. single-chapter fixture / no headers):
    # treat whole text as chapter 1 (mirrors register_gate's ch_num=0 fallback).
    if chapters:
        return _first_n_words(chapters[0][1], n)
    return _first_n_words(book_text, n)


def lexicon_anchor_hit(window_text: str, lexicon: set[str]) -> str | None:
    tokens = re.findall(r"[A-Za-z']+", window_text.lower())
    for tok in tokens:
        if tok in lexicon:
            return tok
    return None


def scene_atom_provenance_hit(book_outline: dict[str, Any] | None) -> bool:
    if not book_outline:
        return False
    for ch in book_outline.get("chapters") or []:
        if not isinstance(ch, dict):
            continue
        try:
            number = int(ch.get("number") or 0)
        except (TypeError, ValueError):
            continue
        if number != 1:
            continue
        slot_types = [str(s).upper() for s in (ch.get("slot_types_landed") or [])]
        if "SCENE" in slot_types:
            return True
    return False


def check_book(
    book_path: Path,
    *,
    lexicon: set[str],
    book_outline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = book_path.read_text(encoding="utf-8", errors="replace")
    window = ch1_first_words(text)
    anchor = lexicon_anchor_hit(window, lexicon)
    provenance = scene_atom_provenance_hit(book_outline)
    satisfied = bool(anchor) or provenance
    return {
        "book": str(book_path),
        "window": window,
        "anchor_hit": anchor,
        "scene_atom_provenance": provenance,
        "satisfied": satisfied,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G-ORIENT Ch1 body/scene anchor check")
    ap.add_argument("--book", type=Path, default=None)
    ap.add_argument("--book-outline", type=Path, default=None)
    ap.add_argument("--lexicon", type=Path, default=DEFAULT_LEXICON_PATH)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Escalate a WARN to a non-zero exit (Layer-2 authored-candidate eligibility check)",
    )
    args = ap.parse_args(argv)

    if args.book is None:
        # Integrity mode: confirm lexicon SSOT loads and has content.
        lexicon = load_lexicon(args.lexicon)
        assert lexicon, "G-ORIENT lexicon must not be empty"
        print(
            f"G-ORIENT: PASS (integrity) — lexicon loaded "
            f"({len(lexicon)} anchor words) from {args.lexicon}; no --book provided"
        )
        return 0

    if not args.book.is_file():
        print(f"G-ORIENT: FAIL — book path missing: {args.book}", file=sys.stderr)
        return 1

    lexicon = load_lexicon(args.lexicon)
    outline = None
    if args.book_outline is not None:
        if args.book_outline.is_file():
            outline = json.loads(args.book_outline.read_text(encoding="utf-8"))
        else:
            print(f"G-ORIENT: NOTE — --book-outline given but missing: {args.book_outline}")

    result = check_book(args.book, lexicon=lexicon, book_outline=outline)

    if result["satisfied"]:
        via = f"lexicon anchor {result['anchor_hit']!r}" if result["anchor_hit"] else "SCENE-atom provenance"
        print(f"G-ORIENT: PASS — Ch1 first {ORIENT_WORD_WINDOW} words satisfied via {via}")
        return 0

    msg = (
        f"{args.book}: G-ORIENT WARN — Ch1 first {ORIENT_WORD_WINDOW} words contain no "
        f"approved body/scene lexicon anchor and no SCENE-atom provenance "
        f"(authored-candidate eligibility at risk). window={result['window'][:200]!r}"
    )
    print(f"::warning::{msg}")
    if args.strict:
        print("G-ORIENT: FAIL (--strict)", file=sys.stderr)
        print(f"  - {msg}", file=sys.stderr)
        return 1

    print("G-ORIENT: WARN (non-blocking; Layer-1 unaffected)")
    print(f"  - {msg}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
