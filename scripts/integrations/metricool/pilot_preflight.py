#!/usr/bin/env python3
"""Safe Metricool pilot readiness check — never prints secret values.

Reports credential presence, brand blog_id state, and a single primary BLOCKER.
Does not call the Metricool API (auth-proof GET requires a real blog_id + creds).

Usage:
    eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
    python3 scripts/integrations/metricool/pilot_preflight.py
    python3 scripts/integrations/metricool/pilot_preflight.py --brand waystream_sanctuary --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
_PKG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(_PKG_DIR))

from client import DEFAULT_BASE_URL, load_credentials  # noqa: E402
import post as metricool_post  # noqa: E402

DEFAULT_BRAND = "waystream_sanctuary"


def assess_readiness(brand_key: str, brands_map_path: Path) -> dict[str, Any]:
    creds = load_credentials()
    api_key_set = bool(creds.get("api_key"))
    user_id_set = bool(creds.get("user_id"))
    user_id_value = creds.get("user_id") or ""
    base_url = creds.get("base_url") or DEFAULT_BASE_URL

    brand_map = metricool_post.load_brand_map(brands_map_path)
    resolved = metricool_post.resolve_brand(brand_key, brand_map)
    blog_id = resolved["blog_id"]
    blog_placeholder = metricool_post.is_placeholder_blog_id(blog_id)
    blog_ready = bool(blog_id) and not blog_placeholder and resolved["status"] == "wired"

    checks = {
        "METRICOOL_API_KEY": "set" if api_key_set else "MISSING",
        "METRICOOL_USER_ID": user_id_value if user_id_set else "MISSING",
        "METRICOOL_BASE_URL": base_url,
        "brand": brand_key,
        "brand_status": resolved["status"],
        "blog_id": blog_id or "null",
        "blog_id_ready": blog_ready,
        "live_publish_approved": bool(metricool_post.LIVE_PUBLISH_OPERATOR_APPROVED),
    }

    blockers: list[dict[str, str]] = []
    if not api_key_set or not user_id_set:
        blockers.append(
            {
                "id": "Q-METRIC-CREDS",
                "detail": (
                    "METRICOOL_API_KEY and/or METRICOOL_USER_ID missing from env. "
                    "Store in Keychain service phoenix-omega then: "
                    'eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"'
                ),
            }
        )
    if not blog_ready:
        blockers.append(
            {
                "id": "Q-METRIC-02",
                "detail": (
                    f"Brand {brand_key!r} blog_id is not a real wired value "
                    f"(current={blog_id or 'null'!r}; status={resolved['status']!r}). "
                    "Replace WAYSTREAM_BLOG_ID_PENDING in "
                    "config/integrations/metricool_brands.yaml — do not guess."
                ),
            }
        )

    primary = blockers[0] if blockers else None
    ready_for_draft_pilot = not blockers
    return {
        "ready_for_draft_pilot": ready_for_draft_pilot,
        "checks": checks,
        "blockers": blockers,
        "primary_blocker": primary,
        "next_actions_when_ready": [
            "GET scheduler/posts (auth proof) via list_scheduler_posts",
            (
                f"python3 scripts/integrations/metricool/post.py "
                f"--brand {brand_key} --asset tests/fixtures/metricool/sample_asset.json --draft"
            ),
            "Poll GET scheduler/posts for postId",
            "Do NOT pass --live until Q-METRIC-01 operator approval",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Metricool pilot readiness (no secrets printed).")
    p.add_argument("--brand", default=DEFAULT_BRAND)
    p.add_argument(
        "--brands-map",
        type=Path,
        default=metricool_post.BRANDS_MAP_PATH,
    )
    p.add_argument("--json", action="store_true", help="Emit JSON only.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = assess_readiness(args.brand, args.brands_map)
    except metricool_post.MetricoolConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        checks = report["checks"]
        print("Metricool pilot preflight")
        print(f"  API_KEY     {checks['METRICOOL_API_KEY']}")
        print(f"  USER_ID     {checks['METRICOOL_USER_ID']}")
        print(f"  BASE        {checks['METRICOOL_BASE_URL']}")
        print(f"  brand       {checks['brand']} status={checks['brand_status']}")
        print(f"  blog_id     {checks['blog_id']} ready={checks['blog_id_ready']}")
        print(f"  live_gate   approved={checks['live_publish_approved']} (Q-METRIC-01)")
        if report["ready_for_draft_pilot"]:
            print("RESULT: READY for draft pilot (not --live)")
        else:
            primary = report["primary_blocker"] or {}
            print(f"RESULT: BLOCKED")
            print(f"PRIMARY_BLOCKER={primary.get('id')}")
            print(f"EVIDENCE={primary.get('detail')}")
            if len(report["blockers"]) > 1:
                print(f"ADDITIONAL_BLOCKERS={len(report['blockers']) - 1}")
                for b in report["blockers"][1:]:
                    print(f"  - {b['id']}: {b['detail']}")

    return 0 if report["ready_for_draft_pilot"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
