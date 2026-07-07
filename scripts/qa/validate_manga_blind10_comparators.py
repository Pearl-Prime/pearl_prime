#!/usr/bin/env python3
"""Validate M6 blind-10 comparator PDFs on disk against COMPARATOR_REGISTRY.yaml.

Read-only gate for operator acquisition closeout. Checks:
  - Expected operator_asset paths exist under comparators/
  - File size ≥ min_bytes (default 500_000)
  - sha256 matches registry when asset_status is ACQUIRED

Exit codes:
  0 — all required entries satisfied
  1 — missing files, size failures, or sha256 mismatch
  2 — input / config error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
DEFAULT_RUN_ROOT = REPO / "artifacts" / "qa" / "manga_blind10_2026-07-08"
MIN_BYTES_DEFAULT = 500_000


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_registry(run_root: Path) -> dict[str, Any]:
    path = run_root / "COMPARATOR_REGISTRY.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"Missing registry: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def validate(
    run_root: Path,
    *,
    min_bytes: int,
    require_p0: bool,
    slot_filter: set[str] | None,
) -> dict[str, Any]:
    registry = _load_registry(run_root)
    slots: dict[str, Any] = registry.get("slots") or {}
    findings: list[dict[str, Any]] = []
    acquired = 0
    pending = 0
    p0_ready = True

    for slot_id, slot in sorted(slots.items(), key=lambda x: x[0]):
        if slot_filter and slot_id not in slot_filter:
            continue
        for comp in slot.get("comparators") or []:
            comp_id = comp.get("id", "?")
            status = comp.get("asset_status", "PENDING_OPERATOR_SCAN")
            priority = comp.get("priority", "P2")
            rel = comp.get("operator_asset", "")
            path = run_root / rel if rel else None
            entry: dict[str, Any] = {
                "slot": slot_id,
                "id": comp_id,
                "title": comp.get("title"),
                "asset_status": status,
                "priority": priority,
                "operator_asset": rel,
            }

            if status in ("PENDING_OPERATOR_SCAN", "READY_TO_ACQUIRE"):
                pending += 1
                if path and path.is_file():
                    entry["note"] = "file present but registry not ACQUIRED"
                    sz = path.stat().st_size
                    entry["bytes"] = sz
                    if sz < min_bytes:
                        findings.append({**entry, "level": "ERROR", "reason": "undersized"})
                        if priority == "P0":
                            p0_ready = False
                    else:
                        entry["sha256_disk"] = _sha256(path)
                else:
                    entry["on_disk"] = False
                    if require_p0 and priority == "P0":
                        findings.append({**entry, "level": "ERROR", "reason": "missing_p0"})
                        p0_ready = False
                continue

            if status != "ACQUIRED":
                pending += 1
                continue

            if not path or not path.is_file():
                findings.append({**entry, "level": "ERROR", "reason": "missing_acquired"})
                if priority == "P0":
                    p0_ready = False
                continue

            sz = path.stat().st_size
            entry["bytes"] = sz
            if sz < min_bytes:
                findings.append({**entry, "level": "ERROR", "reason": "undersized"})
                if priority == "P0":
                    p0_ready = False
                continue

            disk_hash = _sha256(path)
            entry["sha256_disk"] = disk_hash
            expected = comp.get("sha256")
            if expected and disk_hash != expected:
                findings.append(
                    {**entry, "level": "ERROR", "reason": "sha256_mismatch", "sha256_expected": expected}
                )
                if priority == "P0":
                    p0_ready = False
                continue

            acquired += 1
            entry["level"] = "OK"

    errors = [f for f in findings if f.get("level") == "ERROR"]
    report = {
        "run_id": registry.get("run_id"),
        "run_root": str(run_root),
        "acquired": acquired,
        "pending": pending,
        "pilot_ready": p0_ready and acquired >= 2,
        "errors": len(errors),
        "findings": findings,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate M6 blind-10 comparator PDFs")
    parser.add_argument(
        "--run-root",
        type=Path,
        default=DEFAULT_RUN_ROOT,
        help="Blind-10 run directory (default: manga_blind10_2026-07-08)",
    )
    parser.add_argument("--run-id", type=str, default="", help="Set --run-root to artifacts/qa/<run-id>/")
    parser.add_argument("--min-bytes", type=int, default=MIN_BYTES_DEFAULT)
    parser.add_argument("--require-p0", action="store_true", help="Fail if P0 comparators missing")
    parser.add_argument("--slot", action="append", dest="slots", help="Limit to slot id(s), e.g. 01")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    run_root = args.run_root
    if args.run_id:
        run_root = REPO / "artifacts" / "qa" / args.run_id

    slot_filter = set(args.slots) if args.slots else None

    try:
        report = validate(
            run_root,
            min_bytes=args.min_bytes,
            require_p0=args.require_p0,
            slot_filter=slot_filter,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"run_id: {report['run_id']}")
        print(f"acquired: {report['acquired']}  pending: {report['pending']}")
        print(f"pilot_ready: {report['pilot_ready']}  errors: {report['errors']}")
        for f in report["findings"]:
            if f.get("level") == "ERROR":
                print(f"  ERROR {f.get('id')} ({f.get('title')}): {f.get('reason')}")

    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
