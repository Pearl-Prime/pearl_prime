#!/usr/bin/env python3
"""ITE CI: Soundtrack therapeutic validation (T-05, T-06, T-11, T-12, T-13).
Authority: specs/IMPLICIT_THERAPEUTIC_ENGINE_DEV_SPEC.md §11, §15
Input: --chapter-dir containing soundtrack_config.yaml
Exit 1 on T-05 or T-06 BLOCKER."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_soundtrack(chapter_dir: Path) -> dict:
    for name in ("soundtrack_config.yaml", "soundtrack_config.json"):
        path = chapter_dir / name
        if path.exists():
            if name.endswith(".yaml"):
                try:
                    import yaml
                    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                except Exception:
                    return {}
            else:
                return json.loads(path.read_text(encoding="utf-8"))
    return {}


def check_soundtrack(config: dict) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    warns: list[str] = []

    sections = config.get("sections", [])

    for sec in sections:
        section_type = sec.get("type", "")
        has_lyrics = sec.get("has_lyrics", False)
        tempo_bpm = sec.get("tempo_bpm", 66)
        scale = sec.get("scale", "pentatonic")

        # T-05: no lyrics in resolution
        if section_type == "resolution" and has_lyrics:
            blockers.append(f"T-05 BLOCKER: lyrics in resolution section")

        # T-11: calming tempo <= 78 BPM
        if section_type in ("calming", "release", "resolve", "resolution"):
            if tempo_bpm > 78:
                warns.append(f"T-11 WARN: calming section tempo {tempo_bpm} BPM > 78")

    # T-06: video ending arousal
    video_end = config.get("video_end", {})
    if video_end:
        final_cut_sec = video_end.get("final_cut_interval_sec", 10)
        if final_cut_sec < 4:
            blockers.append(
                f"T-06 BLOCKER: video ends on cut rhythm {final_cut_sec}s < 4s (high arousal)"
            )

    # T-12: strategic silence >= 8 sec per 5 min
    total_duration_sec = config.get("total_duration_sec", 300)
    total_silence_sec = config.get("total_silence_sec", 0)
    if total_duration_sec > 0:
        per_5min = total_silence_sec / (total_duration_sec / 300)
        if per_5min < 8:
            warns.append(
                f"T-12 WARN: {total_silence_sec:.0f}s silence in "
                f"{total_duration_sec:.0f}s ({per_5min:.1f}s per 5min < 8s)"
            )

    # T-13: pentatonic ratio
    calming_sections = [s for s in sections if s.get("type") in ("calming", "release", "resolve", "resolution")]
    if calming_sections:
        non_pent = sum(1 for s in calming_sections if s.get("scale", "pentatonic") != "pentatonic")
        ratio = non_pent / len(calming_sections)
        if ratio > 0.5:
            warns.append(
                f"T-13 WARN: {ratio:.0%} of calming sections use non-pentatonic scale (>50%)"
            )

    return blockers, warns


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE soundtrack check")
    ap.add_argument("--chapter-dir", required=True, help="Chapter output directory")
    args = ap.parse_args()
    config = load_soundtrack(Path(args.chapter_dir))
    if not config:
        print("No soundtrack_config found; skipping")
        return 0

    blockers, warns = check_soundtrack(config)
    for w in warns:
        print(w)
    for b in blockers:
        print(b, file=sys.stderr)
    result = {
        "gate": "ite_soundtrack",
        "blockers": blockers,
        "warns": warns,
        "pass": len(blockers) == 0,
    }
    print(json.dumps(result, indent=2))
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
