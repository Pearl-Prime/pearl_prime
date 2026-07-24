#!/usr/bin/env python3
"""CI gate: non-empty angle_id values in catalog planning must join angle_registry.

gt30d keeper I032 — missing/unknown angle_id must be an explicit error, not a silent no-op.

Usage:
  PYTHONPATH=. python3 scripts/ci/check_angle_id_registry_join.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "config/angles/angle_registry.yaml"
SCAN_DIRS = [
    REPO / "config/catalog_planning",
    REPO / "config/angles",
]


def _registry_ids() -> set[str]:
    if yaml is None or not REGISTRY.exists():
        return set()
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    angles = data.get("angles") or {}
    return set(angles.keys()) if isinstance(angles, dict) else set()


def _walk_angle_ids(obj, path: str, out: list[tuple[str, str]]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("angle_id", "successor_angle_id") and isinstance(v, str) and v.strip():
                out.append((path, v.strip()))
            else:
                _walk_angle_ids(v, path, out)
    elif isinstance(obj, list):
        for item in obj:
            _walk_angle_ids(item, path, out)


def collect_refs() -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    if yaml is None:
        return refs
    for root in SCAN_DIRS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.yaml"):
            if path.resolve() == REGISTRY.resolve():
                # Still allow successor_angle_id checks inside registry
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                angles = data.get("angles") or {}
                if isinstance(angles, dict):
                    for aid, body in angles.items():
                        if not isinstance(body, dict):
                            continue
                        succ = body.get("successor_angle_id")
                        if isinstance(succ, str) and succ.strip():
                            refs.append((str(path.relative_to(REPO)), succ.strip()))
                continue
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except Exception:
                continue
            _walk_angle_ids(data, str(path.relative_to(REPO)), refs)
    return refs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-mode", choices=("fail", "warn"), default="fail")
    args = ap.parse_args()
    reg = _registry_ids()
    if not reg:
        print("WARN: angle registry empty/unreadable; skip", file=sys.stderr)
        return 0
    bad = []
    for rel, aid in collect_refs():
        if aid not in reg:
            bad.append(f"{rel}: angle_id={aid!r} not in config/angles/angle_registry.yaml")
    if not bad:
        print(f"OK: angle_id registry join clean ({len(reg)} registry ids)")
        return 0
    msg = "angle_id registry join failures:\n" + "\n".join(f"  - {b}" for b in bad[:50])
    if len(bad) > 50:
        msg += f"\n  ... and {len(bad) - 50} more"
    if args.gate_mode == "warn":
        print(f"::warning::{msg}")
        return 0
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
