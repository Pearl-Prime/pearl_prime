#!/usr/bin/env python3
"""Check manga release/ops readiness without contacting live services."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

REQUIRED_PATHS = (
    "docs/MANGA_RELEASE_RUNBOOK.md",
    "artifacts/analysis/MANGA_100PCT_MASTER_LEDGER_2026-07-14.md",
)
REQUIRED_ENV_DECLARATIONS = (
    "MANGA_QUEUE_BACKEND",
    "MANGA_ARTIFACT_ROOT",
    "MANGA_STORAGE_ROOT",
)


def check(repo_root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for rel in REQUIRED_PATHS:
        path = repo_root / rel
        checks.append({
            "check": f"path:{rel}",
            "passed": path.is_file(),
            "detail": str(path),
        })
    for name in REQUIRED_ENV_DECLARATIONS:
        checks.append({
            "check": f"env:{name}",
            "passed": bool(os.environ.get(name)),
            "detail": "declared" if os.environ.get(name) else "missing",
        })

    proof_packet = repo_root / "artifacts" / "qa" / "manga_100pct_proof_packet_2026-07-14"
    blind_read = repo_root / "artifacts" / "qa" / "manga_blind_read_bar_2026-07-14"
    checks.extend([
        {
            "check": "proof_packet_present",
            "passed": (proof_packet / "manifest.json").is_file(),
            "detail": str(proof_packet),
        },
        {
            "check": "operator_approval_present",
            "passed": (blind_read / "operator_approval.json").is_file(),
            "detail": str(blind_read / "operator_approval.json"),
        },
    ])
    passed = all(row["passed"] for row in checks)
    return {
        "manga-release-readiness": "green" if passed else "partial",
        "manga-ops-runbook": "present" if (repo_root / REQUIRED_PATHS[0]).is_file() else "missing",
        "manga-queue-repeatability": "blocked",
        "overall-manga-green": "NOT_PROVEN",
        "checks": checks,
        "blocker": (
            "" if passed
            else "live queue/GPU/storage repeatability and/or approval evidence is incomplete"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    report = check(args.repo_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["manga-release-readiness"] == "green" else 2


if __name__ == "__main__":
    raise SystemExit(main())
