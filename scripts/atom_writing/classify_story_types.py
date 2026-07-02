#!/usr/bin/env python3
"""Heuristic-first story_type classifier + backfill for persona STORY pools.

docs/STORY_TYPES_AND_STRUCTURES.md defines 5 story types; the 218 persona pools
(atoms/<persona>/<topic>/STORY/CANONICAL.txt) carry MECHANISM_DEPTH/IDENTITY_STAGE/
COST_TYPE but no story_type. This assigns one deterministically (Phase-3 scope,
docs/STORY_TYPE_ENFORCEMENT_SCOPE_2026-07-03.md, decision #2 = heuristic first-pass)
and, in --write mode, injects it into each block's metadata as:

    STORY_TYPE: <type>
    STORY_TYPE_SOURCE: heuristic_v1   # machine-classified, reviewable/overridable

The CANONICAL.txt parser ignores unknown meta keys, so this is inert until a
reader (the linter / selector) consumes it — forward-compatible, non-breaking.
Deterministic; no LLM.

Usage:
  PYTHONPATH=. python3 scripts/atom_writing/classify_story_types.py            # dry-run report
  PYTHONPATH=. python3 scripts/atom_writing/classify_story_types.py --write    # backfill in place
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.story_atom_lint import _has_named_person  # noqa: E402

# Block: ## STORY vNN \n --- \n meta \n --- \n body(until next ## or EOF)
_BLOCK_RE = re.compile(
    r"(##\s*STORY\s*v\d+\s*\n---\s*\n)(?P<meta>.*?)(\n---\s*\n)(?P<body>.*?)(?=\n##\s|\Z)",
    re.DOTALL,
)


def classify(prose: str) -> str:
    """Assign one of the 5 story types by deterministic structure heuristics."""
    t = prose.strip()
    low = t.lower()
    if re.search(
        r"\b(in the .{0,25}tradition|there is (a|an old) story|the zen master|"
        r"a parable|in the teaching of)\b",
        low,
    ):
        return "parable"
    if ('"' in t or "“" in t) and re.search(r"\b(teacher|master|roshi|rinpoche|guru)\b", low) \
            and re.search(r"\b(walked (in|past)|in the doorway|sat across)\b", low):
        return "recognition_exchange"
    you = len(re.findall(r"\byou\b|\byour\b", low))
    third = len(re.findall(r"\b(she|he|her|him|his)\b", low))
    if you >= 3 and you > third:
        return "direct_teaching"
    if third >= 2 or _has_named_person(t):
        return "character_study"
    return "atmospheric"


def story_pools() -> list[Path]:
    return sorted((REPO_ROOT / "atoms").glob("*/*/STORY/CANONICAL.txt"))


def _inject(meta: str, story_type: str) -> str:
    lines = [ln for ln in meta.splitlines() if not re.match(r"\s*STORY_TYPE(_SOURCE)?\s*:", ln)]
    lines.append(f"STORY_TYPE: {story_type}")
    lines.append("STORY_TYPE_SOURCE: heuristic_v1")
    return "\n".join(lines)


def process_file(path: Path, write: bool) -> tuple[Counter, int, int]:
    text = path.read_text(encoding="utf-8")
    dist: Counter = Counter()
    cs_named = cs_unnamed = 0
    n_blocks = 0

    def repl(m: re.Match) -> str:
        nonlocal cs_named, cs_unnamed, n_blocks
        body = m.group("body").strip()
        st = classify(body)
        dist[st] += 1
        n_blocks += 1
        if st == "character_study":
            if _has_named_person(body):
                cs_named += 1
            else:
                cs_unnamed += 1
        if not write:
            return m.group(0)
        new_meta = _inject(m.group("meta"), st)
        return m.group(1) + new_meta + m.group(3) + m.group("body")

    new_text = _BLOCK_RE.sub(repl, text)
    if write and new_text != text:
        # round-trip safety: block count preserved + STORY_TYPE now present
        after = _BLOCK_RE.findall(new_text)
        if len(after) != n_blocks:
            raise RuntimeError(f"block count changed in {path}: {n_blocks} -> {len(after)}")
        if new_text.count("STORY_TYPE:") < n_blocks:
            raise RuntimeError(f"STORY_TYPE not injected into all blocks in {path}")
        path.write_text(new_text, encoding="utf-8")
    return dist, cs_named, cs_unnamed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Inject STORY_TYPE in place (default: dry-run)")
    args = ap.parse_args()

    pools = story_pools()
    total = Counter()
    cs_named = cs_unnamed = 0
    for p in pools:
        d, n, u = process_file(p, write=args.write)
        total.update(d)
        cs_named += n
        cs_unnamed += u

    n_variants = sum(total.values())
    mode = "WROTE" if args.write else "DRY-RUN"
    print(f"[{mode}] {n_variants} story variants across {len(pools)} pools:")
    for k, v in total.most_common():
        print(f"  {k:<22}{v:>5}  ({v / n_variants * 100:.0f}%)")
    print(f"  character_study NAMED:   {cs_named}")
    print(f"  character_study UNNAMED: {cs_unnamed}  (→ CHARACTER_STUDY_UNNAMED WARN worklist)")
    if not args.write:
        print("\n(dry-run — no files modified; pass --write to backfill)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
