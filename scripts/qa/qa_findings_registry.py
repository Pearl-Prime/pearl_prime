#!/usr/bin/env python3
"""
QA Findings Registry
=====================
Persistent append-only log of gate results across catalog build runs.
Detects regressions: a previously-PASS gate that now fails on the same content.

Storage: artifacts/qa/findings_registry.jsonl  (one JSON object per line)
Entry schema:
    timestamp       ISO-8601 UTC
    run_id          str (caller-supplied or auto-generated UUID4 prefix)
    content_id      str (catalog_id, article slug, atom path, etc.)
    gate_name       str
    status          "PASS" | "FAIL" | "WARN"
    score           float | null
    issues          list[str]
    previously_passed  bool
    is_regression   bool  — True when previous entry for same content+gate was PASS and now FAIL

CLI:
    python3 scripts/qa/qa_findings_registry.py --report
    python3 scripts/qa/qa_findings_registry.py --check-regressions   (exits 1 if found)
    python3 scripts/qa/qa_findings_registry.py --check-regressions --since-hours 48

Importable:
    from scripts.qa.qa_findings_registry import log_gate_result, get_regressions
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[2]
_REGISTRY_PATH = _REPO_ROOT / "artifacts" / "qa" / "findings_registry.jsonl"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _registry_path() -> Path:
    return _REGISTRY_PATH


def _ensure_dir() -> None:
    _registry_path().parent.mkdir(parents=True, exist_ok=True)


def _read_all() -> list[dict]:
    p = _registry_path()
    if not p.exists():
        return []
    entries = []
    with open(p, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def _last_status(content_id: str, gate_name: str, before_ts: str) -> Optional[str]:
    """Return the most recent status for content_id+gate_name before before_ts."""
    best: Optional[dict] = None
    for entry in _read_all():
        if entry.get("content_id") == content_id and entry.get("gate_name") == gate_name:
            if entry.get("timestamp", "") < before_ts:
                if best is None or entry["timestamp"] > best["timestamp"]:
                    best = entry
    return best["status"] if best else None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_gate_result(
    content_id: str,
    gate_name: str,
    status: str,
    score: Optional[float],
    issues: list,
    run_id: Optional[str] = None,
) -> dict:
    """Append a gate result to the registry. Returns the written entry."""
    _ensure_dir()
    ts = _now_iso()
    if run_id is None:
        run_id = uuid.uuid4().hex[:8]

    status = status.upper()
    prev = _last_status(content_id, gate_name, ts)
    previously_passed = prev == "PASS"
    is_regression = previously_passed and status == "FAIL"

    entry = {
        "timestamp": ts,
        "run_id": run_id,
        "content_id": content_id,
        "gate_name": gate_name,
        "status": status,
        "score": score,
        "issues": list(issues),
        "previously_passed": previously_passed,
        "is_regression": is_regression,
    }

    p = _registry_path()
    with open(p, "a", encoding="utf-8") as fh:
        # Advisory file lock for concurrent-write safety
        try:
            fcntl.flock(fh, fcntl.LOCK_EX)
        except (AttributeError, OSError):
            pass  # Windows / unavailable — best-effort
        fh.write(json.dumps(entry) + "\n")
        try:
            fcntl.flock(fh, fcntl.LOCK_UN)
        except (AttributeError, OSError):
            pass

    return entry


def get_regressions(since_hours: int = 24) -> list[dict]:
    """Return all regression entries from the last N hours."""
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)
    cutoff_ts = cutoff.isoformat()
    return [
        e for e in _read_all()
        if e.get("is_regression") and e.get("timestamp", "") >= cutoff_ts
    ]


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def _print_report() -> None:
    entries = _read_all()
    if not entries:
        print("No entries in findings registry.")
        return

    total = len(entries)
    passed = sum(1 for e in entries if e.get("status") == "PASS")
    failed = sum(1 for e in entries if e.get("status") == "FAIL")
    warned = sum(1 for e in entries if e.get("status") == "WARN")
    regressions = sum(1 for e in entries if e.get("is_regression"))

    print("QA Findings Registry — Summary")
    print("=" * 40)
    print(f"  Total entries   : {total}")
    print(f"  PASS            : {passed}")
    print(f"  FAIL            : {failed}")
    print(f"  WARN            : {warned}")
    print(f"  Regressions     : {regressions}")
    print()

    # Per-gate breakdown
    gate_stats: dict[str, dict] = {}
    for e in entries:
        g = e.get("gate_name", "unknown")
        s = e.get("status", "")
        if g not in gate_stats:
            gate_stats[g] = {"PASS": 0, "FAIL": 0, "WARN": 0, "regressions": 0}
        gate_stats[g][s] = gate_stats[g].get(s, 0) + 1
        if e.get("is_regression"):
            gate_stats[g]["regressions"] += 1

    print("Per-gate breakdown:")
    for g, st in sorted(gate_stats.items()):
        total_g = st.get("PASS", 0) + st.get("FAIL", 0) + st.get("WARN", 0)
        pass_rate = st.get("PASS", 0) / total_g * 100 if total_g else 0
        print(f"  {g:<35} PASS={st.get('PASS',0):>4}  FAIL={st.get('FAIL',0):>4}  "
              f"WARN={st.get('WARN',0):>4}  pass%={pass_rate:>5.1f}  reg={st.get('regressions',0)}")

    if regressions:
        print()
        print("Recent regressions:")
        reg_entries = [e for e in entries if e.get("is_regression")][-10:]
        for e in reg_entries:
            print(f"  [{e['timestamp'][:19]}] {e['content_id']} / {e['gate_name']} → {e['status']}")


def _check_regressions_cmd(since_hours: int) -> int:
    """Return exit code: 1 if regressions found, 0 otherwise."""
    regs = get_regressions(since_hours=since_hours)
    if not regs:
        print(f"No regressions in the last {since_hours}h.")
        return 0
    print(f"⚠️  REGRESSION DETECTED — {len(regs)} regression(s) in the last {since_hours}h:")
    for e in regs:
        issues_str = "; ".join(e.get("issues", []))[:80]
        print(f"  [{e['timestamp'][:19]}] {e['content_id']} / {e['gate_name']}"
              f"  score={e.get('score')}  issues: {issues_str}")
    return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="QA Findings Registry — report and regression check")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="Print full registry summary")
    group.add_argument("--check-regressions", action="store_true",
                       help="Exit 1 if regressions found (last 24h by default)")
    parser.add_argument("--since-hours", type=int, default=24,
                        help="Window for --check-regressions (default: 24)")
    args = parser.parse_args()

    if args.report:
        _print_report()
    elif args.check_regressions:
        sys.exit(_check_regressions_cmd(args.since_hours))


if __name__ == "__main__":
    main()
