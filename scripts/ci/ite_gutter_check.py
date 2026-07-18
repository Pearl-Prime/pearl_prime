#!/usr/bin/env python3
"""ITE CI: Gutter therapy validation (T-01, T-02, T-03, T-15).
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §8, §15.1, §15.2
Input: --chapter-dir containing panel_prompts.json
Exit 1 on any BLOCKER fail."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GUTTER_CLASS_MULTIPLIER = {
    "tight": 0.5,
    "standard": 1.0,
    "processing": 2.0,
    "therapeutic": 3.0,
    "breath": 4.0,
}


def load_panels(chapter_dir: Path) -> list[dict]:
    pp = chapter_dir / "panel_prompts.json"
    if not pp.exists():
        return []
    data = json.loads(pp.read_text(encoding="utf-8"))
    return data.get("panels", data) if isinstance(data, dict) else data


def gutter_class_value(cls: str) -> float:
    return GUTTER_CLASS_MULTIPLIER.get(cls, 1.0)


def check_gutter_rules(panels: list[dict]) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warns: list[str] = []
    total = len(panels)
    consecutive_tight = 0

    for i, panel in enumerate(panels):
        band = panel.get("emotional_band", 0)
        gutter_after = panel.get("gutter_after", "standard")
        gv = gutter_class_value(gutter_after)

        # T-01: post-band-4 gutter >= processing (2.0x)
        if band >= 4 and gv < 2.0:
            blockers.append(
                f"T-01 BLOCKER: panel {panel.get('panel_id', i)} band={band} "
                f"gutter_after={gutter_after} (need >= processing)"
            )

        # T-02: post-band-5 gutter >= therapeutic (3.0x)
        if band >= 5 and gv < 3.0:
            blockers.append(
                f"T-02 BLOCKER: panel {panel.get('panel_id', i)} band={band} "
                f"gutter_after={gutter_after} (need >= therapeutic)"
            )

        # T-03: consecutive tight gutters
        if gutter_after == "tight":
            consecutive_tight += 1
            if consecutive_tight > 5:
                blockers.append(
                    f"T-03 BLOCKER: >5 consecutive tight gutters ending at panel "
                    f"{panel.get('panel_id', i)}"
                )
        else:
            consecutive_tight = 0

        # T-15: no tight in resolution (final 25%)
        chapter_pct = panel.get("chapter_pct", (i / total * 100) if total else 0)
        if chapter_pct >= 75 and gutter_after == "tight":
            warns.append(
                f"T-15 WARN: tight gutter in resolution section at panel "
                f"{panel.get('panel_id', i)} ({chapter_pct:.0f}%)"
            )

    return blockers, warns


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE gutter therapy check")
    ap.add_argument("--chapter-dir", required=True, help="Chapter output directory")
    args = ap.parse_args()
    chapter_dir = Path(args.chapter_dir)
    panels = load_panels(chapter_dir)
    if not panels:
        print("No panels found; skipping gutter check")
        return 0

    blockers, warns = check_gutter_rules(panels)
    for w in warns:
        print(w)
    for b in blockers:
        print(b, file=sys.stderr)

    result = {
        "gate": "ite_gutter_check",
        "blockers": blockers,
        "warns": warns,
        "pass": len(blockers) == 0,
    }
    print(json.dumps(result, indent=2))

    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
