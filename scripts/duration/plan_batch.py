#!/usr/bin/env python3
"""
CDIS batch planner: brand × platform × locale × format matrix.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration._config import (  # noqa: E402
    config_snapshot_hash,
    load_duration_configs,
    load_yaml,
    should_skip_output,
    write_atomically,
)
from scripts.duration.plan_duration import plan  # noqa: E402


def _all_brands() -> list[str]:
    reg = load_yaml(REPO_ROOT / "config" / "video" / "channel_registry.yaml")
    seen = set()
    for ch in (reg.get("channels") or {}).values():
        if isinstance(ch, dict) and ch.get("brand_id"):
            seen.add(str(ch["brand_id"]))
    return sorted(seen) or ["stillness_press"]


def _all_platforms(cfgs: dict) -> list[str]:
    plat = (cfgs.get("platform_duration_profiles") or {}).get("platforms") or {}
    return sorted(plat.keys())


def _all_formats(cfgs: dict) -> list[str]:
    reg = cfgs.get("duration_registry") or {}
    return sorted((reg.get("formats") or {}).keys())


def main() -> int:
    ap = argparse.ArgumentParser(description="CDIS batch duration planner")
    ap.add_argument("--brands", default="all", help="Comma-separated brand_id or 'all'")
    ap.add_argument("--platforms", default="all", help="Comma-separated or 'all'")
    ap.add_argument("--locales", default="en-US", help="Comma-separated locales")
    ap.add_argument("--intent", default="therapeutic")
    ap.add_argument("--persona", default="millennial_women_professionals")
    ap.add_argument("--modality", default=None)
    ap.add_argument("--micro-dose-protocol", action="store_true")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--force", action="store_true", help="Overwrite output")
    args = ap.parse_args()

    cfgs = load_duration_configs()
    brands = _all_brands() if args.brands.strip() == "all" else [b.strip() for b in args.brands.split(",") if b.strip()]
    plats = _all_platforms(cfgs) if args.platforms.strip() == "all" else [p.strip() for p in args.platforms.split(",") if p.strip()]
    locs = [x.strip() for x in args.locales.split(",") if x.strip()]
    formats = _all_formats(cfgs)

    items = []
    errors = []
    for b in brands:
        for plat in plats:
            for loc in locs:
                for fmt in formats:
                    try:
                        doc = plan(
                            cfgs,
                            brand_id=b,
                            platform=plat,
                            locale=loc,
                            format_key=fmt,
                            persona=args.persona,
                            intent=args.intent,
                            modality=args.modality,
                            micro_dose_protocol=args.micro_dose_protocol,
                        )
                        doc["batch_key"] = f"{b}|{plat}|{loc}|{fmt}"
                        items.append(doc)
                    except ValueError as e:
                        errors.append({"key": f"{b}|{plat}|{loc}|{fmt}", "error": str(e)})

    out_path = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out_path, ["count", "config_hash"], args.force, h):
        print(f"Skip: {out_path}")
        return 0
    out = {
        "config_hash": h,
        "count": len(items),
        "intent": args.intent,
        "persona": args.persona,
        "items": items,
        "errors": errors,
    }
    write_atomically(out_path, out)
    print(f"Wrote {args.out} with {len(items)} plans ({len(errors)} errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
