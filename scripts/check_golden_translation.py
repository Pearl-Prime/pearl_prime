#!/usr/bin/env python3
"""
Golden translation regression: expected substrings from
config/localization/quality_contracts/golden_translation_regression.yaml
must appear in the corresponding translated atom CANONICAL.txt files.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_PATH = REPO_ROOT / "config/localization/quality_contracts/golden_translation_regression.yaml"
ATOMS_ROOT = REPO_ROOT / "atoms"
SLOT_TYPES = ("PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "STORY")


def _find_source_atom_path(source_en: str, atom_type: str) -> Path | None:
    """Locate English CANONICAL.txt under atoms containing source_en."""
    if atom_type not in SLOT_TYPES:
        return None
    needle = source_en.strip()
    if not needle:
        return None
    for path in ATOMS_ROOT.rglob(f"{atom_type}/CANONICAL.txt"):
        if "locales" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if needle in text:
            return path
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Golden translation substring checks")
    ap.add_argument(
        "--locales",
        nargs="+",
        default=["zh-CN", "zh-TW", "ja-JP"],
        help="Locales to verify (default: zh-CN zh-TW ja-JP)",
    )
    args = ap.parse_args()

    if not GOLDEN_PATH.is_file():
        print(f"Missing golden file: {GOLDEN_PATH}", file=sys.stderr)
        return 2

    data = yaml.safe_load(GOLDEN_PATH.read_text(encoding="utf-8")) or {}
    segments = data.get("segments") or []
    failures: list[str] = []

    for seg in segments:
        sid = seg.get("id", "?")
        source_en = (seg.get("source_en") or "").strip()
        atom_type = (seg.get("atom_type") or "").strip()
        expected = seg.get("expected") or {}
        src_path = _find_source_atom_path(source_en, atom_type)
        if src_path is None:
            failures.append(f"{sid}: could not locate English source for atom_type={atom_type}")
            continue
        rel = src_path.relative_to(ATOMS_ROOT)
        persona, topic = rel.parts[0], rel.parts[1]

        for loc in args.locales:
            want = (expected.get(loc) or "").strip()
            if not want:
                continue
            tpath = (
                ATOMS_ROOT
                / persona
                / topic
                / atom_type
                / "locales"
                / loc
                / "CANONICAL.txt"
            )
            if not tpath.is_file():
                failures.append(f"{sid} [{loc}]: missing {tpath.relative_to(REPO_ROOT)}")
                continue
            body = tpath.read_text(encoding="utf-8")
            if want not in body:
                failures.append(
                    f"{sid} [{loc}]: golden substring not found in {tpath.relative_to(REPO_ROOT)}"
                )

    if failures:
        print(f"Golden translation check FAILED ({len(failures)} issue(s)):", file=sys.stderr)
        for line in failures[:50]:
            print(f"  {line}", file=sys.stderr)
        if len(failures) > 50:
            print(f"  ... and {len(failures) - 50} more", file=sys.stderr)
        return 1

    print(
        f"Golden translation check OK ({len(segments)} segments × "
        f"{len(args.locales)} locale(s))."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
