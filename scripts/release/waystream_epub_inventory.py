#!/usr/bin/env python3
"""Waystream EPUB inventory: manifest, disk audit, W26 dedupe after cadence reslice.

Usage:
  PYTHONPATH=. python3 scripts/release/waystream_epub_inventory.py audit
  PYTHONPATH=. python3 scripts/release/waystream_epub_inventory.py manifest
  PYTHONPATH=. python3 scripts/release/waystream_epub_inventory.py dedupe-w26 --dry-run
  PYTHONPATH=. python3 scripts/release/waystream_epub_inventory.py dedupe-w26
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND = "way_stream_sanctuary"
PKG_ROOT = REPO / "artifacts/weekly_packages" / BRAND
STATE = REPO / "artifacts/waystream/batch_epub_state.json"
PLANS = REPO / "config/source_of_truth/book_plans_en_us"
OUT_DIR = REPO / "artifacts/waystream"


def _load_plan_ids() -> set[str]:
    out: set[str] = set()
    for f in PLANS.glob(f"{BRAND}__*.yaml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        bid = d.get("book_id")
        if bid:
            out.add(str(bid))
    return out


def _scan_epubs() -> dict[str, list[dict]]:
    """book_id -> list of {week, path, size, sha256}."""
    by_id: dict[str, list[dict]] = defaultdict(list)
    if not PKG_ROOT.is_dir():
        return by_id
    for week_dir in sorted(PKG_ROOT.iterdir()):
        kdp = week_dir / "amazon_kdp"
        if not kdp.is_dir():
            continue
        for p in sorted(kdp.glob("*.epub")):
            h = hashlib.sha256()
            h.update(p.read_bytes())
            by_id[p.stem].append(
                {
                    "week": week_dir.name,
                    "path": str(p.resolve()),
                    "size": p.stat().st_size,
                    "sha256": h.hexdigest(),
                }
            )
    return by_id


def cmd_audit(_args: argparse.Namespace) -> int:
    by_id = _scan_epubs()
    plan_ids = _load_plan_ids()
    on_disk = set(by_id)
    total_files = sum(len(v) for v in by_id.values())

    batch_ok: set[str] = set()
    batch_fail: set[str] = set()
    batch_missing_paths: list[str] = []
    if STATE.is_file():
        data = json.loads(STATE.read_text(encoding="utf-8"))
        for r in data.get("results", []):
            bid = r.get("book_id", "")
            st = r.get("status", "")
            if st == "ok":
                batch_ok.add(bid)
                p = r.get("path")
                if p and not Path(p).is_file():
                    batch_missing_paths.append(bid)
            elif st not in ("skip_exists", "dry_run"):
                batch_fail.add(bid)

    multi = {b: copies for b, copies in by_id.items() if len(copies) > 1}
    w26_dupes = [
        b
        for b, copies in by_id.items()
        if len(copies) > 1 and any(c["week"] == "2026-W26" for c in copies)
    ]

    report = {
        "date": date.today().isoformat(),
        "pkg_root": str(PKG_ROOT),
        "pkg_root_exists": PKG_ROOT.is_dir(),
        "total_epub_files": total_files,
        "unique_book_ids": len(on_disk),
        "catalog_plans": len(plan_ids),
        "missing_from_catalog": sorted(plan_ids - on_disk),
        "extra_not_in_catalog": sorted(on_disk - plan_ids),
        "batch_ok": len(batch_ok),
        "batch_fail": len(batch_fail),
        "batch_ok_on_disk": len(batch_ok & on_disk),
        "batch_ok_missing_on_disk": sorted(batch_ok - on_disk),
        "batch_state_paths_missing": len(batch_missing_paths),
        "books_in_multiple_weeks": len(multi),
        "w26_duplicate_book_ids": len(w26_dupes),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"epub_audit_{date.today().isoformat()}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nwrote {out.relative_to(REPO)}")
    return 0


def cmd_manifest(_args: argparse.Namespace) -> int:
    by_id = _scan_epubs()
    rows: list[dict] = []
    for bid in sorted(by_id):
        copies = sorted(by_id[bid], key=lambda c: c["week"])
        primary = copies[0]
        rows.append(
            {
                "book_id": bid,
                "primary_week": primary["week"],
                "path": primary["path"],
                "size": primary["size"],
                "sha256": primary["sha256"],
                "copy_count": len(copies),
                "all_weeks": ",".join(c["week"] for c in copies),
            }
        )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "epub_manifest.json"
    json_path.write_text(json.dumps({"books": rows, "count": len(rows)}, indent=2), encoding="utf-8")
    tsv_path = OUT_DIR / "epub_manifest.tsv"
    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["book_id", "primary_week", "path", "size", "sha256", "copy_count", "all_weeks"],
        )
        w.writeheader()
        w.writerows(rows)
    print(f"manifest: {len(rows)} unique books -> {json_path.relative_to(REPO)}, {tsv_path.relative_to(REPO)}")
    return 0


def cmd_dedupe_w26(args: argparse.Namespace) -> int:
    by_id = _scan_epubs()
    removed: list[str] = []
    for bid, copies in by_id.items():
        if len(copies) < 2:
            continue
        weeks = {c["week"] for c in copies}
        if "2026-W26" not in weeks:
            continue
        for c in copies:
            if c["week"] != "2026-W26":
                continue
            p = Path(c["path"])
            if args.dry_run:
                print(f"would remove W26 dupe: {p}")
            else:
                p.unlink(missing_ok=True)
                print(f"removed W26 dupe: {p}")
            removed.append(str(p))
    print(f"{'would remove' if args.dry_run else 'removed'}: {len(removed)} W26 duplicate files")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("audit").set_defaults(fn=cmd_audit)
    sub.add_parser("manifest").set_defaults(fn=cmd_manifest)
    d = sub.add_parser("dedupe-w26")
    d.add_argument("--dry-run", action="store_true")
    d.set_defaults(fn=cmd_dedupe_w26)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
