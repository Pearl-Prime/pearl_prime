#!/usr/bin/env python3
"""CLI for manga story excellence realization gate.

Exit codes: 0=PASS, 1=WARN/malformed, 2=BLOCKED
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from phoenix_v4.manga.story_quality.excellence_gate import evaluate_story_excellence  # noqa: E402


def _load(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        import yaml

        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate manga story excellence realization")
    ap.add_argument("--story-handoff", type=Path, required=True)
    ap.add_argument("--chapter-script", type=Path, required=True)
    ap.add_argument("--internal-record", type=Path, default=None)
    ap.add_argument("--production", action="store_true")
    ap.add_argument("--allow-warn", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--repair-packet", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--repo-root", type=Path, default=REPO)
    args = ap.parse_args(argv)

    try:
        story = _load(args.story_handoff)
        writer = _load(args.chapter_script)
        internal = _load(args.internal_record) if args.internal_record else None
    except Exception as exc:
        print(f"MALFORMED_INPUT: {exc}", file=sys.stderr)
        return 1

    report = evaluate_story_excellence(
        story_handoff=story,
        writer_handoff=writer,
        internal_record=internal,
        production=bool(args.production),
        repo_root=args.repo_root,
    )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.repair_packet:
        print(json.dumps(report.get("repair_packet"), indent=2))
    elif args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"STORY_EXCELLENCE: {report['status']} score={report['score']}/{report['threshold']} "
            f"genre={report['relevance_genre']} market={report['target_market']}",
            file=sys.stderr,
        )
        if report["status"] == "BLOCKED":
            failed = [g["gate_id"] for g in report["gates"] if g.get("status") == "BLOCKED"]
            print("FAILED: " + ", ".join(failed), file=sys.stderr)

    status = report["status"]
    if status == "PASS":
        return 0
    if status == "WARN":
        return 0 if args.allow_warn else 1
    if status == "BLOCKED":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
