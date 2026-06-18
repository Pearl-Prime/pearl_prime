#!/usr/bin/env python3
"""Publish REAL weekly-package deliverables to the static deploy + emit a delivery feed.

The director dashboard's downloads have been EXACT metadata only. This surfaces the
brand's ACTUAL rendered files where they exist: it scans
artifacts/weekly_packages/<canon>/<week>/<platform>/ for real content
(epub/pdf/mp3/m4b/png — not stub READMEs or .zip wrappers), maps the package brand to
its archetype base, copies the files into
brand-wizard-app/public/deliveries/<base>/<week>/<platform>/, and writes
public/brand_deliveries/<base>.json so the dashboard can offer the real downloadable
files. Today only `stillness_press` has rendered output; every other brand stays
metadata-only until its books are rendered (the production-gate frontier).

Run:  python3 scripts/onboarding/gen_brand_deliveries.py
"""
from __future__ import annotations
import json
import shutil
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WP = REPO / "artifacts" / "weekly_packages"
PUB = REPO / "brand-wizard-app" / "public"
DELIV = PUB / "deliveries"
FEED = PUB / "brand_deliveries"
REG = REPO / "config" / "brand_management" / "global_brand_registry_unified.yaml"

CONTENT_EXT = {".epub", ".pdf", ".mp3", ".m4b", ".png", ".cue", ".md"}  # real content; skip .zip + README.txt
MAX_BYTES = 25 * 1024 * 1024  # keep the static deploy lean

def archetype_bases() -> list:
    try:
        reg = yaml.safe_load(REG.read_text(encoding="utf-8")) or {}
        bs = {v.get("brand_archetype_id") for v in (reg.get("brands") or {}).values()
              if isinstance(v, dict) and v.get("brand_archetype_id")}
        return sorted((b for b in bs if b), key=len, reverse=True)  # longest-prefix first
    except Exception:
        return []

def to_base(brand_dir: str, bases: list) -> str:
    for b in bases:
        if brand_dir == b or brand_dir.startswith(b + "_"):
            return b
    return brand_dir

def main() -> None:
    if not WP.exists():
        raise SystemExit(f"no weekly_packages dir: {WP}")
    bases = archetype_bases()
    feeds: dict = {}
    published = 0
    for bdir in sorted(p.name for p in WP.iterdir() if p.is_dir()):
        base = to_base(bdir, bases)
        for week in sorted(p.name for p in (WP / bdir).iterdir() if p.is_dir()):
            plats: dict = {}
            for plat in sorted(p.name for p in (WP / bdir / week).iterdir() if p.is_dir()):
                files = []
                for f in sorted((WP / bdir / week / plat).iterdir()):
                    if (f.is_file() and f.suffix.lower() in CONTENT_EXT
                            and f.name != "README.txt" and 0 < f.stat().st_size <= MAX_BYTES):
                        dest = DELIV / base / week / plat / f.name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dest)
                        published += 1
                        files.append({"file": f.name,
                                      "url": f"deliveries/{base}/{week}/{plat}/{f.name}",
                                      "kb": round(f.stat().st_size / 1024)})
                if files:
                    plats[plat] = files
            if plats:
                feeds.setdefault(base, {"brand": base, "weeks": {}})["weeks"][week] = plats

    FEED.mkdir(parents=True, exist_ok=True)
    for base, feed in feeds.items():
        feed["latest_week"] = sorted(feed["weeks"])[-1]
        (FEED / f"{base}.json").write_text(
            json.dumps(feed, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        plats = sorted({p for w in feed["weeks"].values() for p in w})
        print(f"  {base}: weeks={list(feed['weeks'])} platforms={plats}")
    print(f"published {published} real files across {len(feeds)} brand delivery feeds -> {FEED.relative_to(REPO)}")

main()
