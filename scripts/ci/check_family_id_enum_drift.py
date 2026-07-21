#!/usr/bin/env python3
"""CI gate: spine family_id values must be in canonical topic enum.

Uses line-scan (not full YAML load) to avoid hanging on large spine files.
gt30d keeper I006.

Usage:
  PYTHONPATH=. python3 scripts/ci/check_family_id_enum_drift.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO = Path(__file__).resolve().parents[2]
CANONICAL = REPO / "config/source_of_truth/canonical_topics.yaml"
SPINES = REPO / "config/spines"
FAMILY_RE = re.compile(r"^family_id:\s*[\"']?([A-Za-z0-9_]+)[\"']?\s*$")


def _canonical_ids() -> set[str]:
    if yaml is None or not CANONICAL.exists():
        return set()
    data = yaml.safe_load(CANONICAL.read_text(encoding="utf-8")) or {}
    raw = data.get("topic_ids") or []
    if isinstance(raw, list):
        return {str(x) for x in raw if x}
    return set()


def _spine_family_ids() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if not SPINES.is_dir():
        return found
    for path in sorted(SPINES.glob("*.yaml")):
        # Only scan the first 40 lines — family_id is a header field
        try:
            with path.open(encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f):
                    if i > 40:
                        break
                    m = FAMILY_RE.match(line.strip())
                    if m:
                        found.append((str(path.relative_to(REPO)), m.group(1)))
                        break
        except OSError:
            continue
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-mode", choices=("fail", "warn"), default="fail")
    args = ap.parse_args()
    canon = _canonical_ids()
    if not canon:
        print("WARN: could not load canonical topic ids; skipping", file=sys.stderr)
        return 0
    spines = _spine_family_ids()
    drifts = [
        f"{rel}: family_id={fid!r} not in canonical_topics"
        for rel, fid in spines
        if fid not in canon
    ]
    if not drifts:
        print(f"OK: {len(spines)} spine family_id values match canonical enum ({len(canon)} ids)")
        return 0
    msg = "family_id enum drift:\n" + "\n".join(f"  - {d}" for d in drifts)
    if args.gate_mode == "warn":
        print(f"::warning::{msg}")
        return 0
    print(msg, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
