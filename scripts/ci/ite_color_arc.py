#!/usr/bin/env python3
"""ITE CI: Color arc validation (T-08, T-09, T-14). WARN only.
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §6, §15.2
Input: --chapter-dir containing panel_prompts.json + style_bible.json"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def check_color_arc(chapter_dir: Path) -> list[str]:
    warns: list[str] = []
    panels_data = load_json(chapter_dir / "panel_prompts.json")
    panels = panels_data.get("panels", panels_data) if isinstance(panels_data, dict) else panels_data
    if not panels:
        return warns

    total = len(panels) if isinstance(panels, list) else 0
    if total == 0:
        return warns

    resolution_temps = []
    resolution_sats = []
    phase_sats = []  # (chapter_pct, saturation) for monotonicity check

    for i, panel in enumerate(panels):
        pct = panel.get("chapter_pct", (i / total * 100))
        color = panel.get("color_temperature", {})
        temp_k = color.get("temp_k", 5000)
        sat_pct = color.get("saturation_pct", 50)

        # Collect resolution panels (65-85% of chapter)
        if 65 <= pct <= 85:
            resolution_temps.append(temp_k)
            resolution_sats.append(sat_pct)

        # Collect for monotonicity (tension through resolution: 10-85%)
        if 10 <= pct <= 85:
            phase_sats.append((pct, sat_pct))

    # T-08: resolution color temp >= 5500K
    if resolution_temps:
        mean_temp = sum(resolution_temps) / len(resolution_temps)
        if mean_temp < 5500:
            warns.append(
                f"T-08 WARN: mean resolution color temp {mean_temp:.0f}K < 5500K"
            )

    # T-09: resolution saturation <= 55%
    if resolution_sats:
        mean_sat = sum(resolution_sats) / len(resolution_sats)
        if mean_sat > 55:
            warns.append(
                f"T-09 WARN: mean resolution saturation {mean_sat:.1f}% > 55%"
            )

    # T-14: Phase 2-4 saturation monotonically decreasing (±5% tolerance)
    if len(phase_sats) >= 3:
        phase_sats.sort(key=lambda x: x[0])
        # Check that later panels have lower or equal saturation (with tolerance)
        for j in range(1, len(phase_sats)):
            if phase_sats[j][1] > phase_sats[j - 1][1] + 5:
                warns.append(
                    f"T-14 WARN: non-monotonic saturation at {phase_sats[j][0]:.0f}%: "
                    f"{phase_sats[j][1]:.1f}% > {phase_sats[j-1][1]:.1f}% + 5% tolerance"
                )
                break  # Report first violation only

    return warns


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE color arc check")
    ap.add_argument("--chapter-dir", required=True, help="Chapter output directory")
    args = ap.parse_args()
    warns = check_color_arc(Path(args.chapter_dir))
    result = {"gate": "ite_color_arc", "warns": warns, "pass": True}
    for w in warns:
        print(w)
    print(json.dumps(result, indent=2))
    return 0  # WARN only, never blocks


if __name__ == "__main__":
    sys.exit(main())
