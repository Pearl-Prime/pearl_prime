#!/usr/bin/env python3
"""Validate ``config/integrations/metricool_brands.yaml`` (offline, fail-closed).

Rules:
- Exactly one account (``account`` must be a non-empty string; brands share it)
- Every brand key must be in the canonical registry union (or known alias)
- No orphan keys (map keys not in registry union)
- ``waystream_sanctuary`` must be present
- Wired brands: non-null blog_id; unwired brands: null blog_id
- Placeholder blog_ids (e.g. WAYSTREAM_BLOG_ID_PENDING) are allowed on wired rows
  but flagged as pending (exit 0 for structure OK; use --strict-blog-ids to fail)

Usage:
    python3 scripts/integrations/metricool/validate_config.py
    python3 scripts/integrations/metricool/validate_config.py --json
"""

from __future__ import annotations

import argparse
import json
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
import post as metricool_post  # noqa: E402

BRANDS_MAP_PATH = REPO_ROOT / "config" / "integrations" / "metricool_brands.yaml"


def validate_brand_map(
    data: dict[str, Any],
    *,
    canonical_keys: set[str] | None = None,
    strict_blog_ids: bool = False,
) -> dict[str, Any]:
    """Validate brand map structure. Returns a report dict; raises on hard errors."""
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        raise MetricoolConfigError("Brand map root must be a mapping")

    account = data.get("account")
    if not account or not isinstance(account, str) or not account.strip():
        errors.append("account must be a non-empty string (exactly one Metricool account)")

    brands = data.get("brands")
    if not isinstance(brands, dict) or not brands:
        errors.append("brands must be a non-empty mapping")
        brands = {}

    canon = canonical_keys if canonical_keys is not None else collect_canonical_brand_keys()

    map_keys = set(brands.keys())
    orphans = sorted(map_keys - canon)
    missing = sorted(canon - map_keys)
    if orphans:
        errors.append(f"orphan brand keys not in registries: {orphans}")
    if missing:
        errors.append(f"missing registry brand keys: {missing}")

    for req in sorted(REQUIRED_CLI_KEYS):
        if req not in brands:
            errors.append(f"required CLI brand key missing: {req}")

    wired = 0
    unwired = 0
    pending_placeholders: list[str] = []

    for key, row in sorted(brands.items()):
        if not isinstance(row, dict):
            errors.append(f"{key}: row must be a mapping")
            continue
        status = (row.get("status") or "").strip().lower()
        blog_id = row.get("blog_id")
        if status == "wired":
            wired += 1
            if blog_id is None or str(blog_id).strip() == "":
                errors.append(f"{key}: wired brand requires non-null blog_id")
            elif metricool_post.is_placeholder_blog_id(str(blog_id)):
                pending_placeholders.append(key)
                if strict_blog_ids:
                    errors.append(
                        f"{key}: wired blog_id is still a placeholder ({blog_id!r})"
                    )
                else:
                    warnings.append(
                        f"{key}: blog_id placeholder pending Q-METRIC-02 ({blog_id!r})"
                    )
        elif status == "unwired":
            unwired += 1
            if blog_id is not None:
                errors.append(f"{key}: unwired brand must have blog_id: null (got {blog_id!r})")
        else:
            errors.append(f"{key}: status must be 'wired' or 'unwired' (got {status!r})")

    # Exactly one logical account — surface as error if brands claim divergent accounts
    # (schema has a single top-level account field; reject multi-account keys if present)
    if "accounts" in data:
        errors.append("multi-account maps unsupported; use single top-level account")

    ok = not errors
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "account": account,
        "brand_count": len(brands),
        "wired_count": wired,
        "unwired_count": unwired,
        "pending_placeholders": pending_placeholders,
        "orphan_count": len(orphans),
        "missing_count": len(missing),
        "canonical_key_count": len(canon),
    }


def load_and_validate(
    path: Path = BRANDS_MAP_PATH,
    *,
    strict_blog_ids: bool = False,
) -> dict[str, Any]:
    if not path.is_file():
        raise MetricoolConfigError(f"Brand map missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    report = validate_brand_map(data, strict_blog_ids=strict_blog_ids)
    report["path"] = str(path)
    return report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Validate Metricool brand map (offline).")
    p.add_argument("--brands-map", type=Path, default=BRANDS_MAP_PATH)
    p.add_argument(
        "--strict-blog-ids",
        action="store_true",
        help="Fail if any wired brand still has a placeholder blog_id.",
    )
    p.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = load_and_validate(args.brands_map, strict_blog_ids=args.strict_blog_ids)
    except (MetricoolConfigError, FileNotFoundError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Metricool brand map: {report['path']}")
        print(f"  account     {report['account']}")
        print(f"  brands      {report['brand_count']} (wired={report['wired_count']} unwired={report['unwired_count']})")
        print(f"  canonical   {report['canonical_key_count']}")
        if report["pending_placeholders"]:
            print(f"  pending     {', '.join(report['pending_placeholders'])}")
        for w in report["warnings"]:
            print(f"  WARN: {w}")
        if report["ok"]:
            print("RESULT: OK")
        else:
            print("RESULT: FAIL")
            for e in report["errors"]:
                print(f"  ERROR: {e}")

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
