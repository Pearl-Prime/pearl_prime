#!/usr/bin/env python3
"""ITE CI: Breath sequence validation (T-07, T-10). WARN only.
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §5, §15.2
Input: --chapter-dir containing panel_prompts.json"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def check_breath(chapter_dir: Path) -> list[str]:
    warns: list[str] = []
    pp = chapter_dir / "panel_prompts.json"
    if not pp.exists():
        return warns
    data = json.loads(pp.read_text(encoding="utf-8"))
    breath_map = data.get("breath_map", data.get("breath_sequences", []))
    if isinstance(breath_map, dict):
        breath_map = breath_map.get("breath_sequences", [])

    # T-07: >= 1 breath sequence per chapter
    if len(breath_map) == 0:
        warns.append("T-07 WARN: chapter has 0 breath sequences (minimum 1)")
        return warns

    # T-10: hold panels must have fractal BG (FD 1.3-1.5)
    panels_data = data.get("panels", [])
    panel_map = {}
    if isinstance(panels_data, list):
        for p in panels_data:
            pid = p.get("panel_id")
            if pid:
                panel_map[pid] = p

    for seq_idx, seq in enumerate(breath_map):
        phases = seq.get("phase_panels", {})
        hold_panels = phases.get("hold", [])
        for hold_id in hold_panels:
            panel = panel_map.get(hold_id, {})
            ft = panel.get("fractal_target", {})
            fd_range = ft.get("fd_range", [0, 0])
            if not (1.3 <= fd_range[0] and fd_range[1] <= 1.5):
                if fd_range == [0, 0]:
                    warns.append(
                        f"T-10 WARN: hold panel {hold_id} in breath seq {seq_idx} "
                        f"has no fractal_target"
                    )
                else:
                    warns.append(
                        f"T-10 WARN: hold panel {hold_id} in breath seq {seq_idx} "
                        f"fractal FD range {fd_range} outside [1.3, 1.5]"
                    )

    return warns


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE breath sequence check")
    ap.add_argument("--chapter-dir", required=True, help="Chapter output directory")
    args = ap.parse_args()
    warns = check_breath(Path(args.chapter_dir))
    result = {"gate": "ite_breath_check", "warns": warns, "pass": True}
    for w in warns:
        print(w)
    print(json.dumps(result, indent=2))
    return 0  # WARN only


if __name__ == "__main__":
    sys.exit(main())
