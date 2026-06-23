#!/usr/bin/env python3
"""Re-run Waystream batch books that failed (register_gate / pipeline_fail)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.release.batch_waystream_epubs import PILOT_N, _iso_week, load_books, run_one  # noqa: E402

STATE = REPO / "artifacts/waystream/batch_epub_state.json"


def _fail_ids() -> set[str]:
    if STATE.is_file():
        data = json.loads(STATE.read_text(encoding="utf-8"))
        ids = {
            r["book_id"]
            for r in data.get("results", [])
            if r.get("status") not in ("ok", "skip_exists", "dry_run")
        }
        if ids:
            return ids
    return {
        "way_stream_sanctuary__default_teacher__corporate_managers__anxiety__false_alarm__1hr",
        "way_stream_sanctuary__default_teacher__corporate_managers__anxiety__spiral",
    }


def main() -> int:
    fail_ids = _fail_ids()
    week = _iso_week()
    if STATE.is_file():
        week = json.loads(STATE.read_text(encoding="utf-8")).get("week") or week

    books = load_books(limit=PILOT_N)
    results = []
    for _, plan in books:
        if plan["book_id"] not in fail_ids:
            continue
        print(f"retry {plan['book_id']}...", flush=True)
        results.append(run_one(plan, week, dry_run=False, force=True))

    if not results:
        print("no failures to retry")
        return 0

    ok = sum(1 for r in results if r["status"] in ("ok", "skip_exists"))
    fail = [r for r in results if r["status"] not in ("ok", "skip_exists")]
    print(f"retry: n={len(results)} ok={ok} fail={len(fail)}")
    for r in fail:
        print(f"  FAIL {r['book_id']}: {r.get('error') or r['status']}")

    if STATE.is_file():
        data = json.loads(STATE.read_text(encoding="utf-8"))
        by_id = {r["book_id"]: r for r in data.get("results", [])}
        for r in results:
            by_id[r["book_id"]] = r
        data["results"] = list(by_id.values())
        data["week"] = week
        STATE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
