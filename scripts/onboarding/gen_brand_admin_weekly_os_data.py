#!/usr/bin/env python3
"""
Generate brand-wizard-app/public/brand_admin_weekly_os_data.json from SSOT config.

Source: config/brand_management/brand_admin_weekly_os_platforms.yaml
Consumer: brand_admin_weekly_os.html (Setup / Upload / Weekly phases + quick links)

Usage:
    python3 scripts/onboarding/gen_brand_admin_weekly_os_data.py [--check]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required: pip install pyyaml\n")
    sys.exit(2)

REPO = Path(__file__).resolve().parents[2]
CFG = REPO / "config" / "brand_management" / "brand_admin_weekly_os_platforms.yaml"
OUT = REPO / "brand-wizard-app" / "public" / "brand_admin_weekly_os_data.json"


def _load() -> dict:
    if not CFG.is_file():
        raise SystemExit(f"missing config: {CFG}")
    return yaml.safe_load(CFG.read_text(encoding="utf-8")) or {}


def build() -> dict:
    raw = _load()
    profiles = raw.get("market_profiles") or {}
    lane_index: dict[str, str] = {}
    for market_id, prof in profiles.items():
        for suffix in prof.get("lane_suffixes") or []:
            lane_index[suffix] = market_id
    return {
        "schema_version": raw.get("schema_version", "1.0"),
        "generated_from": str(CFG.relative_to(REPO)),
        "default_market": "en_us",
        "lane_to_market": lane_index,
        "markets": profiles,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    data = build()
    rendered = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if current != rendered:
            sys.stderr.write(f"STALE: {OUT} differs from generated. Re-run without --check.\n")
            return 1
        print(f"OK: {OUT} is up to date.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUT} — {len(data['markets'])} market profiles, {len(data['lane_to_market'])} lane suffixes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
