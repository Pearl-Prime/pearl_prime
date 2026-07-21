#!/usr/bin/env python3
"""Metricool publish CLI — draft-default, live-gated (Q-METRIC-01).

Reuses ``build_metricool_payload`` for asset→payload construction. Routes brands
via ``config/integrations/metricool_brands.yaml``. Unwired / null / placeholder
blog_ids are refused for real HTTP calls. ``--dry-run`` builds and prints only.

SAFE defaults:
- Draft-only unless ``--live`` + ``--i-understand-live`` + Q-METRIC-01 approval
- Network kill-switch: HTTP refused unless ``--dry-run`` OR ``--network`` OR
  ``METRICOOL_ALLOW_NETWORK=1``
- Media: require ≥1 media URL unless ``--allow-text-only`` (API may 500 on empty)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
_PKG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(_PKG_DIR))

from phoenix_v4.social.deterministic_social import build_metricool_payload  # noqa: E402
from client import (  # noqa: E402
    DEFAULT_BASE_URL,
    MetricoolConfigError,
    load_credentials,
    schedule_post,
)

BRANDS_MAP_PATH = REPO_ROOT / "config" / "integrations" / "metricool_brands.yaml"
PLACEHOLDER_MARKERS = ("PENDING", "TODO", "REPLACE", "CHANGEME", "YOUR_")
NETWORK_ALLOW_VALUES = frozenset({"1", "true", "yes", "on"})

# Map phoenix platform_specs surface platforms → Metricool provider network names.
NETWORK_ALIASES = {
    "tiktok_reels_shorts": "tiktok",
    "instagram_reels": "instagram",
    "youtube_shorts": "youtube",
    "x": "twitter",
    "twitter_x": "twitter",
}

# Q-METRIC-01: live auto-publish requires operator ratification of go-live.
# Until OPD row records approval, --live always errors (even with --i-understand-live).
LIVE_PUBLISH_OPERATOR_APPROVED = False


def normalize_network(name: str) -> str:
    key = (name or "").strip().lower()
    return NETWORK_ALIASES.get(key, key)


def load_brand_map(path: Path = BRANDS_MAP_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise MetricoolConfigError(f"Brand map missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "brands" not in data:
        raise MetricoolConfigError(f"Invalid brand map shape: {path}")
    return data


def resolve_brand(brand_key: str, brand_map: dict[str, Any]) -> dict[str, Any]:
    brands = brand_map.get("brands") or {}
    if brand_key not in brands:
        raise MetricoolConfigError(
            f"Unknown brand key {brand_key!r}. Not in {BRANDS_MAP_PATH.name}."
        )
    row = brands[brand_key] or {}
    status = (row.get("status") or "unwired").strip().lower()
    blog_id = row.get("blog_id")
    blog_id_str = "" if blog_id is None else str(blog_id).strip()
    return {
        "brand_key": brand_key,
        "status": status,
        "blog_id": blog_id_str,
        "timezone": row.get("timezone") or "America/New_York",
        "user_id_env": brand_map.get("user_id_env") or "METRICOOL_USER_ID",
    }


def is_placeholder_blog_id(blog_id: str) -> bool:
    if not blog_id:
        return True
    upper = blog_id.upper()
    return any(marker in upper for marker in PLACEHOLDER_MARKERS)


def network_calls_allowed(*, dry_run: bool, network_flag: bool) -> bool:
    """Fail-closed: real HTTP only when explicitly enabled."""
    if dry_run:
        return False
    if network_flag:
        return True
    env = (os.environ.get("METRICOOL_ALLOW_NETWORK") or "").strip().lower()
    return env in NETWORK_ALLOW_VALUES


def assert_media_ready(
    api_payload: dict[str, Any],
    *,
    allow_text_only: bool,
) -> None:
    """Refuse empty media unless operator documents text-only intent.

    Metricool API reference: empty media array may cause HTTP 500.
    """
    media = api_payload.get("media")
    if not isinstance(media, list):
        raise MetricoolConfigError("api_payload.media must be a list")
    usable = [m for m in media if m is not None and str(m).strip()]
    if usable:
        return
    if allow_text_only:
        return
    raise MetricoolConfigError(
        "media requires ≥1 URL before schedule_post (Metricool may 500 on empty). "
        "Pass --allow-text-only only for documented text-only posts."
    )


def assert_brand_postable(resolved: dict[str, Any], *, allow_placeholder_for_dry_run: bool) -> None:
    if resolved["status"] != "wired":
        raise MetricoolConfigError(
            f"Brand {resolved['brand_key']!r} is status={resolved['status']!r} "
            "(unwired). Refusing to post — connect a Metricool blog_id first."
        )
    if not resolved["blog_id"]:
        raise MetricoolConfigError(
            f"Brand {resolved['brand_key']!r} has null/empty blog_id. Refusing to post."
        )
    if is_placeholder_blog_id(resolved["blog_id"]) and not allow_placeholder_for_dry_run:
        raise MetricoolConfigError(
            f"Brand {resolved['brand_key']!r} blog_id is still a placeholder "
            f"({resolved['blog_id']!r}). Blocked on Q-METRIC-02 — supply the real "
            "Metricool blog_id before non-dry-run posting."
        )


def load_asset(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise MetricoolConfigError(f"Asset must be a JSON/YAML object: {path}")
    return data


def to_metricool_api_payload(
    builder_payload: dict[str, Any],
    *,
    draft: bool,
    live: bool,
    when: str | None,
    timezone: str,
) -> dict[str, Any]:
    """Adapt ``build_metricool_payload`` dry-run shape → Metricool scheduler API shape."""
    providers_raw = builder_payload.get("providers") or []
    providers: list[dict[str, str]] = []
    for item in providers_raw:
        if isinstance(item, str):
            providers.append({"network": normalize_network(item)})
        elif isinstance(item, dict) and item.get("network"):
            providers.append({"network": normalize_network(str(item["network"]))})
        else:
            raise MetricoolConfigError(f"Invalid provider entry: {item!r}")

    pub = builder_payload.get("publicationDate")
    tz = builder_payload.get("timezone") or timezone
    if when:
        date_time = when
    elif isinstance(pub, dict):
        date_time = str(pub.get("dateTime") or "")
        tz = str(pub.get("timezone") or tz)
    else:
        date_time = str(pub or "")

    if not date_time:
        raise MetricoolConfigError("publicationDate / --when missing")

    # Strip timezone offset suffix from ISO if present; Metricool wants local dateTime + tz name
    api_payload: dict[str, Any] = {
        "text": builder_payload.get("text") or "",
        "media": list(builder_payload.get("media") or []),
        "mediaAltText": list(builder_payload.get("mediaAltText") or []),
        "publicationDate": {"dateTime": _strip_tz_suffix(date_time), "timezone": tz},
        "providers": providers,
        "firstCommentText": builder_payload.get("firstCommentText") or "",
        "shortener": False,
        "draft": bool(draft) and not live,
        "autoPublish": bool(live) and not draft,
    }
    if builder_payload.get("videoCoverMilliseconds") is not None:
        api_payload["videoCoverMilliseconds"] = builder_payload["videoCoverMilliseconds"]

    platform_data = builder_payload.get("platformData") or {}
    if isinstance(platform_data, dict):
        for key, value in platform_data.items():
            if key.endswith("Data") and isinstance(value, dict):
                # Pass through platform-specific blocks; strip dry-run-only flags
                cleaned = {
                    k: v
                    for k, v in value.items()
                    if k
                    not in {
                        "uploadMode",
                        "autoPublishAllowed",
                        "livePublishingAuthorized",
                        "surface",
                        "mediaKind",
                    }
                }
                if cleaned:
                    api_payload[key] = cleaned

    return api_payload


def _strip_tz_suffix(value: str) -> str:
    """Normalize ``2026-07-22T09:00:00-04:00`` → ``2026-07-22T09:00:00`` for Metricool."""
    s = value.strip()
    if len(s) >= 6 and (s[-6] in "+-" and s[-3] == ":"):
        return s[:-6]
    if s.endswith("Z"):
        return s[:-1]
    return s


def extract_post_id(response: dict[str, Any]) -> str | None:
    if response.get("postId") is not None:
        return str(response["postId"])
    data = response.get("data")
    if isinstance(data, dict):
        if data.get("id") is not None:
            return str(data["id"])
        if data.get("postId") is not None:
            return str(data["postId"])
    if response.get("id") is not None:
        return str(response["id"])
    return None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Schedule a post via Metricool (draft default).")
    p.add_argument("--brand", required=True, help="Brand key from metricool_brands.yaml")
    p.add_argument("--asset", required=True, type=Path, help="JSON/YAML asset for build_metricool_payload")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--draft",
        action="store_true",
        default=True,
        help="Draft in Metricool queue (default). Forces draft:true autoPublish:false.",
    )
    mode.add_argument(
        "--live",
        action="store_true",
        help="Live autoPublish (gated: needs --i-understand-live + Q-METRIC-01 approval).",
    )
    p.add_argument("--when", default=None, help="ISO8601 publication dateTime override")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Build + validate payload only; no HTTP.",
    )
    p.add_argument(
        "--network",
        action="store_true",
        help="Allow real HTTP (also accepted via METRICOOL_ALLOW_NETWORK=1). Off by default.",
    )
    p.add_argument(
        "--allow-text-only",
        action="store_true",
        help="Allow empty media (documented text-only). Default requires ≥1 media URL.",
    )
    p.add_argument(
        "--i-understand-live",
        action="store_true",
        help="Acknowledge live auto-publish risk (still requires Q-METRIC-01 approval).",
    )
    p.add_argument(
        "--brands-map",
        type=Path,
        default=BRANDS_MAP_PATH,
        help="Override path to metricool_brands.yaml",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    live = bool(args.live)
    draft = not live  # --draft is default; --live flips mode

    if live:
        if not args.i_understand_live:
            print(
                "ERROR: --live requires --i-understand-live. "
                "Default posture is draft-only (Q-METRIC-01).",
                file=sys.stderr,
            )
            return 2
        if not LIVE_PUBLISH_OPERATOR_APPROVED:
            print(
                "ERROR: --live blocked — Q-METRIC-01 not ratified. "
                "Operator must approve go-live before autoPublish=true. "
                "Use --draft (default) until then.",
                file=sys.stderr,
            )
            return 2

    try:
        brand_map = load_brand_map(args.brands_map)
        resolved = resolve_brand(args.brand, brand_map)
        assert_brand_postable(resolved, allow_placeholder_for_dry_run=bool(args.dry_run))

        asset = load_asset(args.asset)
        builder_payload = build_metricool_payload(asset, publication_date=args.when)
        builder_payload["draft"] = draft
        builder_payload["autoPublish"] = live and not draft
        builder_payload["dryRun"] = bool(args.dry_run)
        if resolved.get("timezone"):
            builder_payload["timezone"] = resolved["timezone"]

        api_payload = to_metricool_api_payload(
            builder_payload,
            draft=draft,
            live=live,
            when=args.when,
            timezone=resolved["timezone"],
        )
        assert_media_ready(api_payload, allow_text_only=bool(args.allow_text_only))

        if args.dry_run:
            out = {
                "dry_run": True,
                "brand": resolved["brand_key"],
                "blog_id": resolved["blog_id"],
                "status": resolved["status"],
                "mode": "live" if live else "draft",
                "builder_payload": builder_payload,
                "api_payload": api_payload,
            }
            print(json.dumps(out, indent=2, ensure_ascii=False))
            return 0

        if not network_calls_allowed(dry_run=False, network_flag=bool(args.network)):
            print(
                "ERROR: Network kill-switch is OFF. Refusing HTTP. "
                "Pass --network or set METRICOOL_ALLOW_NETWORK=1 "
                "(or use --dry-run). Default stays safe for CI/local accidents.",
                file=sys.stderr,
            )
            return 2

        creds = load_credentials()
        if not creds["api_key"] or not creds["user_id"]:
            print(
                "ERROR: METRICOOL_API_KEY and METRICOOL_USER_ID must be set "
                '(load via: eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)").',
                file=sys.stderr,
            )
            return 2

        response = schedule_post(
            post_payload=api_payload,
            user_id=creds["user_id"],
            blog_id=resolved["blog_id"],
            api_key=creds["api_key"],
            base_url=creds.get("base_url") or DEFAULT_BASE_URL,
        )
        post_id = extract_post_id(response)
        print(json.dumps({"postId": post_id, "response": response}, indent=2, ensure_ascii=False))
        if post_id:
            print(f"postId={post_id}")
        return 0
    except MetricoolConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
