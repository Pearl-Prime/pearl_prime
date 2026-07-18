#!/usr/bin/env python3
"""Placeholder character-sheet tree for GPU workflow (FLUX wiring TODO)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series-id", required=True)
    ap.add_argument("--character-ids", required=True, help="Comma-separated ids")
    args = ap.parse_args()
    base = REPO_ROOT / "config" / "source_of_truth" / "manga_character_sheets" / args.series_id
    meta = {
        "series_id": args.series_id,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "characters": [c.strip() for c in args.character_ids.split(",") if c.strip()],
        "note": "Stub: add FLUX + IP-Adapter renders on pearl-star-gpu.",
    }
    for cid in meta["characters"]:
        d = base / cid
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(f"# {cid}\n\nTurnarounds + expressions pending GPU job.\n", encoding="utf-8")
    base.mkdir(parents=True, exist_ok=True)
    (base / "sheet_manifest.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
