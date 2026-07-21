#!/usr/bin/env python3
"""Verify teacher/music mode survives emit through story handoff."""
from __future__ import annotations

import argparse
import inspect
import json
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]


def _find_vessel_beats(value: Any) -> list[Any]:
    if isinstance(value, dict):
        for key in ("mode_vessel_beats", "vessel_beats", "beats"):
            rows = value.get(key)
            if isinstance(rows, list) and rows:
                return rows
        for child in value.values():
            found = _find_vessel_beats(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = _find_vessel_beats(child)
            if found:
                return found
    return []


def verify_mode(mode: str, *, genre_id: str = "shonen") -> dict[str, Any]:
    from phoenix_v4.manga.series.emit import build_series_artifact_bundle, emit_series_setup
    from scripts.run_manga_pipeline import run_one_book

    failures: list[str] = []
    if "mode" not in inspect.signature(emit_series_setup).parameters:
        failures.append("emit_series_setup_missing_mode_parameter")
    if "mode" not in inspect.signature(run_one_book).parameters:
        failures.append("run_one_book_missing_mode_parameter")

    bundle = build_series_artifact_bundle(
        series_id=f"mode_contract_{mode}",
        arc_id="arc_mode_contract",
        genre_id=genre_id,
        topic="anxiety",
        mode=mode,
    )
    internal = bundle.get("story_architecture_internal") or {}
    handoff = bundle.get("story_architecture_handoff") or {}
    if internal.get("mode") != mode:
        failures.append("internal_mode_not_preserved")
    if handoff.get("mode") != mode:
        failures.append("handoff_mode_not_preserved")
    if not internal.get("mode_vessel"):
        failures.append("internal_mode_vessel_missing")
    if not handoff.get("mode_vessel"):
        failures.append("handoff_mode_vessel_missing")
    if not _find_vessel_beats(internal):
        failures.append("internal_vessel_beats_missing")
    if not _find_vessel_beats(handoff):
        failures.append("handoff_vessel_beats_missing")

    return {
        "mode": mode,
        "genre_id": genre_id,
        "passed": not failures,
        "failures": failures,
        "internal_mode_vessel": internal.get("mode_vessel"),
        "handoff_mode_vessel": handoff.get("mode_vessel"),
        "emit-mode-plumbing": "green" if not failures else "blocked",
        "overall-manga-green": "NOT_PROVEN",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["teacher", "music", "both"], default="both")
    parser.add_argument("--genre", default="shonen")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    modes = ["teacher", "music"] if args.mode == "both" else [args.mode]
    reports = [verify_mode(mode, genre_id=args.genre) for mode in modes]
    payload = {
        "passed": all(row["passed"] for row in reports),
        "reports": reports,
        "manga-teacher-mode": (
            "green" if any(r["mode"] == "teacher" and r["passed"] for r in reports) else "blocked"
        ),
        "manga-music-mode": (
            "green" if any(r["mode"] == "music" and r["passed"] for r in reports) else "blocked"
        ),
        "overall-manga-green": "NOT_PROVEN",
    }
    text = json.dumps(payload, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
