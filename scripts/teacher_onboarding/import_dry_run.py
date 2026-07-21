#!/usr/bin/env python3
"""Dry-run import step: intake JSON → teacher-bank candidate scaffold.

Never creates production atoms. Always emits production_atoms_created: false.
See docs/specs/TEACHER_PORTAL_V2_SPEC.md § Import-step contract.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _safe_slug(value: str) -> str:
    out = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in (value or "").lower())
    out = out.strip("_")[:120]
    return out or "teacher"


def _counts(submission: dict[str, Any]) -> dict[str, int]:
    materials = submission.get("materials") or {}
    teachings = materials.get("teachings") or {}
    doctrine = str(teachings.get("doctrine_text") or "").strip()
    readiness = submission.get("server_readiness") or submission.get("readiness") or {}
    server_counts = readiness.get("server_counts") or readiness.get("counts") or {}
    if server_counts:
        return {str(k): int(v or 0) for k, v in server_counts.items()}
    return {
        "teachings": 1 if doctrine else 0,
        "stories": len(materials.get("stories") or []),
        "practices": len(materials.get("practices") or []),
        "quotes": len(materials.get("quotes") or []),
        "reflections": 1 if str(materials.get("reflections_integrations_text") or "").strip() else 0,
        "raw_sources": len(materials.get("files") or []) + len(materials.get("links") or []),
    }


def build_scaffold(submission: dict[str, Any], source: str) -> dict[str, Any]:
    teacher_id = _safe_slug(
        str(submission.get("teacher_id") or (submission.get("identity") or {}).get("teacher_id") or "teacher")
    )
    teacher_name = str(
        submission.get("teacher_name")
        or (submission.get("identity") or {}).get("public_teacher_name")
        or teacher_id
    ).strip()
    counts = _counts(submission)
    base = f"SOURCE_OF_TRUTH/teacher_banks/candidates/{teacher_id}"
    return {
        "schema_version": "teacher_bank_import_scaffold_v1",
        "source_submission_key": source,
        "teacher_id": teacher_id,
        "teacher_name": teacher_name,
        "lifecycle_status": "imported",
        "production_atoms_created": False,
        "operator_review_required": True,
        "candidate_paths": {
            "doctrine": f"{base}/doctrine/",
            "stories": f"{base}/stories/",
            "practices": f"{base}/practices/",
            "quotes": f"{base}/quotes/",
            "reflections": f"{base}/reflections/",
            "manifest": f"{base}/IMPORT_MANIFEST.json",
        },
        "counts_from_submission": counts,
        "notes": [
            "dry-run only; no files written to SOURCE_OF_TRUTH unless --write-scaffold",
            "production_atoms_created remains false until operator approval + production gates",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Teacher onboarding import dry-run (no production atoms)")
    parser.add_argument("--submission", required=True, help="Path to intake/submission JSON")
    parser.add_argument(
        "--write-scaffold",
        default="",
        help="Optional scratch directory to write scaffold JSON (never SOURCE_OF_TRUTH)",
    )
    args = parser.parse_args(argv)

    path = Path(args.submission)
    if not path.is_file():
        print(f"error: submission not found: {path}", file=sys.stderr)
        return 2

    submission = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(submission, dict):
        print("error: submission must be a JSON object", file=sys.stderr)
        return 2

    scaffold = build_scaffold(submission, source=str(path))
    if scaffold.get("production_atoms_created") is not False:
        print("error: invariant broken — production_atoms_created must be false", file=sys.stderr)
        return 3

    text = json.dumps(scaffold, indent=2, ensure_ascii=False) + "\n"
    sys.stdout.write(text)

    if args.write_scaffold:
        out_dir = Path(args.write_scaffold)
        if "SOURCE_OF_TRUTH" in out_dir.resolve().parts:
            print("error: refusing to write under SOURCE_OF_TRUTH", file=sys.stderr)
            return 4
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{scaffold['teacher_id']}_import_scaffold.json"
        out_path.write_text(text, encoding="utf-8")
        print(f"# wrote {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
