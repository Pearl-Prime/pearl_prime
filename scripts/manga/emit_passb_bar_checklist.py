#!/usr/bin/env python3
"""Emit PassB bar checklist TSV (gt30d D07 / C02). Does not fake EXECUTED-REAL."""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

COMPONENTS = [
    ("reading_graph", ["scripts/manga", "phoenix_v4/manga"]),
    ("spread_layout", ["scripts/manga", "phoenix_v4/manga"]),
    ("jlreq_sfx_lettering", ["phoenix_v4/manga/lettering_from_script.py", "scripts/manga"]),
    ("bar_checklist", []),  # this emitter
]


def _present(paths: list[str]) -> bool:
    for p in paths:
        path = REPO / p
        if path.exists():
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="artifacts/qa/archived_session_audit_gt30d_20260722/manga_passb_bar_checklist.tsv",
    )
    args = ap.parse_args()
    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = [("component", "status", "evidence", "acceptance_layer")]
    for name, paths in COMPONENTS:
        if name == "bar_checklist":
            rows.append((name, "CODE-WIRED", str(out.relative_to(REPO)), "CODE-WIRED"))
            continue
        ok = _present(paths)
        rows.append(
            (
                name,
                "CONFIG-EXISTS" if ok else "ABSENT",
                ";".join(paths) if ok else "(no path hit)",
                "not EXECUTED-REAL",
            )
        )
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"wrote {out}")
    # Honest: packet not complete if any ABSENT
    absent = [r[0] for r in rows[1:] if r[1] == "ABSENT"]
    if absent:
        print(f"BLOCKED: still ABSENT: {absent}")
        return 0  # emitter succeeded; bar packet itself remains incomplete
    print("OK: all components at least CONFIG-EXISTS (still not PROVEN-AT-BAR)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
