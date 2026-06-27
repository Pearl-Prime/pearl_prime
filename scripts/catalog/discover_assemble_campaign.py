#!/usr/bin/env python3
"""Discover brands with buildable-but-not-yet-assembled en_US book plans.

Emits JSON matrix for catalog-assemble-campaign.yml:
  {"include": [{"brand": "...", "pending": N, "buildable": M, "on_r2": K}, ...]}

Buildable = plan has matching master_arc and _needs_authoring is not true.
Assembled-on-R2 = object exists at brand/{brand}/catalog/en_US/{book_id}.epub

  PYTHONPATH=. python3 scripts/catalog/discover_assemble_campaign.py
  PYTHONPATH=. python3 scripts/catalog/discover_assemble_campaign.py --brands way_stream_sanctuary
  PYTHONPATH=. python3 scripts/catalog/discover_assemble_campaign.py --json-only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
PLANS = REPO / "config/source_of_truth/book_plans_en_us"
ARCS = REPO / "config/source_of_truth/master_arcs"
REG = REPO / "config/brand_management/global_brand_registry_unified.yaml"
R2_PREFIX_TMPL = "brand/{brand}/catalog/en_US/{book_id}.epub"


def _load_yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _arc_for_plan(plan: dict) -> Path | None:
    sp_path = REPO / (plan.get("series_plan") or "")
    if sp_path.is_file():
        sp = _load_yaml(sp_path)
        bid = plan.get("book_id", "")
        for inst in (sp.get("arc") or {}).values():
            if inst.get("book_id") == bid and inst.get("master_arc"):
                arc = REPO / inst["master_arc"]
                return arc if arc.is_file() else None
    parts = plan.get("book_id", "").split("__")
    if len(parts) < 4:
        return None
    persona = parts[2] if len(parts) > 2 else ""
    topic = parts[3] if len(parts) > 3 else plan.get("topic", "")
    engine = plan.get("engine") or (parts[4].removesuffix("__1hr") if len(parts) > 4 else "")
    fmt = plan.get("structural_format_id") or "F006"
    arc = ARCS / f"{persona}__{topic}__{engine}__{fmt}.yaml"
    return arc if arc.is_file() else None


def _r2_keys_for_brand(brand: str) -> set[str]:
    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key_id = (os.environ.get("R2_ACCESS_KEY_ID") or os.environ.get("CF_R2_ACCESS_KEY") or "").strip()
    secret = (os.environ.get("R2_SECRET_ACCESS_KEY") or os.environ.get("CF_R2_SECRET_KEY") or "").strip()
    if not all([account, key_id, secret]):
        return set()
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        return set()
    endpoint = (os.environ.get("R2_ENDPOINT") or "").strip() or f"https://{account}.r2.cloudflarestorage.com"
    bucket = (os.environ.get("R2_BUCKET") or os.environ.get("CF_R2_BUCKET") or "phoenix-omega-artifacts").strip()
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    prefix = f"brand/{brand}/catalog/en_US/"
    keys: set[str] = set()
    token = None
    while True:
        kw = {"Bucket": bucket, "Prefix": prefix}
        if token:
            kw["ContinuationToken"] = token
        resp = client.list_objects_v2(**kw)
        for obj in resp.get("Contents") or []:
            keys.add(obj["Key"])
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
    return keys


def _buildable_plans(brand_filter: set[str] | None) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for f in sorted(PLANS.glob("*.yaml")):
        plan = _load_yaml(f)
        bid = plan.get("book_id") or f.stem
        brand = bid.split("__")[0]
        if brand_filter and brand not in brand_filter:
            continue
        if plan.get("_needs_authoring") is True:
            continue
        if not _arc_for_plan(plan):
            continue
        out.setdefault(brand, []).append(bid)
    return out


def _default_brands() -> list[str]:
    """All en_US archetypes with at least one buildable plan."""
    buildable = _buildable_plans(None)
    return sorted(buildable.keys())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brands", default="", help="Space-separated brand archetype ids (default: all buildable)")
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--json-only", action="store_true")
    args = ap.parse_args()

    brand_filter = set(args.brands.split()) if args.brands.strip() else None
    buildable = _buildable_plans(brand_filter)
    include = []
    for brand in sorted(buildable.keys()):
        bids = buildable[brand]
        r2_keys = _r2_keys_for_brand(brand)
        on_r2 = sum(1 for bid in bids if R2_PREFIX_TMPL.format(brand=brand, book_id=bid) in r2_keys)
        pending = len(bids) - on_r2
        if pending <= 0:
            continue
        include.append(
            {
                "brand": brand,
                "locale": args.locale,
                "buildable": len(bids),
                "on_r2": on_r2,
                "pending": pending,
            }
        )

    payload = {"include": include}
    if args.json_only:
        print(json.dumps(payload))
    else:
        print(f"brands with pending assembly: {len(include)}")
        for row in include:
            print(
                f"  {row['brand']}: buildable={row['buildable']} on_r2={row['on_r2']} pending={row['pending']}"
            )
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
