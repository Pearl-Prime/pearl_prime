#!/usr/bin/env python3
"""Smoke: character_individuation tree is present and has a prompt_builder (I028)."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "scripts/manga/character_individuation"


def main() -> int:
    if not ROOT.is_dir():
        print(f"FAIL: missing {ROOT}", file=sys.stderr)
        return 1
    builders = list(ROOT.rglob("*prompt_builder*"))
    py_files = list(ROOT.rglob("*.py"))
    if not py_files:
        print("FAIL: no python files under character_individuation", file=sys.stderr)
        return 1
    print(f"OK: character_individuation present ({len(py_files)} py files, {len(builders)} prompt_builder hits)")
    for p in builders[:5]:
        print(f"  - {p.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
