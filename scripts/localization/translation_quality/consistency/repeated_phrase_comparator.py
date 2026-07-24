#!/usr/bin/env python3
"""Repeated-phrase comparator.

Finds recurring English source phrases (n-grams appearing across multiple
CANONICAL.txt files -- motif phrases, coined terms) and reports every
distinct localized rendering used for each, for Claude to scan for drift.
Deterministic extraction/comparison only.

Usage:
    python3 scripts/localization/translation_quality/consistency/repeated_phrase_comparator.py \\
        --locale zh-CN --atoms-root atoms --min-occurrences 3 --ngram-size 3 5 \\
        --out artifacts/qa/repeated_phrases_zh_cn.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]

WORD_RE = re.compile(r"[A-Za-z']+")
BODY_RE = re.compile(r"^##\s+[A-Za-z0-9_]+\s+v\d+\s*\n---\s*\n([\s\S]*?)\n---", re.MULTILINE)


def _extract_bodies(text: str) -> list[str]:
    """Best-effort body-text extraction per header block, tolerant of the
    empty-metadata double-delimiter shape (see structural_validator.py
    parse_blocks for the stricter header-identity parser used elsewhere;
    this comparator only needs prose spans, not header bookkeeping)."""
    return [m.group(1).strip() for m in BODY_RE.finditer(text) if m.group(1).strip()]


def _ngrams(words: list[str], n: int) -> list[str]:
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def find_repeated_source_phrases(
    atoms_root: Path,
    *,
    ngram_sizes: list[int],
    min_occurrences: int,
    max_files: int | None = None,
) -> dict[str, dict[str, Any]]:
    """Scan English source CANONICAL.txt files (excludes locales/ subtrees)
    for n-gram phrases repeated across >= min_occurrences distinct files."""
    phrase_files: dict[str, set[str]] = defaultdict(set)
    files = [p for p in atoms_root.rglob("CANONICAL.txt") if "/locales/" not in str(p)]
    if max_files:
        files = files[:max_files]

    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(path.relative_to(REPO_ROOT))
        for body in _extract_bodies(text):
            words = WORD_RE.findall(body.lower())
            for n in ngram_sizes:
                for phrase in _ngrams(words, n):
                    phrase_files[phrase].add(rel)

    return {
        phrase: {"file_count": len(paths), "files": sorted(paths)[:20]}
        for phrase, paths in phrase_files.items()
        if len(paths) >= min_occurrences
    }


def localized_renderings_for_phrase(
    atoms_root: Path, locale: str, source_files: list[str]
) -> dict[str, int]:
    """For a repeated source phrase's file set, collect the distinct set of
    localized body texts at the matching path -- returns {rendering_hash_or_snippet: count}
    left as a raw snippet Counter for a human/agent to read, not judged here."""
    renderings: Counter[str] = Counter()
    for src_rel in source_files:
        src_path = REPO_ROOT / src_rel
        localized_path = src_path.parent / "locales" / locale / "CANONICAL.txt"
        if not localized_path.is_file():
            continue
        try:
            text = localized_path.read_text(encoding="utf-8")
        except OSError:
            continue
        bodies = _extract_bodies(text)
        if bodies:
            # first body as a representative snippet (truncated) -- full
            # comparison across every block is out of scope for this
            # deterministic pass; flags candidates for a human/agent read.
            renderings[bodies[0][:80]] += 1
    return dict(renderings)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--locale", required=True)
    ap.add_argument("--atoms-root", type=Path, default=REPO_ROOT / "atoms")
    ap.add_argument("--ngram-size", type=int, nargs="+", default=[4])
    ap.add_argument("--min-occurrences", type=int, default=3)
    ap.add_argument("--max-files", type=int, default=None, help="Cap source files scanned (dev/smoke use)")
    ap.add_argument("--top-n", type=int, default=50, help="Only report the N most-repeated phrases")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    repeated = find_repeated_source_phrases(
        args.atoms_root,
        ngram_sizes=args.ngram_size,
        min_occurrences=args.min_occurrences,
        max_files=args.max_files,
    )
    top = dict(sorted(repeated.items(), key=lambda kv: -kv[1]["file_count"])[: args.top_n])

    report: dict[str, Any] = {}
    for phrase, info in top.items():
        report[phrase] = {
            **info,
            "localized_renderings": localized_renderings_for_phrase(args.atoms_root, args.locale, info["files"]),
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}: {len(report)} repeated phrases (of {len(repeated)} found)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
