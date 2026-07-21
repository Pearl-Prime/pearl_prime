#!/usr/bin/env python3
"""Smoke/pilot checker for Manga Structural Composition MVP (gt30d D06 / C01).

Acceptance: CODE-WIRED smoke only — not EXECUTED-REAL / not PROVEN-AT-BAR.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_OBJECTS = ("support_surface", "contact_region", "support_edge", "relation_check")


def check_panel(panel: dict) -> list[str]:
    errors: list[str] = []
    pid = panel.get("panel_id") or panel.get("id") or "?"
    for key in REQUIRED_OBJECTS:
        if key not in panel:
            errors.append(f"panel {pid}: missing {key}")
            continue
        val = panel[key]
        if val in (None, "", [], {}):
            errors.append(f"panel {pid}: empty {key}")
    prov = panel.get("provenance") or panel.get("layer_provenance")
    if prov == "INTERIM":
        # allowed — but must not be silently treated as REAL
        pass
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", help="JSON file with panels[]")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        good = {
            "panels": [
                {
                    "panel_id": "p1",
                    "support_surface": "floor",
                    "contact_region": "feet-floor",
                    "support_edge": "none",
                    "relation_check": "standing_ok",
                    "provenance": "INTERIM",
                }
            ]
        }
        bad = {"panels": [{"panel_id": "p2"}]}
        e1 = [e for p in good["panels"] for e in check_panel(p)]
        e2 = [e for p in bad["panels"] for e in check_panel(p)]
        assert not e1, e1
        assert e2, "expected errors for empty panel"
        print("OK: structural composition MVP self-test passed")
        return 0

    if not args.manifest:
        print("--manifest or --self-test required", file=sys.stderr)
        return 2
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    panels = data.get("panels") or data.get("panel_list") or []
    errors = [e for p in panels for e in check_panel(p)]
    if errors:
        print("FAIL structural composition MVP:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK: {len(panels)} panels pass MVP object presence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
