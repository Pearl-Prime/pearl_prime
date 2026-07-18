#!/usr/bin/env python3
"""Generate per-brand funnel landing pages from Stillness Press templates."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from phoenix_v4.marketing.book_url_index import load_index, resolve_book_url  # noqa: E402
from phoenix_v4.marketing.brand_profile import get_brand_profile, list_brands  # noqa: E402

TEMPLATE_ROOT = REPO_ROOT / "brand-wizard-app/public/free"
OUT_ROOT = REPO_ROOT / "brand-wizard-app/public/free"
GHL_CAPTURE = REPO_ROOT / "config/freebies/ghl_funnel_capture.yaml"
FUNNEL_MAP = REPO_ROOT / "config/funnel/freebie_to_book_map.yaml"


def _topic_for_slug(slug: str, funnel_map: dict) -> str | None:
    for topic_id, cfg in (funnel_map.get("topics") or {}).items():
        freebie = cfg.get("freebie") or {}
        if freebie.get("slug") == slug:
            return topic_id
    return None


def _shop_cta_url(
    brand_id: str,
    topic_id: str,
    persona_id: str,
    teacher_id: str | None,
    locale: str,
    index: dict,
) -> str | None:
    url = resolve_book_url(
        topic_id,
        persona_id,
        locale=locale,
        brand_id=brand_id,
        index=index,
    )
    if url:
        return url
    if teacher_id:
        inner = f"{topic_id}_{persona_id}_{teacher_id}"
        url_locale = locale.replace("_", "-")
        return f"https://pearlprime.shop/{url_locale}/book/{brand_id}/{inner}"
    return None


def _patch_html(
    html: str,
    *,
    brand_id: str,
    display_name: str,
    persona_id: str,
    teacher_id: str | None,
    topic_id: str,
    slug: str,
    cta_url: str | None,
) -> str:
    out = html
    out = re.sub(
        r"https://pearlprime\.shop/en-US/book/stillness_press/[a-z0-9_]+",
        cta_url or out,
        out,
        count=0,
    )
    if teacher_id:
        out = out.replace("_ahjan", f"_{teacher_id}")
        out = out.replace("/stillness_press/", f"/{brand_id}/")
    elif brand_id != "stillness_press":
        out = out.replace("/stillness_press/", f"/{brand_id}/")
    out = out.replace("Phoenix Omega", display_name)
    out = out.replace("| Phoenix Omega", f"| {display_name}")
    if "data-brand-id=" not in out:
        meta_brand = (
            f'data-brand-id="{brand_id}" data-topic="{topic_id}" '
            f'data-funnel-slug="{slug}"'
        )
        out = re.sub(
            r"<body(\s[^>]*)?>",
            lambda m: f"<body {meta_brand}{m.group(1) or ''}>",
            out,
            count=1,
        )
    return out


def sync_brand(
    brand_id: str,
    *,
    locale: str = "en_US",
    dry_run: bool = False,
) -> int:
    profile = get_brand_profile(brand_id)
    prefix = profile.get("funnel_path_prefix")
    if not prefix:
        print(f"SKIP {brand_id}: no funnel_path_prefix (uses canonical /free/{{slug}}/)")
        return 0

    funnel_map = yaml.safe_load(FUNNEL_MAP.read_text(encoding="utf-8"))
    capture = yaml.safe_load(GHL_CAPTURE.read_text(encoding="utf-8"))
    pages = capture.get("funnel_pages") or []
    index = load_index()
    persona_id = str(profile.get("default_persona") or "corporate_managers")
    teacher_id = profile.get("teacher_id")
    display_name = str(profile.get("display_name") or brand_id)
    written = 0

    for page in pages:
        rel = Path(str(page.get("path") or ""))
        src = REPO_ROOT / rel
        if not src.exists():
            print(f"WARN missing template {src}", file=sys.stderr)
            continue
        slug = str(page.get("funnel_slug") or src.parent.name)
        topic_id = str(page.get("topic") or _topic_for_slug(slug, funnel_map) or "")
        cta_url = _shop_cta_url(
            brand_id,
            topic_id,
            persona_id,
            str(teacher_id) if teacher_id else None,
            locale,
            index,
        )
        html = _patch_html(
            src.read_text(encoding="utf-8"),
            brand_id=brand_id,
            display_name=display_name,
            persona_id=persona_id,
            teacher_id=str(teacher_id) if teacher_id else None,
            topic_id=topic_id,
            slug=slug,
            cta_url=cta_url,
        )
        dest = OUT_ROOT / brand_id / slug / "index.html"
        if dry_run:
            print(f"would write {dest}")
            written += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        written += 1

    print(f"OK {brand_id}: {written} page(s)")
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand-id", action="append", dest="brand_ids")
    ap.add_argument("--rollout-phase", default="pilot")
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    brand_ids = args.brand_ids or list_brands(
        ghl_enabled_only=True,
        rollout_phase=args.rollout_phase,
    )
    total = 0
    for brand_id in brand_ids:
        total += sync_brand(brand_id, locale=args.locale, dry_run=args.dry_run)
    print(f"Total pages: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
