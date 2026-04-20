#!/usr/bin/env python3
"""Build a self-contained HTML dashboard from manga_series_index.json (brand + locale slice)."""

from __future__ import annotations

import argparse
import html as _html
import json
import re
from pathlib import Path
from typing import Any

TEMPLATE_PATH = Path(__file__).resolve().parent / "dashboard_template.html"

# Operator alias: first US-English global manga brand in brand_registry / manga plan.
BRAND_ALIASES: dict[str, str] = {
    "brand1": "stillness_press",
}


def _norm_locale(loc: str | None) -> str:
    if not loc:
        return ""
    return str(loc).split("_")[0].split("-")[0].lower()


def _resolve_brand(brand_arg: str) -> str:
    b = brand_arg.strip().lower()
    return BRAND_ALIASES.get(b, brand_arg.strip())


def _filter_series(
    rows: list[dict[str, Any]],
    *,
    brand_id: str | None,
    locale: str,
) -> list[dict[str, Any]]:
    want_loc = _norm_locale(locale)
    out: list[dict[str, Any]] = []
    for row in rows:
        if brand_id is not None:
            want_brand = _resolve_brand(brand_id)
            if str(row.get("brand_id") or "") != want_brand:
                continue
        row_loc = _norm_locale(row.get("locale"))
        if want_loc and row_loc != want_loc:
            continue
        out.append(row)
    return out


def _safe_embed_json(data: object) -> str:
    raw = json.dumps(data, ensure_ascii=False, indent=2)
    # Case-insensitive replacement for all </script> variants (HTML tags are case-insensitive).
    return re.sub(r"(?i)</script", r"<\\/script", raw)


def build_html(
    *,
    series_slice: list[dict[str, Any]],
    page_title: str,
) -> str:
    tpl = TEMPLATE_PATH.read_text(encoding="utf-8")
    embedded = _safe_embed_json(series_slice)
    html = tpl.replace("__EMBEDDED_JSON__", embedded).replace("__PAGE_TITLE__", _html.escape(page_title))
    return html


def main() -> int:
    ap = argparse.ArgumentParser(description="Build catalog visibility HTML dashboard.")
    ap.add_argument("--index", type=Path, required=True)
    ap.add_argument(
        "--brand",
        type=str,
        default=None,
        help="brand_id or alias (e.g. brand1 → stillness_press). Omit to include all brands.",
    )
    ap.add_argument("--locale", type=str, default="en", help="Primary language subtag match (en matches en_US)")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument(
        "--title",
        type=str,
        default="",
        help="HTML title override (default derived from brand + locale)",
    )
    args = ap.parse_args()

    data = json.loads(args.index.read_text(encoding="utf-8"))
    rows = list(data.get("series") or [])
    filtered = _filter_series(rows, brand_id=args.brand, locale=args.locale)

    if args.brand is not None:
        resolved = _resolve_brand(args.brand)
        title = args.title.strip() or f"Manga catalog — {resolved} ({args.locale})"
        default_out = args.index.parent / f"{resolved}_{args.locale}_manga_dashboard.html"
    else:
        title = args.title.strip() or f"Manga catalog — all brands ({args.locale})"
        default_out = args.index.parent / f"{args.locale}_manga_dashboard.html"

    out_path: Path = args.out if args.out is not None else default_out
    html = build_html(series_slice=filtered, page_title=title)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
