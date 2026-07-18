#!/usr/bin/env python3
"""Guard: public Weekly OS HTML must equal repo-root source after Pages path transform."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROOT_HTML = ROOT / "brand_admin_weekly_os.html"
PUBLIC_HTML = ROOT / "brand-wizard-app/public/brand_admin_weekly_os.html"

REQUIRED_MARKERS = (
    "OS_DATA",
    "applyMarketProfile",
    "packetStatus",
    "setupPlanned",
    "loadBridges",
)


def transform_root_to_public(content: str) -> str:
    return (
        content.replace("brand-wizard-app/public/assets/", "assets/")
        .replace("JSON_BASE='brand-wizard-app/public/'", "JSON_BASE=''")
        .replace(
            "brand-wizard-app/public/brand_handoff_dashboard.html",
            "brand_handoff_dashboard.html",
        )
    )


def main() -> int:
    errors: list[str] = []
    if not ROOT_HTML.is_file():
        errors.append(f"missing canonical source: {ROOT_HTML.relative_to(ROOT)}")
    if not PUBLIC_HTML.is_file():
        errors.append(f"missing Pages artifact: {PUBLIC_HTML.relative_to(ROOT)}")
    if errors:
        for err in errors:
            print(f"check_brand_admin_weekly_os_public_sync.py: {err}", file=sys.stderr)
        return 1

    root = ROOT_HTML.read_text(encoding="utf-8")
    public = PUBLIC_HTML.read_text(encoding="utf-8")
    expected = transform_root_to_public(root)
    if public != expected:
        errors.append(
            "brand-wizard-app/public/brand_admin_weekly_os.html is out of sync with "
            "repo-root brand_admin_weekly_os.html — run: "
            "bash scripts/onboarding/sync_onboarding_config_to_public.sh"
        )
    for marker in REQUIRED_MARKERS:
        if marker not in public:
            errors.append(f"public weekly OS missing required marker {marker!r}")
    if errors:
        for err in errors:
            print(f"check_brand_admin_weekly_os_public_sync.py: {err}", file=sys.stderr)
        return 1

    print(
        "check_brand_admin_weekly_os_public_sync.py: OK —",
        PUBLIC_HTML.relative_to(ROOT),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
