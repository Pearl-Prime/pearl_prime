#!/usr/bin/env python3
"""Status report for Pearl News per-brand mapping leftover (I038)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts/qa/archived_session_audit_gt30d_20260722/pearl_news_per_brand_map_status.json"

CANDIDATES = [
    "docs/PEARL_NEWS_WRITER_SPEC.md",
    "docs/PEARL_NEWS_SIDEBAR_VERSION_HISTORY.md",
    "scripts/pearl_news",
    "artifacts/pearl_news/snapshots/CANONICAL_SIDEBAR.html",
]


def main() -> int:
    rows = []
    for rel in CANDIDATES:
        p = REPO / rel
        rows.append({"path": rel, "exists": p.exists()})
    present = [r["path"] for r in rows if r["exists"]]
    missing = [r["path"] for r in rows if not r["exists"]]
    # Heuristic: writer spec + sidebar canonical = PARTIAL; full per-brand map may still be open
    status = "PARTIAL_SURFACES_PRESENT" if len(present) >= 3 else "BLOCKED"
    report = {
        "keeper": "I038",
        "status": status,
        "present": present,
        "missing": missing,
        "next": "Map weekly_package / brand_admin deliverables per brand; do not touch sidebar without parity gate",
        "acceptance_layer": "CODE-WIRED status only",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
