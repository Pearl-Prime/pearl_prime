#!/usr/bin/env python3
"""Merge Metricool brand map keys from canonical registries (preserve blog_id/status).

Safe merge:
- Adds missing registry keys as ``status: unwired``, ``blog_id: null``
- Preserves existing blog_id / status / timezone / notes for known keys
- Never invents blog_ids
- Ensures ``waystream_sanctuary`` exists (alias of ``way_stream_sanctuary``)
- Does not delete orphan keys unless ``--prune-orphans`` (default: leave + warn)

Usage:
    python3 scripts/integrations/metricool/sync_brands_from_registry.py --dry-run
    python3 scripts/integrations/metricool/sync_brands_from_registry.py --write
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
_PKG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(_PKG_DIR))

from brand_keys import (  # noqa: E402
    REQUIRED_CLI_KEYS,
    collect_canonical_brand_keys,
)
from client import MetricoolConfigError  # noqa: E402

BRANDS_MAP_PATH = REPO_ROOT / "config" / "integrations" / "metricool_brands.yaml"

DEFAULT_HEADER = {
    "schema_version": 1,
    "account": "waystream",
    "user_id_env": "METRICOOL_USER_ID",
    "derived_from": [
        "config/brand_registry.yaml",
        "config/catalog_planning/brand_archetype_registry.yaml",
        "config/brand_management/global_brand_registry_unified.yaml",
    ],
    "notes": (
        "One Metricool account (waystream). Only waystream_sanctuary is wired; "
        "all other brand keys are addressable but refuse posting until blog_id is set. "
        "Registry archetype way_stream_sanctuary maps to CLI key waystream_sanctuary."
    ),
}


def merge_brand_map(
    existing: dict[str, Any] | None,
    canonical_keys: set[str],
    *,
    prune_orphans: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (merged_map, stats)."""
    base = dict(DEFAULT_HEADER)
    if existing and isinstance(existing, dict):
        for key in ("schema_version", "account", "user_id_env", "derived_from", "notes"):
            if key in existing and existing[key] is not None:
                base[key] = existing[key]

    old_brands = {}
    if existing and isinstance(existing.get("brands"), dict):
        old_brands = dict(existing["brands"])

    added: list[str] = []
    preserved: list[str] = []
    pruned: list[str] = []
    orphans: list[str] = []

    new_brands: dict[str, Any] = {}
    for key in sorted(canonical_keys):
        if key in old_brands and isinstance(old_brands[key], dict):
            new_brands[key] = dict(old_brands[key])
            # Normalize status/blog_id invariants lightly
            status = (new_brands[key].get("status") or "unwired").strip().lower()
            new_brands[key]["status"] = status if status in ("wired", "unwired") else "unwired"
            if new_brands[key]["status"] == "unwired" and "blog_id" not in new_brands[key]:
                new_brands[key]["blog_id"] = None
            preserved.append(key)
        else:
            new_brands[key] = {"blog_id": None, "status": "unwired"}
            added.append(key)

    for key in sorted(set(old_brands) - canonical_keys):
        orphans.append(key)
        if prune_orphans:
            pruned.append(key)
        else:
            # Keep orphan so operator can decide; validator will fail until pruned/synced
            row = old_brands[key]
            new_brands[key] = dict(row) if isinstance(row, dict) else {"blog_id": None, "status": "unwired"}

    for req in REQUIRED_CLI_KEYS:
        if req not in new_brands:
            # Prefer cloning way_stream_sanctuary wiring if present, else unwired stub
            donor = new_brands.get("way_stream_sanctuary")
            if isinstance(donor, dict) and donor.get("status") == "wired":
                new_brands[req] = dict(donor)
                new_brands[req].setdefault(
                    "notes",
                    "CLI alias of way_stream_sanctuary. blog_id placeholder until Q-METRIC-02.",
                )
            else:
                new_brands[req] = {
                    "blog_id": "WAYSTREAM_BLOG_ID_PENDING",
                    "status": "wired",
                    "timezone": "America/New_York",
                    "notes": "Single live Metricool account path. blog_id placeholder until Q-METRIC-02.",
                }
            if req not in added and req not in preserved:
                added.append(req)

    base["brands"] = dict(sorted(new_brands.items()))
    stats = {
        "added": sorted(added),
        "preserved": len(preserved),
        "orphans": orphans,
        "pruned": pruned,
        "brand_count": len(base["brands"]),
    }
    return base, stats


def load_existing(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is not None and not isinstance(data, dict):
        raise MetricoolConfigError(f"Invalid brand map shape: {path}")
    return data


def dump_brand_map(data: dict[str, Any]) -> str:
    """Stable YAML dump with readable nulls."""

    class _Dumper(yaml.SafeDumper):
        pass

    def _repr_none(dumper: yaml.SafeDumper, _value: None) -> Any:
        return dumper.represent_scalar("tag:yaml.org,2002:null", "null")

    _Dumper.add_representer(type(None), _repr_none)
    body = yaml.dump(
        data,
        Dumper=_Dumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=100,
    )
    header = (
        "# Metricool brand → blog_id routing SSOT (Pearl_Int).\n"
        "# Derived live from brand registries via sync_brands_from_registry.py.\n"
        "# Do not hand-invent brand keys. Do not guess blog_ids.\n"
        "# Q-METRIC-02: replace WAYSTREAM_BLOG_ID_PENDING with the real Metricool blog_id.\n"
    )
    return header + body


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Sync Metricool brand keys from registries.")
    p.add_argument("--brands-map", type=Path, default=BRANDS_MAP_PATH)
    p.add_argument("--dry-run", action="store_true", help="Print stats only (default if no --write).")
    p.add_argument("--write", action="store_true", help="Write merged map to --brands-map.")
    p.add_argument(
        "--prune-orphans",
        action="store_true",
        help="Drop map keys not present in canonical registries.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    write = bool(args.write)
    dry_run = bool(args.dry_run) or not write

    try:
        existing = load_existing(args.brands_map)
        canonical = collect_canonical_brand_keys()
        merged, stats = merge_brand_map(
            existing, canonical, prune_orphans=bool(args.prune_orphans)
        )
    except (MetricoolConfigError, FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"canonical_keys={len(canonical)}")
    print(f"brand_count={stats['brand_count']}")
    print(f"preserved={stats['preserved']}")
    print(f"added={len(stats['added'])}")
    if stats["added"]:
        print(f"  + {', '.join(stats['added'][:20])}{'...' if len(stats['added']) > 20 else ''}")
    print(f"orphans={len(stats['orphans'])}")
    if stats["orphans"]:
        print(f"  ? {', '.join(stats['orphans'])}")
    if stats["pruned"]:
        print(f"pruned={', '.join(stats['pruned'])}")

    if dry_run and not write:
        print("RESULT: dry-run (no write)")
        return 0

    args.brands_map.parent.mkdir(parents=True, exist_ok=True)
    args.brands_map.write_text(dump_brand_map(merged), encoding="utf-8")
    print(f"WROTE {args.brands_map}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
